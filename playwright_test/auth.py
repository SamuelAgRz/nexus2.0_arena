"""
Run this ONCE to authenticate with Microsoft SSO and save the session.
After running, credentials/auth_state.json will be reused by query.py.

Usage:
    .venv\Scripts\python.exe test_playwright/auth.py
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

CHATBOT_URL = "https://stage.nexusai.coke.com/weekly-ou360"
CREDENTIALS_DIR = Path(__file__).parent / "credentials"
AUTH_STATE_FILE = CREDENTIALS_DIR / "auth_state.json"


async def main():
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"Opening {CHATBOT_URL} ...")
        await page.goto(CHATBOT_URL)

        print("\nPlease log in with your Microsoft account in the browser window.")
        input("Once you can see the chatbot (not the login page), press Enter here to save your session...")

        await page.wait_for_load_state("networkidle", timeout=30_000)
        print(f"Authenticated! Current URL: {page.url}")

        await context.storage_state(path=str(AUTH_STATE_FILE))
        print(f"Session saved to {AUTH_STATE_FILE}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
