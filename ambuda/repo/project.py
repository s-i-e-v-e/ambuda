import logging
from slugify import slugify

from ambuda import database as db
from ambuda import queries as q

def add(
    display_title: str,
    creator_id: int,
    num_pages: int,
):
    """
    :param display_title: the project's title.
    :param pdf_path: local path to the source PDF.
    :param output_dir: local path where page images will be stored.
    :param app_environment: the app environment, e.g. `"development"`.
    :param creator_id: the user that created this project.
    """
    # Tasks must be idempotent. Exit if the project already exists.

    session = q.get_session()
    slug = slugify(display_title)
    project = session.query(db.Project).filter_by(slug=slug).first()

    if project:
        raise ValueError(
            f'Project "{display_title}" already exists. Please choose a different title.'
        )

    logging.info(f"Creating project (slug = {slug}) ...")
    session = q.get_session()
    board = db.Board(title=f"{slug} discussion board")
    session.add(board)
    session.flush()

    project = db.Project(slug=slug, display_title=display_title, creator_id=creator_id)
    project.board_id = board.id
    session.add(project)
    session.flush()

    logging.info(f"Fetching project and status (slug = {slug}) ...")
    unreviewed = session.query(db.PageStatus).filter_by(name="reviewed-0").one()

    logging.info(f"Creating {num_pages} Page entries (slug = {slug}) ...")
    for n in range(1, num_pages + 1):
        session.add(
            db.Page(
                project_id=project.id,
                slug=str(n),
                order=n,
                status_id=unreviewed.id,
            )
        )
    session.commit()
