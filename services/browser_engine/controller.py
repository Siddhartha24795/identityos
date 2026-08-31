"""v3 — Playwright wrapper implementing the generalized
BrowserObservation/BrowserAction abstraction (PROMPT.md's BROWSER
AUTOMATION section). Field detection is DOM-based (label text + input
type), not hard-coded to any one page's markup — the same
`observe()`/`fill_text()`/`select_option()`/`check()` calls work against
any page with standard form semantics, demonstrated here against a local
synthetic form (data/applications/local_demo/) since no real target site
has been named (docs/roadmap.md v3).

v3.1: `observe()` also never surfaces a hidden/invisible field (a sighted
human wouldn't fill one either, and it may be a honeypot trap) and flags
any CAPTCHA/anti-bot widget markup or page text via `BrowserObservation.errors`
— `agent.py` halts the entire task on either signal rather than attempting
to solve it (ground rule 3: never bypass MFA/CAPTCHA/anti-bot protections).
See services/browser_engine/safety.py for the text-pattern half of this
and the two other guardrails (prompt-injection detection, zero-evidence
refusal) that live closer to field mapping and generation.

v4.3: `observe()` also flags a page that never actually loaded — an HTTP
status >= 400 (`open()` now keeps the `Response` object) or blocked-page
title phrasing (safety.py's `looks_like_blocked_page()`) — found by
testing this project's browser agent against a real, live third-party
site for the first time and getting a silent "0 fields, 0 errors" back
from a page a WAF had actually blocked with a 403. See safety.py's
module docstring, concern 4, for the full story.
"""
from __future__ import annotations

from packages.schemas.browser import BrowserObservation, DetectedField, FieldType
from services.browser_engine.safety import (
    looks_like_anti_bot_check,
    looks_like_blocked_page,
    looks_like_mfa_challenge,
)

_FIELD_TYPE_MAP = {
    "textarea": FieldType.TEXTAREA,
    "select": FieldType.SELECT,
}


