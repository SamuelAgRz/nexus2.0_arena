"""
Run a batch of questions from a CSV file in parallel against the chatbot.
Captures only: original question, answer (summarizer result), total time spent,
and the chatbot threadId. Each question gets its own browser context. Results are
saved as individual JSON files inside a shared batch subfolder in results/, plus a
summary CSV.

Usage:
    .venv\Scripts\python.exe test_nexus/batch_nexus.py

Configuration:
    - Edit CONCURRENCY to control how many tabs run simultaneously.
    - Edit CSV_FILE to point to a different question list.
"""

import asyncio
import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import Browser, async_playwright

CHATBOT_URL = "https://stage.nexusai.coke.com/weekly-ou360"
AUTH_STATE_FILE = Path(__file__).parent / "credentials" / "auth_state.json"
RESULTS_DIR = Path(__file__).parent / "results"
CSV_FILE = Path(__file__).parent / "golden_set.csv"

INPUT_SELECTOR = "textarea[placeholder='Ask me anything...']"
AGENT_BTN_SELECTOR = "button:has-text('Agent Interaction')"
THREAD_ID_RE = re.compile(r"threadId:\s*([0-9a-fA-F-]+)")
SUMMARIZER_RE = re.compile(r"Source: SummarizerAgent.*?Content:\n\n(.*?)\nCopy", re.DOTALL)
RESPONSE_TIMEOUT_MS = 600_000  # 10 minutes

CONCURRENCY = 10

CSV_COLUMNS = ["index", "question", "answer", "total_runtime_seconds", "thread_id"]


def extract_answer(text: str) -> str | None:
    """Return the last SummarizerAgent answer from the raw agent output."""
    matches = SUMMARIZER_RE.findall(text)
    return matches[-1].strip() if matches else None


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
                        raise RuntimeError("Message failed to send after 3 attempts — textarea never cleared")
                    print(f"{label} [{elapsed(batch_start)}] Send attempt {attempt} failed, retrying...")

            send_time = time.time()
            print(f"{label} [{elapsed(batch_start)}] Sent: \"{question[:80]}{'...' if len(question) > 80 else ''}\"")

            agent_btn = page.locator(AGENT_BTN_SELECTOR).last
            await agent_btn.wait_for(state="visible", timeout=RESPONSE_TIMEOUT_MS)
            chatbot_wait = round(time.time() - send_time, 2)
            print(f"{label} [{elapsed(batch_start)}] Response ready ({chatbot_wait}s wait)")

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

            total_runtime = round(time.time() - start_time, 2)
            answer = extract_answer(response_text)

            output = {
                "question": question,
                "answer": answer,
                "total_runtime_seconds": total_runtime,
                "thread_id": thread_id,
            }
            row = {
                "index": index,
                "question": question,
                "answer": answer,
                "total_runtime_seconds": total_runtime,
                "thread_id": thread_id,
            }

        except Exception as exc:
            total_runtime = round(time.time() - start_time, 2)
            print(f"{label} [{elapsed(batch_start)}] ERROR: {exc}")
            output = {
                "question": question,
                "answer": None,
                "total_runtime_seconds": total_runtime,
                "thread_id": None,
            }
            row = {
                "index": index,
                "question": question,
                "answer": None,
                "total_runtime_seconds": total_runtime,
                "thread_id": None,
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
    batch_dir = RESULTS_DIR / f"batch_simple_{batch_timestamp}"
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
