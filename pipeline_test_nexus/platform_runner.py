"""
Paso 2 del pipeline: preguntar cada question del golden set al chatbot
Nexus vía Playwright y capturar la respuesta del SummarizerAgent.

Cada pregunta se corre CONCURRENCY veces en paralelo (misma pregunta,
distintos browser contexts, sesión compartida desde credentials/auth_state.json)
para medir consistencia de respuesta entre corridas repetidas, una pregunta
a la vez (batch por pregunta). Cada corrida guarda su propio checkpoint YAML
en la carpeta del run, de modo que un crash no pierde las corridas ya
completadas.
"""

import ast
import asyncio
import re
import time
from pathlib import Path

from playwright.async_api import Browser, async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from adomd_connector import LiteralString, save_yaml
from config import (
    AGENT_BTN_SELECTOR,
    AUTH_STATE_FILE,
    CHATBOT_URL,
    CONCURRENCY,
    HEADLESS,
    INPUT_READY_SELECTOR,
    INPUT_READY_TIMEOUT_MS,
    INPUT_SELECTOR,
    PAGE_LOAD_ATTEMPTS,
    RESPONSE_TIMEOUT_MS,
    SEND_CONFIRM_TIMEOUT_MS,
    SEND_RETRY_CLICK_TIMEOUT_MS,
    SUMMARIZER_RE,
    THREAD_ID_RE,
)


CONTENT_RE = re.compile(r"Content:\n\n(.*?)\nCopy", re.DOTALL)


def parse_agent_blocks(text: str) -> list[tuple[str, str]]:
    """
    Parsea el texto crudo del Agent Interaction en bloques (source, content).
    Cada bloque tiene la forma:
        Source: <AgentName>
        ... metadatos ...
        Content:

        <contenido>
        Copy
    """
    blocks = []
    for chunk in re.split(r"(?=^Source: )", text, flags=re.MULTILINE):
        if not chunk.startswith("Source: "):
            continue
        source = chunk.split("\n", 1)[0].removeprefix("Source: ").strip()
        match = CONTENT_RE.search(chunk)
        if match:
            blocks.append((source, match.group(1).strip()))
    return blocks


def last_content(blocks: list[tuple[str, str]], predicate) -> str | None:
    """Devuelve el content del último bloque cuyo source cumple el predicado."""
    for source, content in reversed(blocks):
        if predicate(source):
            return content
    return None


def extract_answer(text: str, blocks: list[tuple[str, str]]) -> str | None:
    """
    Devuelve la última respuesta del summarizer. Primero intenta el patrón
    original (SummarizerAgent); si no hay match, cae al último bloque cuyo
    source contenga 'Summarizer' (p.ej. DaxResultSummarizer).
    """
    matches = SUMMARIZER_RE.findall(text)
    if matches:
        return matches[-1].strip()
    return last_content(blocks, lambda s: "summarizer" in s.lower())


def extract_dax_executor(blocks: list[tuple[str, str]]):
    """
    Devuelve el content del último bloque DaxExecutor. Si es una lista de
    filas en formato literal de Python, la parsea a datos estructurados;
    si no, devuelve el string crudo.
    """
    content = last_content(blocks, lambda s: s == "DaxExecutor")
    if content is None:
        return None
    try:
        return ast.literal_eval(content)
    except (ValueError, SyntaxError):
        return content


def elapsed(batch_start: float) -> str:
    return f"{round(time.time() - batch_start, 1)}s"


