"""
Send a question to the chatbot and save the full response to a text file.
Requires credentials/auth_state.json — run auth.py first if it doesn't exist.

Usage:
    .venv\Scripts\python.exe test_playwright/query.py
"""

import asyncio
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

CHATBOT_URL = "https://stage.nexusai.coke.com/weekly-ou360"
AUTH_STATE_FILE = Path(__file__).parent / "credentials" / "auth_state.json"
RESULTS_DIR = Path(__file__).parent / "results"

INPUT_SELECTOR = "textarea[placeholder='Ask me anything...']"
AGENT_BTN_SELECTOR = "button:has-text('Agent Interaction')"
RESPONSE_TIMEOUT_MS = 360_000  # 6 minutes

QUESTION = "Give me the sales (volume) data of last year 2025 for Colombia for all categories, groupped by channel"


async def main():
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

        await chat_input.press("Enter")
        print("Message sent. Waiting for response (this can take 1-5 minutes)...")

        # Wait for the "Agent Interaction" button — signals response is complete
        agent_btn = page.locator(AGENT_BTN_SELECTOR).last
        await agent_btn.wait_for(state="visible", timeout=RESPONSE_TIMEOUT_MS)
        print("Response is ready.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Click to reveal the full output
        await agent_btn.click()
        await page.wait_for_load_state("networkidle", timeout=15_000)
        await page.wait_for_timeout(1_500)

        # Extract response text
        response_text = await page.locator(".agentinteraction").last.inner_text()
        response_text = response_text.strip()

        # Save to file
        output_file = RESULTS_DIR / f"response_{timestamp}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Question: {QUESTION}\n\n")
            f.write(response_text)

        print("\n--- Response ---")
        print(response_text)
        print(f"\nSaved to {output_file}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
