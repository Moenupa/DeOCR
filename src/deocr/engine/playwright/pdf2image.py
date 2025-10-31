import asyncio

try:
    import pymupdf
except ImportError:
    pymupdf = None


def get_image_path(subfolder: str, i: int, total: int, extension: str) -> str:
    return f"{subfolder}/{i:010d}-{total:010d}.{extension}"


def pdf2image(pdf_bytes: bytes, subfolder: str, dpi: int, extension: str) -> list[str]:
    with pymupdf.Document(stream=pdf_bytes, filetype="pdf") as pdf_doc:
        n_pages = len(pdf_doc)
        image_paths: list[str] = []
        for i in range(n_pages):
            page_pdf = pdf_doc.load_page(i)
            pix = page_pdf.get_pixmap(dpi=dpi)
            save_to = get_image_path(subfolder, i, n_pages, extension)
            pix.save(save_to)
            image_paths.append(save_to)

    return image_paths


async def pdf2image_async(
    pdf_bytes: bytes, subfolder: str, dpi: int, extension: str
) -> list[str]:
    return await asyncio.to_thread(pdf2image, pdf_bytes, subfolder, dpi, extension)