async def wait_for_input_ready(page, label: str, batch_start: float) -> None:
    """
    Espera a que el chat input esté visible Y habilitado (la app lo renderiza
    disabled mientras inicializa). Si no se habilita en INPUT_READY_TIMEOUT_MS,
    recarga la página y reintenta, hasta PAGE_LOAD_ATTEMPTS cargas en total.
    """
    for load_attempt in range(1, PAGE_LOAD_ATTEMPTS + 1):
        try:
            await page.locator(INPUT_READY_SELECTOR).wait_for(
                state="visible", timeout=INPUT_READY_TIMEOUT_MS
            )
            return
        except PlaywrightTimeoutError:
            if load_attempt == PAGE_LOAD_ATTEMPTS:
                raise RuntimeError(
                    f"El chat input nunca se habilitó tras {PAGE_LOAD_ATTEMPTS} cargas de página"
                )
            print(
                f"{label} [{elapsed(batch_start)}] Input deshabilitado tras "
                f"{INPUT_READY_TIMEOUT_MS // 1000}s, recargando página "
                f"(intento {load_attempt}/{PAGE_LOAD_ATTEMPTS})..."
            )
            await page.reload(wait_until="domcontentloaded", timeout=60_000)
            await page.wait_for_load_state("networkidle", timeout=60_000)


