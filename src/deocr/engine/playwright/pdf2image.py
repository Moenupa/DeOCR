import asyncio
from typing import TYPE_CHECKING

try:
    import pymupdf
except ImportError:
    pymupdf = None


from ..dataio import get_image_path

if TYPE_CHECKING:
    from PIL.Image import Image


async def pdf2image_async(
    pdf_bytes: bytes, subfolder: str, dpi: int, extension: str, save_images: bool = True
) -> tuple[str] | tuple["Image"]:
    out = []
    loop = asyncio.get_event_loop()
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        n_pages = len(pdf_doc)

        for i in range(n_pages):
            page = pdf_doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi)
            if save_images:
                save_to = get_image_path(subfolder, i, n_pages, extension)
                await loop.run_in_executor(None, pix.save, save_to)
                out.append(save_to)
            else:
                pil_image = await loop.run_in_executor(None, pix.pil_image)
                out.append(pil_image)

    return tuple(out)


def pdf2image(
    pdf_bytes: bytes, subfolder: str, dpi: int, extension: str, save_images: bool = True
) -> tuple[str] | tuple["Image"]:
    out = []
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        n_pages = len(pdf_doc)
        # if n_pages == 1:
        #     it = _worker(
        #         (pdf_bytes, subfolder, dpi, extension, save_images, 0, n_pages)
        #     )
        #     return (it,)

        for i in range(n_pages):
            page = pdf_doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi)
            if save_images:
                save_to = get_image_path(subfolder, i, n_pages, extension)
                pix.save(save_to)
                out.append(save_to)
            else:
                out.append(pix.pil_image())

    # from ..defaults import MAX_WORKERS
    # distribute saving work using tqdm
    # out = process_map(
    #     _worker,
    #     [
    #         (pdf_bytes, subfolder, dpi, extension, save_images, i, n_pages)
    #         for i in range(n_pages)
    #     ],
    #     max_workers=None if MAX_WORKERS is None else min(n_pages, MAX_WORKERS),
    #     chunksize=1,
    # )
    return tuple(out)
