# credit: https://github.com/PYUDNG/markdown2image
import os
import os.path as osp
from asyncio import Future
from glob import glob
from typing import TypedDict

from playwright._impl._api_structures import PdfMargins
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

try:
    import pymupdf
except ImportError:
    pymupdf = None

from ..args import PDFArgs
from ..dataio import get_identifier, item2md
from ..defaults import MAX_ASYNC_PAGES
from .md2html import md2html
from .pdf2image import get_image_path, pdf2image


# Init browser and context
class T_status_page(TypedDict):
    id: int
    busy: bool
    page: Page


class IdlePagesManager:
    def __init__(self, max_pages: int) -> None:
        self.pages: list[T_status_page] = []
        self.pages_count: int = 0
        self.idle_futures: list[Future[T_status_page]] = []
        self.max_pages: int = max_pages

    async def new_page(self) -> T_status_page:
        page = await _context.new_page()
        status_page: T_status_page = {
            "id": len(self.pages),
            "busy": False,
            "page": page,
        }
        self.pages.append(status_page)
        return status_page

    async def get_idle_page(self) -> T_status_page:
        # Use existing idle page
        for status_page in self.pages:
            if not status_page["busy"]:
                return status_page

        # No idle page available for now
        if self.pages_count < self.max_pages:
            # create a new page
            self.pages_count += 1
            status_page = await self.new_page()
            return status_page
        else:
            # reaching max_page limit
            status_page = await self.wait_for_page_idle()
            return status_page

    async def wait_for_page_idle(self) -> T_status_page:
        # create a Future and wait for self.set_page_status finishing it
        future: Future[T_status_page] = Future()
        self.idle_futures.append(future)
        status_page = await future
        return status_page

    def set_page_status(self, page_id: int, busy: bool):
        for status_page in self.pages:
            if page_id == status_page["id"]:
                status_page["busy"] = busy
                if not busy and self.idle_futures:
                    future = self.idle_futures.pop(0)
                    future.set_result(status_page)
                return
        raise Exception(f"No page found with provided page_id {repr(page_id)}")


_playwright: Playwright
_browser: Browser
_context: BrowserContext
_manager: IdlePagesManager
# False: not initialized; True: initialized; Future[bool]: initializing
initialized: bool | Future[bool] = False


async def _init():
    global _playwright, _browser, _context, _manager, initialized
    initialized = Future()
    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch()
    _context = await _browser.new_context(viewport={"width": 512, "height": 512})
    # config vars
    # modify max_pages before first convertion/screenshot, modification later then will not take effect
    _manager = IdlePagesManager(MAX_ASYNC_PAGES)
    initialized.set_result(True)
    initialized = True


async def html2image(
    html: str,
    root: str,
    *,
    pdf_args: PDFArgs,
):
    """
    Render HTML content to image(s) using Playwright.

    Args:
        html (str): The HTML content to render.
        root (str): The root directory to save output images.
        pdf_args (PDFArgs): PDF and rendering options.

    Returns:
        tuple: Tuple of DeOCR-ed images, an iterable of image paths or objects.

    Examples::

        >>> image_paths = await html2image("<h1>Hello World</h1>", root="./output")
    """
    global initialized
    if isinstance(initialized, Future):
        await initialized
    elif not initialized:
        await _init()

    # Get an idle page to render
    status_page: T_status_page = await _manager.get_idle_page()
    _manager.set_page_status(status_page["id"], True)
    page = status_page["page"]

    # render & screenshot
    await page.reload(wait_until="commit")
    width, height = pdf_args.pagesize

    assert isinstance(width, int)
    height = None if pdf_args.autoAdjustHeight else height
    await page.set_viewport_size({"width": width, "height": height or width})
    await page.set_content(html=html, wait_until="load")

    # inject css if any
    if pdf_args.css is not None:
        await page.add_style_tag(content=pdf_args.css)
    if pdf_args.css_path is not None:
        await page.add_style_tag(path=pdf_args.css_path)

    # prepare output dir
    subfolder_name = get_identifier(html, pdf_args)
    subfolder = f"{root}/{subfolder_name}"
    if osp.exists(subfolder) and not pdf_args.overwrite:
        cached_files = glob(f"{subfolder}/*.{pdf_args.extension}")
        if len(cached_files) > 0:
            return tuple(sorted(cached_files))
    if not osp.exists(subfolder):
        os.makedirs(subfolder)

    # take screenshot
    if pymupdf is None or pdf_args.forceOnePage:
        path = get_image_path(subfolder, 0, 1, pdf_args.extension)
        await page.screenshot(
            path=path, full_page=pdf_args.autoAdjustHeight or height is None
        )
        # release page to idle pages
        _manager.set_page_status(status_page["id"], False)
        return (path,)

    # export as pdf and then convert to images
    pdf_bytes = await page.pdf(
        path=f"{subfolder}/.pdf" if pdf_args.savePDF else None,
        scale=1,
        header_template=None,
        footer_template=None,
        format=None,
        print_background=True,
        width=f"{width}px",
        height=f"{height}px" if height is not None else None,
        margin=PdfMargins(
            top=f"{pdf_args.marginTop}px",
            bottom=f"{pdf_args.marginBottom}px",
            left=f"{pdf_args.marginLeft}px",
            right=f"{pdf_args.marginRight}px",
        ),
    )
    image_paths = pdf2image(
        pdf_bytes=pdf_bytes,
        subfolder=subfolder,
        dpi=pdf_args.dpi,
        extension=pdf_args.extension,
        save_images=pdf_args.saveImage,
    )
    # release page to idle pages
    _manager.set_page_status(status_page["id"], False)
    return image_paths


async def markdown2image(
    md: str,
    root: str,
    *,
    pdf_args: PDFArgs,
):
    """
    Render markdown content to image(s) using Playwright.

    Args:
        md (str): The markdown content to render.
        root (str): The root directory to save output images.
        pdf_args (PDFArgs): PDF and rendering options.

    Returns:
        tuple: Tuple of DeOCR-ed images, an iterable of image paths or objects.

    Examples::

        >>> image_paths = await markdown2image("# Hello World", root="./output")
    """
    html = md2html(md)
    return await html2image(html, root, pdf_args=pdf_args)


async def transform(
    item: str | dict,
    cache_dir: str,
    pdf_args: PDFArgs,
):
    """
    Transform a single data item by converting specified text columns to images.

    Args:
        item (dict): Data item containing text fields.
        cache_dir (str): Directory to cache generated images.
        pdf_args (PDFArgs): PDF and rendering options.

    Returns:
        tuple: Tuple of DeOCR-ed images, an iterable of image paths or objects.
    """
    md = item2md(item)

    # convert md to image via async markdown2image function
    deocr_ed = await markdown2image(md, root=cache_dir, pdf_args=pdf_args)

    return deocr_ed


if __name__ == "__main__":
    import asyncio

    async def main():
        md_content = """
# Sample Document
```python
print("Hello, World!")
```
"""
        image_paths = await markdown2image(md_content, root="./output")
        print("Generated image paths:", image_paths)

    asyncio.run(main())
