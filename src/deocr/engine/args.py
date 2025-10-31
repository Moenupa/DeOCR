from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PDFArgs:
    # page geometry
    pagesize: tuple[float, Optional[float]] = field(
        default=(512, 512),
        metadata={
            "help": "(width, height) of each page, expressed in points (pt). Changing this changes the physical size of the PDF pages."
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
        metadata={
            "help": "If true, saves the generated PDF to disk. This is only for debugging since PDF is converted in-memory to images."
        },
    )
    saveImage: bool = field(
        default=True,
        metadata={
            "help": "If true, saves the generated Image to disk. If false, returns PIL Image objects in memory."
        },
    )

    dpi: int = field(
        default=96,
        metadata={"help": "Dots per inch for image rendering."},
    )

    overwrite: bool = field(
        default=True,
        metadata={"help": "If true, overwrites existing directory."},
    )
    extension: str = field(
        default="jpg",
        metadata={"help": "File extension for output images."},
    )

    css: Optional[str] = field(
        default=None,
        metadata={"help": "CSS styles to apply when rendering."},
    )
    css_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to a CSS file to apply when rendering."},
    )
