"""
Run a batch of questions from a CSV file in parallel against the chatbot.
Each question gets its own browser context. Results are saved as individual
JSON files inside a shared batch subfolder in results/, plus a summary CSV.

Usage:
    .venv\Scripts\python.exe playwright_test/batch_query.py

Configuration:
    - Edit CONCURRENCY to control how many tabs run simultaneously.
      Start with 3 and increase carefully — the chatbot server is the bottleneck.
    - Edit CSV_FILE to point to a different question list.
"""

import asyncio
import csv
import json
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import Browser, async_playwright

from query import parse_response

CHATBOT_URL = "https://stage.nexusai.coke.com/weekly-ou360"
AUTH_STATE_FILE = Path(__file__).parent / "credentials" / "auth_state.json"
RESULTS_DIR = Path(__file__).parent / "results"
CSV_FILE = Path(__file__).parent / "questions_ontology.csv"

INPUT_SELECTOR = "textarea[placeholder='Ask me anything...']"
AGENT_BTN_SELECTOR = "button:has-text('Agent Interaction')"
RESPONSE_TIMEOUT_MS = 600_000  # 10 minutes

CONCURRENCY = 5  # max simultaneous browser contexts — increase carefully

CSV_COLUMNS = [
    "index", "question",
    "total_runtime_seconds", "chatbot_wait_seconds",
    "intent_clarifier",
    "ontology_dax_query", "ontology_dax_executor_result", "ontology_result_summarizer",
    "main_dax_query", "main_dax_executor_result", "main_result_summarizer",
    "summarizer",
    "error",
]


def read_questions(csv_path: Path) -> list[str]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row["question"].strip() for row in reader if row["question"].strip()]


def elapsed(batch_start: float) -> str:
    return f"{round(time.time() - batch_start, 1)}s"


async def run_question(
    browser: Browser,
    question: str,
    index: int,
    semaphore: asyncio.Semaphore,
    batch_dir: Path,
    batch_start: float,
) -> dict:
    label = f"[Q{index}]"

    async with semaphore:
        start_time = time.time()
        context = await browser.new_context(storage_state=str(AUTH_STATE_FILE))
        page = await context.new_page()

        try:
            print(f"{label} [{elapsed(batch_start)}] Navigating to chatbot...")
            await page.goto(CHATBOT_URL, wait_until="domcontentloaded", timeout=60_000)
            await page.wait_for_load_state("networkidle", timeout=60_000)

            if "microsoftonline" in page.url or "login" in page.url.lower():
                raise RuntimeError("Session expired — re-run auth.py to refresh credentials.")

            # Wait until the textarea is interactive (React may still be mounting)
            chat_input = page.locator(INPUT_SELECTOR)
            await chat_input.wait_for(state="visible", timeout=30_000)

            # Try up to 3 times to confirm the message was actually submitted.
            # After a successful send the textarea is cleared by the app.
            for attempt in range(1, 4):
                await chat_input.click()
                await chat_input.fill(question)
                await page.wait_for_timeout(500)  # let the app register the value
                await chat_input.press("Enter")

                # Give the app up to 5 s to clear the input (confirms submission)
                try:
                    await page.wait_for_function(
                        f"document.querySelector({INPUT_SELECTOR!r})?.value === ''",
                        timeout=5_000,
                    )
                    break  # input cleared — message sent successfully
                except Exception:
                    if attempt == 3:
                        raise RuntimeError("Message failed to send after 3 attempts — textarea never cleared")
                    print(f"{label} [{elapsed(batch_start)}] Send attempt {attempt} failed, retrying...")

            send_time = time.time()
            print(f"{label} [{elapsed(batch_start)}] Sent: \"{question[:80]}{'...' if len(question) > 80 else ''}\"")

            agent_btn = page.locator(AGENT_BTN_SELECTOR).last
            await agent_btn.wait_for(state="visible", timeout=RESPONSE_TIMEOUT_MS)
            response_time = time.time()
            chatbot_wait = round(response_time - send_time, 2)
            print(f"{label} [{elapsed(batch_start)}] Response ready ({chatbot_wait}s wait)")

            await agent_btn.click()
            await page.wait_for_load_state("networkidle", timeout=15_000)
            await page.wait_for_timeout(1_500)

            response_text = await page.locator(".agentinteraction").last.inner_text()
            response_text = response_text.strip()

            total_runtime = round(time.time() - start_time, 2)
            parsed = parse_response(response_text)

            output = {
                "question": question,
                "timing": {
                    "total_runtime_seconds": total_runtime,
                    "chatbot_wait_seconds": chatbot_wait,
                },
                "response": parsed,
            }
            row = {
                "index": index,
                "question": question,
                "total_runtime_seconds": total_runtime,
                "chatbot_wait_seconds": chatbot_wait,
                "intent_clarifier": parsed.get("intent_clarifier"),
                "ontology_dax_query": parsed.get("ontology_dax_query"),
                "ontology_dax_executor_result": parsed.get("ontology_dax_executor_result"),
                "ontology_result_summarizer": parsed.get("ontology_result_summarizer"),
                "main_dax_query": parsed.get("main_dax_query"),
                "main_dax_executor_result": parsed.get("main_dax_executor_result"),
                "main_result_summarizer": parsed.get("main_result_summarizer"),
                "summarizer": parsed.get("summarizer"),
                "error": None,
            }

        except Exception as exc:
            total_runtime = round(time.time() - start_time, 2)
            print(f"{label} [{elapsed(batch_start)}] ERROR: {exc}")
            output = {
                "question": question,
                "timing": {"total_runtime_seconds": total_runtime, "chatbot_wait_seconds": None},
                "error": str(exc),
            }
            row = {
                "index": index,
                "question": question,
                "total_runtime_seconds": total_runtime,
                "chatbot_wait_seconds": None,
                "intent_clarifier": None,
                "ontology_dax_query": None,
                "ontology_dax_executor_result": None,
                "ontology_result_summarizer": None,
                "main_dax_query": None,
                "main_dax_executor_result": None,
                "main_result_summarizer": None,
                "summarizer": None,
                "error": str(exc),
            }

        finally:
            await context.close()

        output_file = batch_dir / f"response_q{index}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"{label} [{elapsed(batch_start)}] Saved to {output_file.relative_to(Path(__file__).parent)}")

        return row


def write_summary_csv(batch_dir: Path, rows: list[dict]) -> None:
    rows_sorted = sorted(rows, key=lambda r: r["index"])
    summary_file = batch_dir / "summary.csv"
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows_sorted)
    print(f"Summary CSV → {summary_file.relative_to(Path(__file__).parent)}")


async def main() -> None:
    if not AUTH_STATE_FILE.exists():
        print("ERROR: No saved session found. Run auth.py first.")
        return

    questions = read_questions(CSV_FILE)
    if not questions:
        print(f"ERROR: No questions found in {CSV_FILE}")
        return

    batch_start = time.time()
    batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = RESULTS_DIR / f"batch_{batch_timestamp}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    print(f"Batch: {len(questions)} question(s) | concurrency: {CONCURRENCY}")
    print(f"Results → {batch_dir.relative_to(Path(__file__).parent)}\n")

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        rows = await asyncio.gather(
            *[
                run_question(browser, q, i + 1, semaphore, batch_dir, batch_start)
                for i, q in enumerate(questions)
            ]
        )

        await browser.close()

    write_summary_csv(batch_dir, list(rows))
    print(f"\nBatch complete in {elapsed(batch_start)}. {len(questions)} question(s) processed.")


if __name__ == "__main__":
    asyncio.run(main())
