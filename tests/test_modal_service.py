import asyncio
import time
from urllib.parse import urlparse

import modal
from playwright.sync_api import expect, sync_playwright

from test_time_to_first_frame import receive_first_frame


def frontend_url() -> str:
    url = modal.Server.from_name("kine", "Frontend").get_url()
    if url is None:
        raise AssertionError("deployed kine Frontend has no URL")
    return url


def frontend_ws_url() -> str:
    parsed = urlparse(frontend_url())
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return parsed._replace(scheme=scheme, path="/ws", query="", fragment="").geturl()


def test_modal_frontend_returns_a_page() -> None:
    url = frontend_url()
    script = "script[src*='/assets/']"
    deadline = time.monotonic() + 60
    with sync_playwright() as playwright:
        page = playwright.chromium.launch().new_page()
        while True:
            page.goto(url, timeout=60_000)
            if page.locator(script).count() > 0:
                break
            if time.monotonic() > deadline:
                expect(page.locator(script)).to_be_attached(timeout=1_000)
            time.sleep(1)


def test_modal_frontend_receives_first_frame() -> None:
    frame = asyncio.run(receive_first_frame(frontend_ws_url()))
    assert frame.width == 640
    assert frame.height == 480