class BrowserController:
    def __init__(self, headless: bool = True):
        from playwright.sync_api import sync_playwright  # local import: optional dependency

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=headless)
        self._page = self._browser.new_page()
        self._last_response = None

    def open(self, url: str) -> None:
        # Kept (not just checked-and-discarded) so observe() can tell a
        # real page load apart from a WAF/anti-bot block that served an
        # error status instead of the real content — see safety.py's
        # concern 4 for why this matters and how it was found.
        self._last_response = self._page.goto(url)

    def observe(self) -> BrowserObservation:
        page = self._page
        fields: list[DetectedField] = []
        errors: list[str] = []
        n_hidden_skipped = 0

        for el in page.locator("input, textarea, select").all():
            tag = el.evaluate("e => e.tagName.toLowerCase()")
            input_type = (el.get_attribute("type") or "text").lower() if tag == "input" else tag
            field_id = el.get_attribute("id")
            selector = f"#{field_id}" if field_id else None
            if not selector:
                continue  # only reason about addressable, labeled fields

            # Never fill what a sighted human wouldn't see. A hidden field is
            # either dead markup or a honeypot trap for scripted fillers —
            # either way, the correct behavior is to leave it alone, not to
            # try to detect *which* case it is.
            if input_type != "hidden" and not el.is_visible():
                n_hidden_skipped += 1
                continue
            if input_type == "hidden":
                n_hidden_skipped += 1
                continue

            label = self._label_for(field_id) or el.get_attribute("placeholder") or field_id

            if tag == "select":
                options = [
                    opt.strip()
                    for opt in el.locator("option").all_inner_texts()
                    if opt.strip() and opt.strip() != "-- select --"
                ]
                # Bug found via v3's own browser demo (docs/hot_take.md's v3
                # addendum): el.input_value() returns the <option value="...">
                # attribute, but field_mapper/agent fill and compare by the
                # option's visible LABEL text. Recording the selected
                # option's own inner_text keeps observe()/fill/verify
                # comparing like-for-like.
                selected_label = el.locator("option:checked").inner_text().strip()
                fields.append(
                    DetectedField(
                        selector=selector, label=label, field_type=FieldType.SELECT,
                        options=options, current_value=selected_label,
                    )
                )
            elif input_type == "checkbox":
                fields.append(
                    DetectedField(
                        selector=selector, label=label, field_type=FieldType.CHECKBOX,
                        current_value="checked" if el.is_checked() else "",
                    )
                )
            elif tag == "textarea":
                fields.append(
                    DetectedField(
                        selector=selector, label=label, field_type=FieldType.TEXTAREA,
                        current_value=el.input_value(),
                    )
                )
            else:
                fields.append(
                    DetectedField(
                        selector=selector, label=label, field_type=FieldType.TEXT,
                        current_value=el.input_value(),
                    )
                )

        submit_selector = None
        submit_loc = page.locator("button[type=button], button[type=submit], input[type=submit]")
        if submit_loc.count() > 0:
            sid = submit_loc.first.get_attribute("id")
            submit_selector = f"#{sid}" if sid else None

        if n_hidden_skipped:
            errors.append(
                f"skipped {n_hidden_skipped} hidden field(s) — not visible, "
                "never filled (potential honeypot trap)"
            )

        # Ground rule 3: never bypass MFA/CAPTCHA/anti-bot protections.
        # Detected, not solved — agent.py halts the entire task on any hit
        # here before touching a single field.
        #
        # Deliberately checks page TITLE, not the full visible_text: a real
        # full-page challenge (a Cloudflare interstitial, a dedicated OTP
        # page) is reliably named in its title. Scanning the whole page
        # body would also match ordinary field LABELS ("Are you a robot?"
        # as one field among several legitimate ones) and incorrectly halt
        # the entire task instead of just that field — that per-field case
        # is handled separately, correctly scoped, in
        # services/security/policy_engine.py and field_mapper.py.
        captcha_widget_loc = page.locator(
            "iframe[src*='captcha' i], [class*='captcha' i], [id*='captcha' i]"
        )
        visible_text = page.locator("body").inner_text()[:2000]
        if captcha_widget_loc.count() > 0:
            errors.append("anti-bot/CAPTCHA widget detected in page markup — halting, not bypassing")
        if looks_like_anti_bot_check(page.title()):
            errors.append("anti-bot/identity-verification phrasing detected in page title — halting, not bypassing")
        if looks_like_mfa_challenge(page.title()):
            errors.append("MFA/OTP challenge phrasing detected in page title — halting, not bypassing")

        # v4.3 — a page that never actually loaded (a WAF/anti-bot block,
        # a dead link) must not be reported as "0 fields found" — that
        # reads identically to "this page genuinely has no form," which
        # is false and was found to be false against a real site. Two
        # signals: the HTTP status itself, and, for a block page that
        # returns 200 with a JS challenge instead, its title phrasing.
        if self._last_response is not None and self._last_response.status >= 400:
            errors.append(
                f"page failed to load (HTTP {self._last_response.status}) — likely a "
                "WAF/anti-bot block, not an empty form; halting rather than reporting "
                "zero fields as 'no form here'"
            )
        if looks_like_blocked_page(page.title()):
            errors.append(
                "blocked-page phrasing detected in page title — halting, not treating "
                "as a real page"
            )

        return BrowserObservation(
            url=page.url,
            title=page.title(),
            visible_text=visible_text,
            fields=fields,
            submit_selector=submit_selector,
            errors=errors,
        )

    def _label_for(self, field_id: str | None) -> str | None:
        if not field_id:
            return None
        loc = self._page.locator(f"label[for='{field_id}']")
        if loc.count() > 0:
            return loc.first.inner_text().strip()
        # checkbox labels often wrap the input rather than using `for`
        wrapping = self._page.locator(f"label:has(#{field_id})")
        if wrapping.count() > 0:
            return wrapping.first.inner_text().strip()
        return None

    def fill_text(self, selector: str, value: str) -> None:
        self._page.fill(selector, value)

    def select_option(self, selector: str, value: str) -> None:
        self._page.select_option(selector, label=value)

    def check(self, selector: str) -> None:
        self._page.check(selector)

    def click(self, selector: str) -> None:
        self._page.click(selector)

    def close(self) -> None:
        self._browser.close()
        self._pw.stop()

    def __enter__(self) -> "BrowserController":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
