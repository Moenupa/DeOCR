# credit: https://github.com/PYUDNG/markdown2image
from typing import Optional

import markdown
from playwright.sync_api import Playwright, sync_playwright

# Init browser and context
_playwright: Playwright = sync_playwright().start()
_browser = _playwright.chromium.launch()
_context = _browser.new_context(viewport={"width": 800, "height": 1})
_page = _context.new_page()


def html2image(
    html: str,
    path: str,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
    css: Optional[str] = None,
    css_path: Optional[str] = None,
    allow_flexible_height: bool = False,
):
    _page.reload(wait_until="commit")
    if width is not None:
        _page.set_viewport_size({"width": width, "height": height or 1})
    _page.set_content(html=html, wait_until="load")
    # Inject CSS if provided
    if css:
        _page.add_style_tag(content=css)
    if css_path:
        _page.add_style_tag(path=css_path)
    _page.screenshot(path=path, full_page=allow_flexible_height)


def markdown2image(
    md: str,
    path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    css: Optional[str] = None,
    css_path: Optional[str] = None,
):
    html = markdown.markdown(md)
    html2image(html, path, width=width, height=height, css=css, css_path=css_path)
