"""v3 — Playwright wrapper implementing the generalized
BrowserObservation/BrowserAction abstraction (PROMPT.md's BROWSER
AUTOMATION section). Field detection is DOM-based (label text + input
type), not hard-coded to any one page's markup — the same
`observe()`/`fill_text()`/`select_option()`/`check()` calls work against
any page with standard form semantics, demonstrated here against a local
synthetic form (data/applications/local_demo/) since no real target site
has been named (docs/roadmap.md v3).
"""
from __future__ import annotations

from packages.schemas.browser import BrowserObservation, DetectedField, FieldType

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

    def open(self, url: str) -> None:
        self._page.goto(url)

    def observe(self) -> BrowserObservation:
        page = self._page
        fields: list[DetectedField] = []

        for el in page.locator("input, textarea, select").all():
            tag = el.evaluate("e => e.tagName.toLowerCase()")
            input_type = (el.get_attribute("type") or "text").lower() if tag == "input" else tag
            field_id = el.get_attribute("id")
            selector = f"#{field_id}" if field_id else None
            if not selector:
                continue  # only reason about addressable, labeled fields

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

        return BrowserObservation(
            url=page.url,
            title=page.title(),
            visible_text=page.locator("body").inner_text()[:2000],
            fields=fields,
            submit_selector=submit_selector,
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