async def check_session(browser: Browser, batch_start: float) -> None:
    """Navega una vez antes del fan-out para detectar sesión expirada temprano."""
    context = await browser.new_context(storage_state=str(AUTH_STATE_FILE))
    page = await context.new_page()
    try:
        await page.goto(CHATBOT_URL, wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_load_state("networkidle", timeout=60_000)
        if "microsoftonline" in page.url or "login" in page.url.lower():
            raise RuntimeError("Sesión expirada — corre auth.py de nuevo para refrescar credenciales.")
        await wait_for_input_ready(page, "[session]", batch_start)
    finally:
        await context.close()


async def ask_question(
    browser: Browser,
    item: dict,
    run_index: int,
    total_runs: int,
    semaphore: asyncio.Semaphore,
    run_dir: Path,
    batch_start: float,
) -> dict:
    """
    Hace una pregunta al chatbot y devuelve el dict platform_answer.

    run_index/total_runs identifican la corrida repetida (1..N) de ESTA MISMA
    pregunta dentro de su batch, no la posición de la pregunta en el golden set.
    """
    question = item["question"]
    label = f"[Q{item['id']} run {run_index}/{total_runs}]"

    async with semaphore:
        start_time = time.time()
        context = await browser.new_context(storage_state=str(AUTH_STATE_FILE))
        page = await context.new_page()

        try:
            print(f"{label} [{elapsed(batch_start)}] Navegando al chatbot...")
            await page.goto(CHATBOT_URL, wait_until="domcontentloaded", timeout=60_000)
            await page.wait_for_load_state("networkidle", timeout=60_000)

            if "microsoftonline" in page.url or "login" in page.url.lower():
                raise RuntimeError("Sesión expirada — corre auth.py de nuevo para refrescar credenciales.")

            await wait_for_input_ready(page, label, batch_start)
            chat_input = page.locator(INPUT_SELECTOR)

            for attempt in range(1, 4):
                try:
                    await chat_input.click(timeout=SEND_RETRY_CLICK_TIMEOUT_MS)
                except PlaywrightTimeoutError:
                    # El input dejó de ser clickeable entre nuestro intento
                    # anterior (que parecía fallido) y este reintento — lo más
                    # probable es que ese intento sí se haya enviado y la app
                    # ya esté ocupada procesándolo.
                    print(f"{label} [{elapsed(batch_start)}] Input no disponible para reintentar, "
                          f"asumiendo que el envío anterior sí funcionó.")
                    break

                await chat_input.fill(question)
                await page.wait_for_timeout(500)
                await chat_input.press("Enter")

                try:
                    await page.wait_for_function(
                        f"document.querySelector({INPUT_SELECTOR!r})?.value === ''",
                        timeout=SEND_CONFIRM_TIMEOUT_MS,
                    )
                    break
                except PlaywrightTimeoutError:
                    # El textarea puede tardar más que SEND_CONFIRM_TIMEOUT_MS
                    # en vaciarse bajo carga concurrente aunque el envío haya
                    # funcionado — antes de asumir que falló, chequeamos el
                    # valor actual.
                    if await chat_input.input_value() == "":
                        break
                    if attempt == 3:
                        raise RuntimeError("El mensaje no se envió tras 3 intentos — el textarea nunca se vació")
                    print(f"{label} [{elapsed(batch_start)}] Intento de envío {attempt} falló, reintentando...")

            send_time = time.time()
            print(f"{label} [{elapsed(batch_start)}] Enviado: \"{question[:80]}{'...' if len(question) > 80 else ''}\"")

            agent_btn = page.locator(AGENT_BTN_SELECTOR).last
            await agent_btn.wait_for(state="visible", timeout=RESPONSE_TIMEOUT_MS)
            chatbot_wait = round(time.time() - send_time, 2)
            print(f"{label} [{elapsed(batch_start)}] Respuesta lista ({chatbot_wait}s de espera)")

            await agent_btn.click()
            await page.wait_for_load_state("networkidle", timeout=15_000)
            await page.wait_for_timeout(1_500)

            response_text = await page.locator(".agentinteraction").last.inner_text()
            response_text = response_text.strip()

            thread_id = None
            try:
                thread_text = await page.get_by_text(THREAD_ID_RE).last.inner_text()
                match = THREAD_ID_RE.search(thread_text)
                thread_id = match.group(1) if match else None
            except Exception:
                pass

            blocks = parse_agent_blocks(response_text)
            dax_developer = last_content(blocks, lambda s: s == "DaxQuery_Developer")

            platform_answer = {
                "status": "ok",
                "answer": extract_answer(response_text, blocks),
                "dax_developer": LiteralString(dax_developer) if dax_developer else None,
                "dax_executor": extract_dax_executor(blocks),
                "total_runtime_seconds": round(time.time() - start_time, 2),
                "thread_id": thread_id,
            }

        except Exception as exc:
            print(f"{label} [{elapsed(batch_start)}] ERROR: {exc}")
            platform_answer = {
                "status": "error",
                "answer": None,
                "dax_developer": None,
                "dax_executor": None,
                "error": str(exc),
                "total_runtime_seconds": round(time.time() - start_time, 2),
                "thread_id": None,
            }

        finally:
            await context.close()

        # Checkpoint individual: un crash del batch no pierde esta corrida
        checkpoint_file = run_dir / f"response_q{item['id']}_run{run_index}.yaml"
        save_yaml(checkpoint_file, {
            "id": item["id"],
            "question": question,
            "run_index": run_index,
            "platform_answer": platform_answer,
        })
        print(f"{label} [{elapsed(batch_start)}] Checkpoint → {checkpoint_file.name}")

        return platform_answer


async def run_platform(items: list[dict], run_dir: Path) -> list[dict]:
    """
    Para cada pregunta del golden set, lanza CONCURRENCY corridas concurrentes
    de LA MISMA pregunta (batch por pregunta, una pregunta a la vez) y le
    agrega la llave 'platform_answers': una lista de CONCURRENCY dicts
    {status, answer, total_runtime_seconds, thread_id}, para medir
    consistencia de respuesta entre corridas repetidas.
    """
    batch_start = time.time()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    repeats = CONCURRENCY

    print(f"Plataforma: {len(items)} pregunta(s) | {repeats} corrida(s) repetida(s) por pregunta\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)

        print("Verificando sesión...")
        await check_session(browser, batch_start)
        print("Sesión válida.\n")

        for q_index, item in enumerate(items, start=1):
            print(f"=== Pregunta {q_index}/{len(items)}: id {item['id']} — {repeats} corridas concurrentes ===")

            answers = await asyncio.gather(
                *[
                    ask_question(browser, item, run_index, repeats, semaphore, run_dir, batch_start)
                    for run_index in range(1, repeats + 1)
                ]
            )

            item["platform_answers"] = answers
            ok = sum(1 for a in answers if a["status"] == "ok")
            print(f"=== Pregunta {q_index}/{len(items)} lista: {ok}/{repeats} corridas OK ===\n")

        await browser.close()

    total_runs = len(items) * repeats
    total_ok = sum(1 for item in items for a in item["platform_answers"] if a["status"] == "ok")
    print(f"\nPlataforma lista en {elapsed(batch_start)}: {total_ok}/{total_runs} corridas OK "
          f"({len(items)} preguntas x {repeats} corridas).\n")
    return items
