from pathlib import Path
import pypdf

from ambuda.std import id, executor


def get_page_count(pdf_path: str) -> int:
    doc = pypdf.PdfReader(pdf_path)
    return len(doc.pages)


def __split_pdf_into_pages(
    task_id: str,
    pdf_path: Path,
    output_dir: Path
):
    """Split the given PDF into N .jpg images, one image per page.

    :param pdf_path: filesystem path to the PDF we should process.
    :param output_dir: the directory to which we'll write these images.
    """
    n = 0
    doc = pypdf.PdfReader(pdf_path)
    page_count = len(doc.pages)
    for page in doc.pages:
        assert len(page.images) == 1
        image = page.images[0]
        n += 1
        output_path = output_dir / f"{n}.jpg"
        with output_path.open('wb') as f:
            f.write(image.data)

        executor.ts_set(task_id, n, page_count, 'PROGRESS')
    executor.ts_set(task_id, n, page_count, 'SUCCESS')


def split_pdf_into_pages(
    pdf_path: Path,
    output_dir: Path
):
    task_id = id.random_string()
    doc = pypdf.PdfReader(pdf_path)
    page_count = len(doc.pages)
    executor.ts_set(task_id, 0, page_count, 'PROGRESS')
    executor.exec(__split_pdf_into_pages, task_id, pdf_path, output_dir)
    return task_id
