# credit: https://github.com/PYUDNG/markdown2image
import os
import os.path as osp
from typing import Optional

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from playwright._impl._api_structures import PdfMargins
from playwright.sync_api import Playwright, sync_playwright

from ..dataio import get_identifier

try:
    import pymupdf
except ImportError:
    pymupdf = None

from ..args import PDFArgs

# Init browser and context
_playwright: Playwright = sync_playwright().start()
_browser = _playwright.chromium.launch()
_context = _browser.new_context(viewport={"width": 512, "height": 512})
_page = _context.new_page()


def html2image(
    html: str,
    root: str,
    *,
    pdf_args: PDFArgs = PDFArgs(),
    css: Optional[str] = None,
    css_path: Optional[str] = None,
) -> list[str]:
    """
    Render HTML content to image(s) using Playwright.

    Args:
        html (str): The HTML content to render.
        root (str): The root directory to save output images.
        pdf_args (PDFArgs, optional): PDF and rendering options. Default: PDFArgs().
        css (Optional[str], optional): CSS content to inject. Default: None.
        css_path (Optional[str], optional): Path to CSS file to inject. Default: None.

    Returns:
        list[str]: List of file paths to the generated images.

    Examples::

        >>> # instantiate the renderer and close it after use:
        >>> renderer = PlaywrightSyncRenderer()
        >>> image_paths = renderer.markdown2image("<h1>Hello World</h1>", root="./output")
    """

    _page.reload(wait_until="commit")
    width, height = pdf_args.pagesize

    assert isinstance(width, int)
    height = None if pdf_args.autoAdjustHeight else height
    _page.set_viewport_size({"width": width, "height": height or width})
    _page.set_content(html=html, wait_until="load")

    # inject css if any
    if css:
        _page.add_style_tag(content=css)
    if css_path:
        _page.add_style_tag(path=css_path)

    # prepare output dir
    subfolder_name = get_identifier(html, pdf_args)
    subfolder = f"{root}/{subfolder_name}"
    if not osp.exists(subfolder):
        os.makedirs(subfolder)

    # take screenshot
    if pymupdf is None or pdf_args.forceOnePage:
        path = f"{subfolder}/{0:010d}.png"
        _page.screenshot(
            path=path, full_page=pdf_args.autoAdjustHeight or height is None
        )
        return [path]

    # export as pdf and then convert to images
    pdf_bytes = _page.pdf(
        # path=f"{subfolder}/.pdf" if pdf_args.savePDF else None,
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
    pdf_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    for i in range(len(pdf_doc)):
        page = pdf_doc.load_page(i)
        pix = page.get_pixmap(dpi=pdf_args.dpi)
        pix.save(f"{subfolder}/{i:010d}.png")
    return [f"{subfolder}/{i:010d}.png" for i in range(len(pdf_doc))]


def markdown2image(
    md: str,
    root: str,
    *,
    pdf_args: PDFArgs = PDFArgs(),
    css: Optional[str] = None,
    css_path: Optional[str] = None,
) -> list[str]:
    """
    Render markdown content to image(s) using Playwright.

    Args:
        md (str): The markdown content to render.
        root (str): The root directory to save output images.
        pdf_args (PDFArgs, optional): PDF and rendering options. Default: PDFArgs().
        css (Optional[str], optional): CSS content to inject. Default: None.
        css_path (Optional[str], optional): Path to CSS file to inject. Default: None.

    Returns:
        list[str]: List of file paths to the generated images.

    Examples::

        >>> # instantiate the renderer and close it after use:
        >>> renderer = PlaywrightSyncRenderer()
        >>> image_paths = renderer.markdown2image("# Hello World", root="./output")
    """
    md_renderer = (
        MarkdownIt("commonmark")
        .use(front_matter_plugin)
        .use(dollarmath_plugin)
        .use(footnote_plugin)
        .enable("table")
    )
    html = md_renderer.render(md)
    return html2image(html, root, pdf_args=pdf_args, css=css, css_path=css_path)
