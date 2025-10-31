import os
from typing import TYPE_CHECKING

from tqdm.contrib.concurrent import process_map

try:
    import pymupdf
except ImportError:
    pymupdf = None


if TYPE_CHECKING:
    from PIL.Image import Image


if "DEOCR_PDF2IMAGE_WORKERS" in os.environ:
    MAX_WORKERS = int(os.environ["DEOCR_PDF2IMAGE_WORKERS"])
else:
    MAX_WORKERS = None


def get_image_path(subfolder: str, i: int, total: int, extension: str) -> str:
    return f"{subfolder}/{i:010d}-{total:010d}.{extension}"


def _worker(args):
    pdf_bytes, subfolder, dpi, extension, save_images, i, n_pages = args
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        page_pdf = pdf_doc.load_page(i)
        pix = page_pdf.get_pixmap(dpi=dpi)
        if save_images:
            save_to = get_image_path(subfolder, i, n_pages, extension)
            pix.save(save_to)
            return save_to
        else:
            return pix.pil_image()


def pdf2image(
    pdf_bytes: bytes, subfolder: str, dpi: int, extension: str, save_images: bool = True
) -> list[str] | list["Image"]:
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        n_pages = len(pdf_doc)
        if n_pages == 1:
            it = _worker(
                (pdf_bytes, subfolder, dpi, extension, save_images, 0, n_pages)
            )
            return [it]

    # distribute saving work using tqdm
    out = process_map(
        _worker,
        [
            (pdf_bytes, subfolder, dpi, extension, save_images, i, n_pages)
            for i in range(n_pages)
        ],
        max_workers=None if MAX_WORKERS is None else min(n_pages, MAX_WORKERS),
        chunksize=1,
    )
    return out
