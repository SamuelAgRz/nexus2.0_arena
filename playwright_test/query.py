"""
Send a question to the chatbot and save the full response as a JSON file.
Requires credentials/auth_state.json — run auth.py first if it doesn't exist.

Usage:
    .venv\Scripts\python.exe playwright_test/query.py
"""

import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

CHATBOT_URL = "https://stage.nexusai.coke.com/weekly-ou360"
AUTH_STATE_FILE = Path(__file__).parent / "credentials" / "auth_state.json"
RESULTS_DIR = Path(__file__).parent / "results"

INPUT_SELECTOR = "textarea[placeholder='Ask me anything...']"
AGENT_BTN_SELECTOR = "button:has-text('Agent Interaction')"
RESPONSE_TIMEOUT_MS = 600_000  # 10 minutes

QUESTION = "Give me the sales (volume) data of last year 2025 for Colombia for all categories, groupped by channel"


def _split_sections(text: str) -> tuple[str, str]:
    """Split response into (ontology_section, main_section).

    The ontology loop starts with SelectorGroupChatManager selecting LATAM_NSR_Ontology.
    The main loop starts with SelectorGroupChatManager selecting NSR_LATAM_Cube_UAT.
    We split at the moment NSR_LATAM_Cube_UAT is selected.
    """
    pattern = (
        r'Source: SelectorGroupChatManager.*?Message Type: SelectSpeakerEvent'
        r'.*?Content:\n\n\[\s*"NSR_LATAM_Cube_UAT"\s*\]\s*\nCopy'
    )
    m = re.search(pattern, text, re.DOTALL)
    if m:
        return text[:m.start()], text[m.start():]
    return text, ""


def _last_source_content(section: str, source_name: str) -> str | None:
    """Extract content from the last occurrence of a source in a section."""
    pattern = rf"Source: {re.escape(source_name)}.*?Content:\n\n(.*?)\nCopy"
    matches = re.findall(pattern, section, re.DOTALL)
    return matches[-1].strip() if matches else None


def _last_dax_executor_result(section: str) -> str | None:
    """Extract content from the last DaxExecutor ToolCallExecutionEvent in a section."""
    pattern = r"Source: DaxExecutor.*?Message Type: ([^\n]+).*?Content:\n\n(.*?)\nCopy"
    result = None
    for m in re.finditer(pattern, section, re.DOTALL):
        if m.group(1).strip() == "ToolCallExecutionEvent":
            result = m.group(2).strip()
    return result


def parse_response(text: str) -> dict:
    ontology_sec, main_sec = _split_sections(text)
    return {
        "complete_output": text,
        "intent_clarifier": _last_source_content(text, "IntentClarifier"),
        # Ontology loop — last result within the ontology section
        "ontology_dax_query":           _last_source_content(ontology_sec, "DaxQuery_Developer"),
        "ontology_dax_executor_result": _last_dax_executor_result(ontology_sec),
        "ontology_result_summarizer":   _last_source_content(ontology_sec, "DaxResultSummarizer"),
        # Main loop — last result within the main section
        "main_dax_query":               _last_source_content(main_sec, "DaxQuery_Developer"),
        "main_dax_executor_result":     _last_dax_executor_result(main_sec),
        "main_result_summarizer":       _last_source_content(main_sec, "DaxResultSummarizer"),
        # Final summary
        "summarizer": _last_source_content(text, "SummarizerAgent"),
    }


async def main():
    start_time = time.time()

    if not AUTH_STATE_FILE.exists():
        print("ERROR: No saved session found. Run auth.py first.")
        return

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(AUTH_STATE_FILE))
        page = await context.new_page()

        print(f"Navigating to {CHATBOT_URL}...")
        await page.goto(CHATBOT_URL, wait_until="domcontentloaded", timeout=60_000)
        await page.wait_for_load_state("networkidle", timeout=60_000)

        if "microsoftonline" in page.url or "login" in page.url.lower():
            print("ERROR: Session expired. Re-run auth.py to refresh credentials.")
            await browser.close()
            return

        # Send the question — retry up to 3 times until the textarea clears (confirms submission)
        chat_input = page.locator(INPUT_SELECTOR)
        await chat_input.wait_for(state="visible", timeout=30_000)
        print(f"Question: {QUESTION}")

        for attempt in range(1, 4):
            await chat_input.click()
            await chat_input.fill(QUESTION)
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
                print(f"Send attempt {attempt} failed, retrying...")

        send_time = time.time()
        print("Message sent. Waiting for response (up to 10 minutes)...")

        # Wait for the "Agent Interaction" button — signals response is complete
        agent_btn = page.locator(AGENT_BTN_SELECTOR).last
        await agent_btn.wait_for(state="visible", timeout=RESPONSE_TIMEOUT_MS)
        response_time = time.time()
        print("Response is ready.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Click to reveal the full output
        await agent_btn.click()
        await page.wait_for_load_state("networkidle", timeout=15_000)
        await page.wait_for_timeout(1_500)

        # Extract and parse response text
        response_text = await page.locator(".agentinteraction").last.inner_text()
        response_text = response_text.strip()

        total_runtime = round(time.time() - start_time, 2)
        chatbot_wait = round(response_time - send_time, 2)

        output = {
            "question": QUESTION,
            "timing": {
                "total_runtime_seconds": total_runtime,
                "chatbot_wait_seconds": chatbot_wait,
            },
            "response": parse_response(response_text),
        }

        output_file = RESULTS_DIR / f"response_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\nSaved to {output_file}")
        print(f"Total runtime: {total_runtime}s | Chatbot wait: {chatbot_wait}s")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
