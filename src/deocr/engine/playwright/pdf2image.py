import asyncio
from typing import TYPE_CHECKING

try:
    import pymupdf
except ImportError:
    pymupdf = None


from ..dataio import get_image_path

if TYPE_CHECKING:
    from PIL.Image import Image


async def fn_save_img_async(
    pil_image: "Image", save_to: str, save_kwargs: dict
) -> None:
    pil_image.save(save_to, **save_kwargs)


async def pdf2image_async(
    pdf_bytes: bytes,
    subfolder: str,
    dpi: int,
    save_format: str,
    enable_saving: bool = True,
    save_kwargs: dict = None,
) -> tuple[str] | tuple["Image"]:
    out = []
    loop = asyncio.get_event_loop()
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        n_pages = len(pdf_doc)

        for i in range(n_pages):
            page = pdf_doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi)
            pil_image = await loop.run_in_executor(None, pix.pil_image)
            # no need to save, add object
            if not enable_saving:
                out.append(pil_image)
                continue

            save_to = get_image_path(subfolder, i, n_pages, save_format)
            out.append(save_to)
            await fn_save_img_async(pil_image, save_to, save_kwargs or {})

    return tuple(out)


def pdf2image(
    pdf_bytes: bytes,
    subfolder: str,
    dpi: int,
    save_format: str,
    enable_saving: bool = True,
    save_kwargs: dict = None,
) -> tuple[str] | tuple["Image"]:
    out = []
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        n_pages = len(pdf_doc)
        for i in range(n_pages):
            page = pdf_doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi)
            pil_image = pix.pil_image()
            if not enable_saving:
                out.append(pil_image)
                continue

            save_to = get_image_path(subfolder, i, n_pages, save_format)
            pil_image.save(save_to, **(save_kwargs or {}))
            out.append(save_to)

    return tuple(out)
