"""浏览器自动化封装（Playwright，Celery Worker 内同步使用）。

提供会话管理、导航、截图与页面快照采集。探索阶段采集页面结构，
后续执行阶段在此基础扩展表单填充、断言等能力。
"""

import logging
from typing import Any

from playwright.sync_api import Browser, Page, Playwright, sync_playwright

logger = logging.getLogger(__name__)


class BrowserSession:
    """管理一个浏览器会话。"""

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    def __enter__(self) -> "BrowserSession":
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
        return self

    def __exit__(self, *exc: Any) -> None:
        if self._browser is not None:
            self._browser.close()
        if self._pw is not None:
            self._pw.stop()

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("浏览器会话未启动")
        return self._page

    def open(self, url: str) -> None:
        """导航到指定 URL。"""
        self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)

    def screenshot(self, path: str) -> None:
        """截图保存到本地路径。"""
        self.page.screenshot(path=path, full_page=False)

    def snapshot(self) -> dict[str, Any]:
        """采集当前页面快照（标题、URL、文本、链接、可交互元素）。"""
        page = self.page
        title = page.title()
        url = page.url
        text = page.inner_text("body")[:5000]
        links = page.eval_on_selector_all(
            "a[href]",
            "els => els.slice(0, 100).map(e => ({text: e.innerText.trim(), href: e.href}))",
        )
        buttons = page.eval_on_selector_all(
            "button, input[type=submit], [role=button]",
            "els => els.slice(0, 50).map(e => e.innerText.trim() || e.getAttribute('value') || e.tagName)",
        )
        return {"title": title, "url": url, "text": text, "links": links, "buttons": buttons}
