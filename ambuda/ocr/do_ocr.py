"""Background tasks for proofing projects."""

from ambuda.std import id, executor
from ambuda import consts
from ambuda import database as db
from ambuda import queries as q
from ambuda.enums import SitePageStatus

from ambuda.utils.assets import get_page_image_filepath
from ambuda.utils.revisions import add_revision

from ambuda.repo import user as user_repo
from ambuda.ocr import backend


def __run_ocr_for_page(
    project_slug: str,
    page_slug: str,
) -> int:
    bot_user_id = user_repo.get(consts.BOT_USERNAME)
    if bot_user_id is None:
        raise ValueError(f'User "{consts.BOT_USERNAME}" is not defined.')

    # The actual API call.
    image_path = get_page_image_filepath(project_slug, page_slug)
    #ocr_text, ocr_bounding_boxes = backend.exec_google_ocr(image_path)
    ocr_text, ocr_bounding_boxes = backend.exec_tesseract_ocr(image_path)


    session = q.get_session()
    project = q.project(project_slug)
    page = q.page(project.id, page_slug)
    page.ocr_bounding_boxes = ocr_bounding_boxes
    session.add(page)
    session.commit()

    summary = "Run OCR"
    try:
        return add_revision(
            page=page,
            summary=summary,
            content=ocr_text,
            status=SitePageStatus.R0,
            version=0,
            author_id=bot_user_id,
        )
    except Exception as e:
        raise ValueError(
            f'OCR failed for page "{project.slug}/{page.slug}".'
        ) from e


def __run_ocr_for_project(project_slug: str, page_slugs: list[str]):
    for p in page_slugs:
        __run_ocr_for_page(project_slug, p)


def run_ocr_for_project(project: db.Project):
    unedited_pages = [p.slug for p in project.pages if p.version == 0]

    if not unedited_pages:
        return None

    task_id = id.random_string()
    executor.ts_set(task_id, 0, len(unedited_pages), 'PROGRESS')
    executor.exec(__run_ocr_for_project, task_id, project.slug, unedited_pages)
    return task_id
