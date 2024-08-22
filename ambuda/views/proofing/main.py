"""Views for basic site pages."""
from datetime import datetime, timedelta
from flask import Blueprint, render_template
from sqlalchemy import orm


from ambuda import consts
from ambuda import database as db
from ambuda import queries as q
from ambuda.enums import SitePageStatus
from ambuda.views.proofing.decorators import moderator_required


bp = Blueprint("proofing", __name__)


@bp.route("/")
def index():
    """List all available proofing projects."""

    # Fetch all project data in a single query for better performance.
    session = q.get_session()
    projects = (
        session.query(db.Project)
        .options(
            orm.joinedload(db.Project.pages)
            .load_only(db.Page.id)
            .joinedload(db.Page.status)
        )
        .all()
    )
    status_classes = {
        SitePageStatus.R2: "bg-green-200",
        SitePageStatus.R1: "bg-yellow-200",
        SitePageStatus.R0: "bg-red-300",
        SitePageStatus.SKIP: "bg-slate-100",
    }

    projects = q.projects()
    statuses_per_project = {}
    progress_per_project = {}
    pages_per_project = {}
    for project in projects:
        page_statuses = [p.status.name for p in project.pages]

        # FIXME(arun): catch this properly, prevent prod issues
        if not page_statuses:
            statuses_per_project[project.id] = {}
            pages_per_project[project.id] = 0
            continue

        num_pages = len(page_statuses)
        project_counts = {}
        for enum_value, class_ in status_classes.items():
            fraction = page_statuses.count(enum_value) / num_pages
            project_counts[class_] = fraction
            if enum_value == SitePageStatus.R0:
                # The more red pages there are, the lower progress is.
                progress_per_project[project.id] = 1 - fraction

        statuses_per_project[project.id] = project_counts
        pages_per_project[project.id] = num_pages

    projects.sort(key=lambda x: x.display_title)
    return render_template(
        "proofing/index.html",
        projects=projects,
        statuses_per_project=statuses_per_project,
        progress_per_project=progress_per_project,
        pages_per_project=pages_per_project,
    )


@bp.route("/help/beginners-guide")
def beginners_guide():
    """Display our minimal proofing guidelines."""
    return render_template("proofing/beginners-guide.html")


@bp.route("/help/complete-guide")
def complete_guide():
    """Display our complete proofing guidelines."""
    return render_template("proofing/complete-guide.html")


@bp.route("/help/editor-guide")
def editor_guide():
    """Describe how to use the page editor."""
    return render_template("proofing/editor-guide.html")


@bp.route("/recent-changes")
def recent_changes():
    """Show recent changes across all projects."""
    num_per_page = 100

    # Exclude bot edits, which overwhelm all other edits on the site.
    bot_user = q.user(consts.BOT_USERNAME)
    assert bot_user, "Bot user not defined"

    session = q.get_session()
    recent_revisions = (
        session.query(db.Revision)
        .options(orm.defer(db.Revision.content))
        .filter(db.Revision.author_id != bot_user.id)
        .order_by(db.Revision.created.desc())
        .limit(num_per_page)
        .all()
    )
    recent_activity = [("revision", r.created, r) for r in recent_revisions]

    recent_projects = (
        session.query(db.Project)
        .order_by(db.Project.created_at.desc())
        .limit(num_per_page)
        .all()
    )
    recent_activity += [("project", p.created_at, p) for p in recent_projects]

    recent_activity.sort(key=lambda x: x[1], reverse=True)
    recent_activity = recent_activity[:num_per_page]
    return render_template(
        "proofing/recent-changes.html", recent_activity=recent_activity
    )


@bp.route("/talk")
def talk():
    """Show discussion across all projects."""
    projects = q.projects()

    # FIXME: optimize this once we have a higher thread volume.
    all_threads = []
    from ambuda.repository import DataSession, Board, Thread
    with DataSession() as ds:
        for p in projects:
            b = Board.select(ds, p.board_id)
            assert b
            xs = Thread.select_by_board(ds, b.id)
            for x in xs:
                all_threads.append((p, x))

    all_threads.sort(key=lambda x: x[1].updated_at, reverse=True)

    return render_template("proofing/talk.html", all_threads=all_threads)


@bp.route("/admin/dashboard/")
@moderator_required
def dashboard():
    now = datetime.now()
    days_ago_30d = now - timedelta(days=30)
    days_ago_7d = now - timedelta(days=7)
    days_ago_1d = now - timedelta(days=1)

    session = q.get_session()
    bot = session.query(db.User).filter_by(username=consts.BOT_USERNAME).one()
    bot_id = bot.id

    revisions_30d = (
        session.query(db.Revision)
        .filter(
            (db.Revision.created >= days_ago_30d) & (db.Revision.author_id != bot_id)
        )
        .options(orm.load_only(db.Revision.created, db.Revision.author_id))
        .order_by(db.Revision.created)
        .all()
    )
    revisions_7d = [x for x in revisions_30d if x.created >= days_ago_7d]
    revisions_1d = [x for x in revisions_7d if x.created >= days_ago_1d]
    num_revisions_30d = len(revisions_30d)
    num_revisions_7d = len(revisions_7d)
    num_revisions_1d = len(revisions_1d)

    num_contributors_30d = len({x.author_id for x in revisions_30d})
    num_contributors_7d = len({x.author_id for x in revisions_7d})
    num_contributors_1d = len({x.author_id for x in revisions_1d})

    return render_template(
        "proofing/dashboard.html",
        num_revisions_30d=num_revisions_30d,
        num_revisions_7d=num_revisions_7d,
        num_revisions_1d=num_revisions_1d,
        num_contributors_30d=num_contributors_30d,
        num_contributors_7d=num_contributors_7d,
        num_contributors_1d=num_contributors_1d,
    )


from ambuda.views.proofing import project_create

@bp.route("/create-project", methods=["GET", "POST"])
def create_project():
    return project_create.create_project()


@bp.route("/status/<task_id>")
def create_project_status(task_id):
    return project_create.create_project_status(task_id)