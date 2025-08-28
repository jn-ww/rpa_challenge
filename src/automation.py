"""
Playwright automation for https://rpachallenge.com/ (Input Forms).

Approach:
- Select inputs by stable Angular attribute `ng-reflect-name`, not by position.
- Field order shuffles each round; we always target by name.
- Optional --perf mode blocks heavy resources for speed and lowers timeouts.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict

from playwright.sync_api import BrowserContext, Page, sync_playwright

from src.utils import read_rows

log = logging.getLogger(__name__)

# Map canonical spreadsheet columns -> ng-reflect-name attribute values on inputs
FIELD_MAP: Dict[str, str] = {
    "First Name": "labelFirstName",
    "Last Name": "labelLastName",
    "Company Name": "labelCompanyName",
    "Role in Company": "labelRole",
    "Address": "labelAddress",
    "Email": "labelEmail",
    "Phone Number": "labelPhone",
}


def _enable_perf_routes(context: BrowserContext) -> None:
    """Block non-essential resources to speed things up."""
    # Abort images, media, fonts to reduce bandwidth/render time.
    block_types = {"image", "media", "font"}

    def _route(route):
        if route.request.resource_type in block_types:
            return route.abort()
        return route.continue_()

    context.route("**/*", _route)


def _wait_form_ready(page: Page, timeout_ms: int) -> None:
    # Wait until at least one known input is visible; form shuffles each round.
    page.wait_for_selector('input[ng-reflect-name="labelFirstName"]', timeout=timeout_ms)


def _fill_round(page: Page, row: Dict[str, str], timeout_ms: int) -> None:
    for col, reflect in FIELD_MAP.items():
        value = (row.get(col) or "").strip()
        if not value:
            continue
        locator = page.locator(f'input[ng-reflect-name="{reflect}"]')
        locator.wait_for(state="visible", timeout=timeout_ms)
        locator.fill(value)
    page.get_by_role("button", name="Submit").click()


def run_rpa_challenge(file_path: str, headless: bool = False, perf_mode: bool = False) -> None:
    """Run the rpachallenge.com input forms challenge end-to-end."""
    rows = list(read_rows(file_path))
    if not rows:
        raise SystemExit(f"No rows found in {file_path}")

    log.info("Launching browser (headless=%s, perf=%s) ...", headless, perf_mode)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        if perf_mode:
            _enable_perf_routes(context)
            context.set_default_timeout(4000)  # be a bit stricter in perf mode
        page = context.new_page()
        # Slightly lower default if perf-mode; otherwise keep Playwright default (30s)
        if perf_mode:
            page.set_default_timeout(4000)

        log.info("Navigating to rpachallenge.com ...")
        try:
            page.goto("https://rpachallenge.com/", wait_until="domcontentloaded", timeout=15000)
        except Exception:
            # One quick retry if first attempt was slow
            page.goto("https://rpachallenge.com/", wait_until="domcontentloaded", timeout=20000)

        # Start the timed challenge
        page.get_by_role("button", name="Start").click()

        round_timeout = 5000 if perf_mode else 10000

        start = time.perf_counter()
        for idx, row in enumerate(rows, start=1):
            _wait_form_ready(page, timeout_ms=round_timeout)
            _fill_round(page, row, timeout_ms=round_timeout)
            log.debug("Submitted round %d", idx)

        # Proof & result capture
        page.screenshot(path="screenshots/result.png", full_page=True)
        elapsed = time.perf_counter() - start

        # ensure folder exists before writing artifacts
        Path("screenshots").mkdir(exist_ok=True)

        # one-line summary that shows even when perf mutes INFO logs
        summary = (
            f"OK: rounds={len(rows)} elapsed={elapsed:.3f}s headless={headless} perf={perf_mode}"
        )
        (log.warning if perf_mode else log.info)(summary)

        # write a tiny run report for CI/manual verification
        with open("screenshots/run_summary.json", "w") as f:
            json.dump(
                {
                    "ok": True,
                    "rounds": len(rows),
                    "elapsed_sec": round(elapsed, 3),
                    "headless": headless,
                    "perf": perf_mode,
                },
                f,
                indent=2,
            )

        # Try to log the result text if present
        try:
            msg = page.get_by_text("Congratulations", exact=False).first
            if msg.is_visible():
                log.info("Result: %s", msg.inner_text())
        except Exception:
            pass

        log.info("Completed all rounds in %.3f s", elapsed)
        browser.close()
