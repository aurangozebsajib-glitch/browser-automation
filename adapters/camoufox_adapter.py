
import os, json, time, pathlib
from playwright.sync_api import sync_playwright

class CamoufoxAdapter:
    def __init__(self, camoufox_cfg: dict, provider="generic"):
        self.cfg = camoufox_cfg
        self.provider = provider
        self.provider_cfg = self.load_provider(provider)

    def load_provider(self, name):
        p = pathlib.Path(__file__).parent / "sites" / f"{name}.json"
        if p.exists():
            return json.loads(p.read_text())
        # fallback generic
        return {
            "url": "https://chat.openai.com/",
            "input_selector": "textarea, [contenteditable=true]",
            "submit_selector": "button[data-testid='send-button'], button[type=submit]",
            "result_selector": "[data-message-author-role='assistant'], .markdown",
            "wait_ms": 90000
        }

    def test_connectivity(self):
        try:
            with sync_playwright() as pw:
                # If connect_url provided, connect, else launch camoufox if executable exists
                if self.cfg.get("connect_url"):
                    browser = pw.chromium.connect_over_cdp(self.cfg["connect_url"])
                else:
                    exe = self.cfg.get("executable_path")
                    if exe and pathlib.Path(exe).exists():
                        browser = pw.chromium.launch(executable_path=exe, headless=self.cfg.get("headless", False))
                    else:
                        browser = pw.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto(self.provider_cfg.get("url","https://example.com"), timeout=30000)
                title = page.title()
                browser.close()
                return {"ok": True, "title": title, "provider": self.provider}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def submit_prompt(self, prompt_text: str) -> str:
        # Real implementation with configurable selectors
        with sync_playwright() as pw:
            if self.cfg.get("connect_url"):
                browser = pw.chromium.connect_over_cdp(self.cfg["connect_url"])
            else:
                exe = self.cfg.get("executable_path") or None
                launch_kwargs = {"headless": self.cfg.get("headless", False)}
                if exe and pathlib.Path(exe).exists():
                    launch_kwargs["executable_path"]=exe
                browser = pw.chromium.launch(**launch_kwargs)

            context = browser.new_context()
            page = context.new_page()
            # load provider url
            url = self.provider_cfg.get("url")
            page.goto(url, timeout=60000)
            time.sleep(2)

            # Try to find input
            input_sel = self.provider_cfg.get("input_selector")
            page.wait_for_selector(input_sel, timeout=self.cfg.get("timeout_ms",120000))
            # Fill prompt
            try:
                page.fill(input_sel, prompt_text)
            except:
                # contenteditable fallback
                el = page.locator(input_sel).first
                el.click()
                page.keyboard.type(prompt_text)

            # Submit
            submit_sel = self.provider_cfg.get("submit_selector")
            try:
                page.click(submit_sel, timeout=5000)
            except:
                page.keyboard.press("Enter")

            # Wait for result
            result_sel = self.provider_cfg.get("result_selector")
            page.wait_for_selector(result_sel, timeout=self.cfg.get("timeout_ms",120000))
            # Wait a bit for streaming to finish
            time.sleep(5)
            # Extract last assistant message
            texts = page.locator(result_sel).all_inner_texts()
            raw = "\n".join(texts[-3:]) if texts else page.content()

            # optional screenshot for debug
            try:
                pathlib.Path("logs").mkdir(exist_ok=True)
                page.screenshot(path=f"logs/last_run_{int(time.time())}.png")
            except:
                pass

            browser.close()
            return raw
