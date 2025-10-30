from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class PDFArgs:
    # page geometry
    pagesize: tuple[float, Optional[float]] = field(
        default=(512, 512),
        metadata={
            "help": "(width, height) of each page, expressed in points (pt). Changing this changes the physical size of the PDF pages."
        },
    )
    pageTemplates: List[Any] = field(
        default_factory=list,
        metadata={
            "help": "A list of `PageTemplate` objects that define how frames (text columns, images, etc.) are laid out on each page and what happens on a page‑break. Empty list → a single default template is created automatically."
        },
    )
    showBoundary: int = field(
        default=0,
        metadata={
            "help": "If true, the borders of every `Frame` are drawn (thin red lines) – handy for debugging layout."
        },
    )
    marginLeft: float = field(
        default=0,
        metadata={"help": "Left margin in points."},
    )
    marginRight: float = field(
        default=0,
        metadata={"help": "Right margin in points."},
    )
    marginTop: float = field(
        default=0,
        metadata={"help": "Top margin in points."},
    )
    marginBottom: float = field(
        default=0,
        metadata={"help": "Bottom margin in points."},
    )

    invariant: Optional[Any] = field(
        default=None,
        metadata={
            "help": "A user‑supplied object that will be stored unchanged on the `DocTemplate` instance; you can use it to pass any extra data you need while building the document."
        },
    )
    rotation: int = field(
        default=0,
        metadata={
            "help": "Whole‑page rotation in degrees (0, 90, 180, 270). The page is rotated after it is drawn, so text stays upright relative to the new orientation."
        },
    )
    cropMarks: Optional[Any] = field(
        default=None,
        metadata={
            "help": "If supplied, a CropMarks object is used to draw printer’s crop marks on each page."
        },
    )
    enforceColorSpace: Optional[Any] = field(
        default=None,
        metadata={
            "help": "When set to 'RGB' or 'CMYK' forces all images and colors to be converted to that colour space, useful for press‑ready PDFs."
        },
    )
    cropBox: Optional[Any] = field(
        default=None,
        metadata={
            "help": "Optional PDF page boxes that define the printable area (CropBox)."
        },
    )
    artBox: Optional[Any] = field(
        default=None,
        metadata={"help": "Optional PDF page boxes that define the art area."},
    )
    trimBox: Optional[Any] = field(
        default=None,
        metadata={
            "help": "Optional PDF page boxes that define the trim area (for cutting)."
        },
    )
    bleedBox: Optional[Any] = field(
        default=None,
        metadata={
            "help": "Optional PDF page boxes that define the bleed area (extra margin for printing)."
        },
    )

    # layout control
    allowSplitting: bool = field(
        default=True,
        metadata={
            "help": "If false, forces each Paragraph to stay on the same page; if it doesn’t fit, it is moved to the next page."
        },
    )
    keepTogetherClass: Any = field(
        default=None,
        metadata={"help": "How flowables are broken across pages."},
    )

    # other options
    forceOnePage: bool = field(
        default=False,
        metadata={
            "help": "If true, forces the output to be a single page by adjusting the height as needed."
        },
    )
    autoAdjustHeight: bool = field(
        default=False,
        metadata={
            "help": "If true, automatically adjusts the page height to fit the content."
        },
    )
    savePDF: bool = field(
        default=False,
        metadata={"help": "If true, saves the generated PDF to disk."},
    )

    # dpi
    dpi: int = field(
        default=96,
        metadata={"help": "Dots per inch for image rendering."},
    )
