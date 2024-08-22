"""Common queries.

We use this module to organize repetitive query logic and keep our views readable.
For simple or adhoc queries, you can just write them in their corresponding view.
"""

import functools

from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import load_only, scoped_session, selectinload, sessionmaker

import ambuda.database as db

# NOTE: this logic is copied from Flask-SQLAlchemy. We avoid Flask-SQLAlchemy
# because we also need to access the database from a non-Flask context when
# we run database seed scripts.
# ~~~
# Scope the session to the current greenlet if greenlet is available,
# otherwise fall back to the current thread.
try:
    from greenlet import getcurrent as _ident_func
except ImportError:
    from threading import get_ident as _ident_func


# functools.cache makes this return value a singleton.
@functools.cache
def get_engine():
    import unstd.config
    database_uri = unstd.config.current.SQLALCHEMY_DATABASE_URI
    return create_engine(database_uri)


# functools.cache makes this return value a singleton.
@functools.cache
def get_session_class():
    # Scoped sessions remove various kinds of errors, e.g. when using database
    # objects created on different threads.
    #
    # For details, see:
    # - https://stackoverflow.com/questions/12223335
    # - https://flask.palletsprojects.com/en/2.1.x/patterns/sqlalchemy/
    session_factory = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return scoped_session(session_factory, scopefunc=_ident_func)


def get_session():
    """Instantiate a scoped session.

    If we implemented this right, there should be exactly one unique session
    per request.
    """
    Session = get_session_class()
    return Session()


def texts() -> list[db.Text]:
    """Return a list of all texts in no particular older."""
    session = get_session()
    return session.query(db.Text).all()


def page_statuses() -> list[db.PageStatus]:
    session = get_session()
    return session.query(db.PageStatus).all()


def text(slug: str) -> db.Text | None:
    session = get_session()
    return (
        session.query(db.Text)
        .filter_by(slug=slug)
        .options(
            selectinload(db.Text.sections).load_only(
                db.TextSection.slug,
                db.TextSection.title,
            )
        )
        .first()
    )


def text_meta(slug: str) -> db.Text:
    """Return only specific fields from the given text."""
    # TODO: is this method even useful? Is there a performance penalty for
    # using just `text`?
    session = get_session()
    return (
        session.query(db.Text)
        .filter_by(slug=slug)
        .options(
            load_only(
                db.Text.id,
                db.Text.slug,
            )
        )
        .first()
    )


def text_section(text_id: int, slug: str) -> db.TextSection | None:
    session = get_session()
    return session.query(db.TextSection).filter_by(text_id=text_id, slug=slug).first()


def block(text_id: int, slug: str) -> db.TextBlock | None:
    session = get_session()
    return session.query(db.TextBlock).filter_by(text_id=text_id, slug=slug).first()


def block_parse(block_id: int) -> db.BlockParse | None:
    session = get_session()
    return session.query(db.BlockParse).filter_by(block_id=block_id).first()


def projects() -> list[db.Project]:
    """Return all projects in no particular order."""
    session = get_session()
    return session.query(db.Project).all()


def project(slug: str) -> db.Project | None:
    session = get_session()
    return session.query(db.Project).filter(db.Project.slug == slug).first()



def page(project_id, page_slug: str) -> db.Page | None:
    session = get_session()
    return (
        session.query(db.Page)
        .filter((db.Page.project_id == project_id) & (db.Page.slug == page_slug))
        .first()
    )


def user(username: str) -> db.User | None:
    session = get_session()
    return (
        session.query(db.User)
        .filter_by(username=username, is_deleted=False, is_banned=False)
        .first()
    )


def create_user(*, username: str, email: str, raw_password: str) -> db.User:
    session = get_session()
    user = db.User(username=username, email=email)
    user.set_password(raw_password)
    session.add(user)
    session.flush()

    # Allow all users to be proofreaders
    proofreader_role = (
        session.query(db.Role).filter_by(name=db.SiteRole.P1.value).first()
    )
    user_role = db.UserRoles(user_id=user.id, role_id=proofreader_role.id)
    session.add(user_role)

    session.commit()
    return user


def genres() -> list[db.Genre]:
    session = get_session()
    return session.query(db.Genre).all()
