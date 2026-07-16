"""
Ejecutar UNA VEZ para autenticarse con Microsoft SSO y guardar la sesión.
Después de correrlo, credentials/auth_state.json será reutilizado por el pipeline.

Uso:
    .venv\\Scripts\\python.exe pipeline_test_nexus/auth.py
"""

import asyncio

from playwright.async_api import async_playwright

from config import AUTH_STATE_FILE, CHATBOT_URL, CREDENTIALS_DIR


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
