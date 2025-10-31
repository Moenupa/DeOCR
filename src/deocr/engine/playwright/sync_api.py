# credit: https://github.com/PYUDNG/markdown2image
import os
import os.path as osp
from glob import glob

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from playwright._impl._api_structures import PdfMargins
from playwright.sync_api import Playwright, sync_playwright

try:
    import pymupdf
except ImportError:
    pymupdf = None
from ..args import PDFArgs
from ..dataio import get_identifier
from .pdf2image import get_image_path, pdf2image

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
    if pdf_args.css is not None:
        _page.add_style_tag(content=pdf_args.css)
    if pdf_args.css_path is not None:
        _page.add_style_tag(path=pdf_args.css_path)

    # prepare output dir
    subfolder_name = get_identifier(html, pdf_args)
    subfolder = f"{root}/{subfolder_name}"
    # use cache when exists, if found, skip rendering
    if osp.exists(subfolder) and not pdf_args.overwrite:
        cached_files = glob(f"{subfolder}/*.{pdf_args.extension}")
        if len(cached_files) > 0:
            return sorted(cached_files)
    if not osp.exists(subfolder):
        os.makedirs(subfolder)

    # take screenshot
    if pymupdf is None or pdf_args.forceOnePage:
        path = get_image_path(subfolder, 0, 1, pdf_args.extension)
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
    return pdf2image(
        pdf_bytes=pdf_bytes,
        subfolder=subfolder,
        dpi=pdf_args.dpi,
        extension=pdf_args.extension,
    )


def markdown2image(
    md: str,
    root: str,
    *,
    pdf_args: PDFArgs = PDFArgs(),
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
    return html2image(html, root, pdf_args=pdf_args)
