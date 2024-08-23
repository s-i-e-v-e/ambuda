import datetime
from ambuda.repository import *
from ambuda.services.user import UserService, AmbudaUser, AmbudaAnonymousUser

def create_bot_user(ds: DataSession):
    import unstd.config
    try:
        password = unstd.config.current.AMBUDA_BOT_PASSWORD
    except KeyError as e:
        raise ValueError(
            "Please set the AMBUDA_BOT_PASSWORD environment variable."
        ) from e

    import logging
    logging.debug("Creating bot user ...")
    UserService.create_bot(ds, password)
    logging.debug("Done.")

def create_default_roles(ds: DataSession):
    """Create roles iff they don't exist already.

    NOTE: this script doesn't delete existing roles.
    """
    import logging
    from ambuda.repository import SiteRole
    roles = Role.all(ds)
    existing_names = {s.name for s in roles}
    new_names = {r.value for r in SiteRole if r.value not in existing_names}

    time = datetime.datetime.utcnow()
    if new_names:
        for name in new_names:
            Role.insert(ds, name, time)
            logging.debug(f"Created role: {name}")

    logging.debug("Done. The following roles are defined:")
    roles = Role.all(ds)
    for r in roles:
        logging.debug(f"- {r.name}")

def get_default_id():
    """Used in the `add_page_statuses` migration."""
    engine = create_db()
    with Session(engine) as session:
        return session.query(db.PageStatus).filter_by(name=SitePageStatus.R0).one()


def create_default_page_status(ds: DataSession):
    """Create page statuses iff they don't exist already."""
    engine = engine or create_db()
    logging.debug("Creating PageStatus rows ...")
    with Session(engine) as session:
        statuses = session.query(db.PageStatus).all()
        existing_names = {s.name for s in statuses}
        new_names = {n.value for n in SitePageStatus if n not in existing_names}

        if new_names:
            for name in new_names:
                status = db.PageStatus(name=name)
                session.add(status)
            session.commit()
    logging.debug("Done.")