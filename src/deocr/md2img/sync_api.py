# credit: https://github.com/PYUDNG/markdown2image
from typing import Optional

import markdown
from playwright.sync_api import Playwright, sync_playwright

# Init browser and context
_playwright: Playwright = sync_playwright().start()
_browser = _playwright.chromium.launch()
_context = _browser.new_context(viewport={"width": 1024, "height": 1024})
_page = _context.new_page()


def html2image(
    html: str,
    path: str,
    *,
    width: int = 1024,
    height: Optional[int] = None,
    css: Optional[str] = None,
    css_path: Optional[str] = None,
    allow_flexible_height: bool = False,
):
    _page.reload(wait_until="commit")
    _page.set_viewport_size({"width": width, "height": height or width})
    _page.set_content(html=html, wait_until="load")
    # Inject CSS if provided
    if css:
        _page.add_style_tag(content=css)
    if css_path:
        _page.add_style_tag(path=css_path)
    _page.screenshot(path=path, full_page=allow_flexible_height or height is None)


def markdown2image(
    md: str,
    path: str,
    width: int = 1024,
    height: Optional[int] = None,
    css: Optional[str] = None,
    css_path: Optional[str] = None,
):
    html = markdown.markdown(md)
    html2image(html, path, width=width, height=height, css=css, css_path=css_path)
