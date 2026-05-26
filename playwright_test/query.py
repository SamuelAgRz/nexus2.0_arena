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


def _extract_source_content(text: str, source_name: str) -> str | None:
    pattern = rf"Source: {re.escape(source_name)}.*?Content:\n\n(.*?)\nCopy"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else None


def _extract_dax_executor_result(text: str) -> str | None:
    pattern = r"Source: DaxExecutor.*?Message Type: ([^\n]+).*?Content:\n\n(.*?)\nCopy"
    for m in re.finditer(pattern, text, re.DOTALL):
        if m.group(1).strip() == "ToolCallExecutionEvent":
            return m.group(2).strip()
    return None


def parse_response(text: str) -> dict:
    return {
        "complete_output": text,
        "intent_clarifier": _extract_source_content(text, "IntentClarifier"),
        "dax_query": _extract_source_content(text, "DaxQuery_Developer"),
        "dax_executor_result": _extract_dax_executor_result(text),
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
        await page.goto(CHATBOT_URL)
        await page.wait_for_load_state("networkidle", timeout=30_000)

        if "microsoftonline" in page.url or "login" in page.url.lower():
            print("ERROR: Session expired. Re-run auth.py to refresh credentials.")
            await browser.close()
            return

        # Send the question
        chat_input = page.locator(INPUT_SELECTOR)
        await chat_input.click()
        await chat_input.fill(QUESTION)
        print(f"Question: {QUESTION}")

        send_time = time.time()
        await chat_input.press("Enter")
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
