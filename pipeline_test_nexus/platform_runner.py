"""
Paso 2 del pipeline: preguntar cada question del golden set al chatbot
Nexus vía Playwright y capturar la respuesta del SummarizerAgent.

Cada pregunta corre en su propio browser context (sesión compartida desde
credentials/auth_state.json) y guarda un checkpoint YAML individual en la
carpeta del run, de modo que un crash no pierde las respuestas ya completadas.
"""

import ast
import asyncio
import re
import time
from pathlib import Path

from playwright.async_api import Browser, async_playwright

from adomd_connector import LiteralString, save_yaml
from config import (
    AGENT_BTN_SELECTOR,
    AUTH_STATE_FILE,
    CHATBOT_URL,
    CONCURRENCY,
    HEADLESS,
    INPUT_SELECTOR,
    RESPONSE_TIMEOUT_MS,
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


async def check_session(browser: Browser) -> None:
    """Navega una vez antes del fan-out para detectar sesión expirada temprano."""
    context = await browser.new_context(storage_state=str(AUTH_STATE_FILE))
    page = await context.new_page()
    try:
        await page.goto(CHATBOT_URL, wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_load_state("networkidle", timeout=60_000)
        if "microsoftonline" in page.url or "login" in page.url.lower():
            raise RuntimeError("Sesión expirada — corre auth.py de nuevo para refrescar credenciales.")
    finally:
        await context.close()


async def ask_question(
    browser: Browser,
    item: dict,
    index: int,
    total: int,
    semaphore: asyncio.Semaphore,
    run_dir: Path,
    batch_start: float,
) -> dict:
    """Hace una pregunta al chatbot y devuelve el dict platform_answer."""
    question = item["question"]
    label = f"[Q{item['id']} {index}/{total}]"

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

            chat_input = page.locator(INPUT_SELECTOR)
            await chat_input.wait_for(state="visible", timeout=30_000)

            for attempt in range(1, 4):
                await chat_input.click()
                await chat_input.fill(question)
                await page.wait_for_timeout(500)
                await chat_input.press("Enter")

                try:
                    await page.wait_for_function(
                        f"document.querySelector({INPUT_SELECTOR!r})?.value === ''",
                        timeout=5_000,
                    )
                    break
                except Exception:
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

        # Checkpoint individual: un crash del batch no pierde esta respuesta
        checkpoint_file = run_dir / f"response_q{item['id']}.yaml"
        save_yaml(checkpoint_file, {
            "id": item["id"],
            "question": question,
            "platform_answer": platform_answer,
        })
        print(f"{label} [{elapsed(batch_start)}] Checkpoint → {checkpoint_file.name}")

        return platform_answer


async def run_platform(items: list[dict], run_dir: Path) -> list[dict]:
    """
    Pregunta cada item al chatbot (concurrencia CONCURRENCY) y le agrega
    la llave 'platform_answer': {status, answer, total_runtime_seconds, thread_id}.
    """
    batch_start = time.time()
    semaphore = asyncio.Semaphore(CONCURRENCY)

    print(f"Plataforma: {len(items)} pregunta(s) | concurrencia: {CONCURRENCY}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)

        print("Verificando sesión...")
        await check_session(browser)
        print("Sesión válida.\n")

        answers = await asyncio.gather(
            *[
                ask_question(browser, item, i + 1, len(items), semaphore, run_dir, batch_start)
                for i, item in enumerate(items)
            ]
        )

        await browser.close()

    for item, answer in zip(items, answers):
        item["platform_answer"] = answer

    ok = sum(1 for a in answers if a["status"] == "ok")
    print(f"\nPlataforma lista en {elapsed(batch_start)}: {ok}/{len(items)} preguntas OK.\n")
    return items
