import datetime
from flask import Blueprint, render_template, url_for
from flask_babel import lazy_gettext as _l
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea

from ambuda.repository import DataSession, Board, Thread, Post
from ambuda import queries as q

bp = Blueprint("talk", __name__)


class CreateThreadForm(FlaskForm):
    title = StringField(_l("Title"))
    content = StringField(
        _l("Message"), widget=TextArea(), validators=[DataRequired(), Length(max=10000)]
    )


class CreatePostForm(FlaskForm):
    content = StringField(
        _l("Message"), widget=TextArea(), validators=[DataRequired(), Length(max=10000)]
    )


class EditPostForm(FlaskForm):
    content = StringField(
        _l("Message"), widget=TextArea(), validators=[DataRequired(), Length(max=10000)]
    )


@bp.route("/<slug>/talk/")
def board(slug):
    """
    Show all threads for some board.
    """
    project_ = q.project(slug)
    if project_ is None:
        abort(404)

    with DataSession() as ds:
        board = Board.select(ds, project_.board_id)

    return render_template(
        "proofing/talk/board.html", project=project_, board=board
    )


@bp.route("/<slug>/talk/create-thread", methods=["GET", "POST"])
@login_required
def create_thread(slug):
    project_ = q.project(slug)
    if project_ is None:
        abort(404)

    form = CreateThreadForm()
    if form.validate_on_submit():
        with DataSession() as ds:
            time = datetime.datetime.utcnow()
            thread_id = Thread.insert(
                ds,
                title=form.title.data,
                board_id=project_.board_id,
                author_id=current_user.id,
                time=time,
            )
            Post.insert(
                ds,
                board_id=project_.board_id,
                thread_id=thread_id,
                author_id=current_user.id,
                content = form.content.data,
                time=time,
            )
        return redirect(url_for("proofing.talk.board", slug=slug))

    return render_template(
        "proofing/talk/create-thread.html", project=project_, form=form
    )


@bp.route("/<project_slug>/talk/<thread_id>")
def thread(project_slug, thread_id):
    """
    Show all posts for some thread.
    """
    project_ = q.project(project_slug)
    if project_ is None:
        abort(404)

    with DataSession() as ds:
        t = Thread.select(ds, thread_id)
        if t is None:
            abort(404)

    return render_template("proofing/talk/thread.html", project=project_, thread=t)


@bp.route("/<project_slug>/talk/<thread_id>/create", methods=["GET", "POST"])
@login_required
def create_post(project_slug, thread_id):
    """
    Create a post on an existing thread.
    """
    project_ = q.project(project_slug)
    if project_ is None:
        abort(404)

    with DataSession() as ds:
        t = Thread.select(ds, thread_id)
    if t is None or t.board_id != project_.board_id:
        abort(404)

    form = CreatePostForm()
    if form.validate_on_submit():
        with DataSession() as ds:
            time = datetime.datetime.utcnow()
            Post.insert(
                ds,
                board_id=project_.board_id,
                thread_id=thread_id,
                author_id=current_user.id,
                content = form.content.data,
                time=time,
            )
            Thread.update(
                ds,
                t,
                time=time,
            )
        return redirect(
            url_for(
                "proofing.talk.thread",
                project_slug=project_.slug,
                thread_id=t.id,
            )
        )

    return render_template(
        "proofing/talk/create-post.html", project=project_, thread=t, form=form
    )


@bp.route("/<project_slug>/talk/<thread_id>/<post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(project_slug, thread_id, post_id):
    """
    Edit an existing post.
    """
    project_ = q.project(project_slug)
    if project_ is None:
        abort(404)

    with DataSession() as ds:
        t = Thread.select(ds, thread_id)

    if t is None or t.board_id != project_.board_id:
        abort(404)

    with DataSession() as ds:
        p = Post.select(ds, post_id)

    if p is None or p.thread_id != t.id:
        abort(404)

    if p.author_id != current_user.id:
        abort(403)

    form = EditPostForm()
    if form.validate_on_submit():
        p.content = form.content.data
        with DataSession() as ds:
            time = datetime.datetime.utcnow()
            Post.update(ds, p, time=time)

        return redirect(
            url_for(
                "proofing.talk.thread", project_slug=project_slug, thread_id=thread_id
            )
        )

    form.content.data = p.content
    return render_template(
        "proofing/talk/edit-post.html",
        project=project_,
        thread=t,
        post=p,
        form=form,
    )
