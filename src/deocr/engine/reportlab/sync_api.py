# credit: https://github.com/thu-coai/Glyph
import io
import os
import re
from xml.sax.saxutils import escape

import pymupdf
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate

from ..args import RenderArgs
from ..dataio import get_identifier

PRESETS = getSampleStyleSheet()


def text_to_images(
    text: str,
    output_dir: str,
    unique_id=None,
    font_path: str = None,
    newline_markup: str = "<br/>",
    background_color: colors.Color = colors.white,
    layout_kwargs: RenderArgs = RenderArgs(),
    p_style_kwargs: dict = None,
):
    """
    Convert text to image by first rendering to PDF and then converting each PDF page to image.
    """

    # Generate unique ID
    if unique_id is None:
        unique_id = get_identifier(text, layout_kwargs)

    # Register font
    if font_path is not None:
        font_name = os.path.splitext(os.path.basename(font_path))[0]
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
        except Exception:
            pass  # Font already registered

    # Create PDF
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, **(layout_kwargs or {}))

    # Create paragraph style
    RE_CJK = re.compile(r"[\u4E00-\u9FFF]")
    p_style_kwargs.setdefault("wordWrap", "CJK" if RE_CJK.search(text) else None)
    custom = ParagraphStyle(
        name="Custom",
        parent=PRESETS["Normal"],
        **(p_style_kwargs or {}),
    )

    # Process text
    def replace_spaces(s):
        return re.sub(r" {2,}", lambda m: "&nbsp;" * len(m.group()), s)

    text = text.replace("\xad", "").replace("\u200b", "")
    processed_text = replace_spaces(escape(text))
    parts = processed_text.split("\n")

    # Create paragraphs in batches
    story = []
    turns = 30
    for i in range(0, len(parts), turns):
        tmp_text = newline_markup.join(parts[i : i + turns])
        story.append(Paragraph(tmp_text, custom))

    # Build PDF
    page_size = doc.pagesize
    doc.build(
        story,
        onFirstPage=lambda c, d: (
            c.saveState(),
            c.setFillColor(background_color),
            c.rect(0, 0, page_size[0], page_size[1], stroke=0, fill=1),
            c.restoreState(),
        ),
        onLaterPages=lambda c, d: (
            c.saveState(),
            c.setFillColor(background_color),
            c.rect(0, 0, page_size[0], page_size[1], stroke=0, fill=1),
            c.restoreState(),
        ),
    )

    pdf_bytes = buf.getvalue()
    buf.close()

    # Create output directory
    out_root = os.path.join(output_dir, unique_id)
    os.makedirs(out_root, exist_ok=True)

    # Convert PDF to images
    image_paths = []

    pdf_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    for i in range(len(pdf_doc)):
        page = pdf_doc.load_page(i)
        pix = page.get_pixmap()
        image_path = os.path.join(out_root, f"page_{i + 1:03d}.png")
        pix.save(image_path)
        image_paths.append(image_path)

    return image_paths
