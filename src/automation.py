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
from typing import Dict, List

from playwright.sync_api import (
    BrowserContext,
    Page,
    sync_playwright,
)
from playwright.sync_api import (
    TimeoutError as PWTimeoutError,
)

from src.utils import read_rows

log = logging.getLogger(__name__)

URL = "https://rpachallenge.com/"

# Spreadsheet header -> ng-reflect-name (stable, resists shuffle)
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
    """Block heavy resources to speed things up (keep CSS for layout)."""
    block = {"image", "media", "font"}
    context.route(
        "**/*",
        lambda route: route.abort() if route.request.resource_type in block else route.continue_(),
    )


def _fill_round(page: Page, row: Dict[str, str], timeout_ms: int) -> None:
    """Fill one round and click Submit; caller may wait for the next round if needed."""
    # Pre-cache locators for slight speedup/clarity
    loc = {k: page.locator(f'input[ng-reflect-name="{v}"]') for k, v in FIELD_MAP.items()}
    for col, reflect in FIELD_MAP.items():
        value = (row.get(col) or "").strip()
        if value:
            loc[col].fill(value, timeout=timeout_ms)
    page.get_by_role("button", name="Submit").click()

    # wait for next round (except caller can skip on last if you prefer)
    page.wait_for_function(
        '() => (document.querySelector(\'input[ng-reflect-name="labelFirstName"]\')?.value || "") === ""',
        timeout=timeout_ms,
    )


def run_rpa_challenge(file_path: str, headless: bool = False, perf_mode: bool = False) -> Dict:
    """Run the rpachallenge.com Input Forms challenge end-to-end and return a summary."""
    rows: List[Dict[str, str]] = list(read_rows(file_path))
    if not rows:
        raise SystemExit(f"No rows found in {file_path}")

    round_timeout = 5000 if perf_mode else 10000
    
    # Make sure screenshot directory exists
    Path("screenshots").mkdir(exist_ok=True)

    elapsed=0.0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        # Smaller viewport reduces layout/paint cost, keep scale = 1 for speed
        context = browser.new_context(viewport={"width": 900, "height": 650}, device_scale_factor=1)

        if perf_mode:
            _enable_perf_routes(context) # block images/media/fonts
            # Kill animations/transitions to avoid needless frames
            context.add_init_script("""
            const s = document.createElement('style');
            s.textContent='*,*::before,*::after{animation:none!important;transition:none!important}';
            document.head.appendChild(s);
            """)
            # Slightly tighter defaults; still generous for reliability
            context.set_default_timeout(2500)
            log.warning("PERF mode: blocking images/media/fonts; tighter element waits")

        failed = False
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = None

        try:
            page = context.new_page()

            # Try normal DOMContentLoaded; if slow, retry with commit + Wait for Start
            try:
                page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            except PWTimeoutError:
                log.warning("Navigation slow; retrying with commit + Start wait")
                page.goto(URL, wait_until="commit", timeout=45000)
                page.get_by_role("button", name="Start").wait_for(timeout=30000)

            # Ensure Start is visible then begin
            page.get_by_role("button", name="Start").click()

            # Start measuring at first round; stop at final Submit
            start = time.perf_counter()
            for i, row in enumerate(rows, 1):
                _fill_round(page, row, timeout_ms=round_timeout)
                # After submit, wait until first-name clears (next round ready), except after last
                if i != len(rows):
                    page.wait_for_function(
                        '() => (document.querySelector(\'input[ng-reflect-name="labelFirstName"]\')?.value || "") === ""',
                        timeout=round_timeout,
                    )
            elapsed = time.perf_counter() - start

            # Screenshot of results
            page.screenshot(path="screenshots/result.png", full_page=True)

            # Try to read the site's banner time (nice to report)
            site_timer = ""
            try:
                txt = page.locator(".message2, .congratulations").first.text_content(timeout=2000)
                site_timer = (txt or "").strip()
            except Exception:
                pass

        except Exception:
            failed = True
            # Best-effort error screenshot for debugging
            try:
                if page:
                    page.screenshot(path="screenshots/error.png", full_page=True)
            except Exception:
                pass
            raise

        finally:
            # Save trace on failure (for CI artifacts), always clean up
            try:
                if failed:
                    context.tracing.stop(path="screenshots/trace.zip")
                else:
                    context.tracing.stop()
            except Exception:
                pass
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass

    summary = {
        "ok": True,
        "rounds": len(rows),
        "elapsed_sec": round(elapsed, 3),
        "headless": headless,
        "perf": perf_mode,
        "site_timer": site_timer,
    }

    # In perf mode, print at WARNING so it shows even when INFO is muted
    (log.warning if perf_mode else log.info)(
        'OK: rounds=%d elapsed=%.3fs headless=%s perf=%s site="%s"',
        summary["rounds"],
        summary["elapsed_sec"],
        headless,
        perf_mode,
        site_timer,
    )

    with open("screenshots/run_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary
