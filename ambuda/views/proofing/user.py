from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import BooleanField, StringField
from wtforms.widgets import TextArea

from ambuda import database as db
from ambuda import queries as q

from ambuda.utils import heatmap
from ambuda.views.proofing.decorators import moderator_required
from ambuda.services import DataSession, UserService, AmbudaUser, Role, SiteRole
from data import List

bp = Blueprint("user", __name__)


class RolesForm(FlaskForm):
    pass


class EditProfileForm(FlaskForm):
    description = StringField("Profile description", widget=TextArea())


@bp.route("/<username>/")
def summary(username):
    with DataSession() as ds:
        user = UserService.get_by_name(ds, username)
    if not user:
        abort(404)

    return render_template(
        "proofing/user/summary.html",
        user=user,
    )


@bp.route("/<username>/activity")
def activity(username):
    """Summarize the user's public activity on Ambuda."""
    with DataSession() as ds:
        user = UserService.get_by_name(ds, username)
    if not user:
        abort(404)

    session = q.get_session()
    recent_revisions = (
        session.query(db.Revision)
        .options(
            orm.defer(db.Revision.content),
            orm.joinedload(db.Revision.page).load_only(db.Page.id, db.Page.slug),
        )
        .filter_by(author_id=user.id)
        .order_by(db.Revision.created.desc())
        .limit(100)
        .all()
    )
    recent_projects = (
        session.query(db.Project)
        .filter_by(creator_id=user.id)
        .order_by(db.Project.created_at.desc())
        .all()
    )

    recent_activity = [("revision", r.created, r) for r in recent_revisions]
    recent_activity += [("project", p.created_at, p) for p in recent_projects]
    hm = heatmap.create(x[1].date() for x in recent_activity)

    return render_template(
        "proofing/user/activity.html",
        user=user,
        recent_activity=recent_activity,
        heatmap=hm,
    )


@bp.route("/<username>/edit", methods=["GET", "POST"])
@login_required
def edit(username):
    """
    Allow a user to edit their own information.
    """
    with DataSession() as ds:
        user = UserService.get_by_name(ds, username)
        if not user:
            abort(404)

        # Only this user can edit their bio.
        if username != current_user.username:
            abort(403)

        form = EditProfileForm(obj=user)
        if form.validate_on_submit():
            form.populate_obj(user)
            UserService.update_description(ds, user)

            flash("Saved changes.", "success")
            return redirect(url_for("proofing.user.summary", username=username))

        return render_template("proofing/user/edit.html", user=user, form=form)


def _make_role_form(roles: List[Role], user_role_ids: List[int], user: AmbudaUser):
    descriptions = {
        SiteRole.P1: "Proofreading 1 (can make pages yellow)",
        SiteRole.P2: "Proofreading 2 (can make pages green)",
        SiteRole.MODERATOR: "Moderator",
    }
    # We're mutating a global object, but this is safe because we're doing so
    # in an idempotent way.
    for r in roles:
        attr_name = f"id_{r.id}"
        user_has_role = r.id in user_role_ids
        setattr(
            RolesForm,
            attr_name,
            BooleanField(descriptions.get(r.name, r.name), default=user_has_role),
        )
    return RolesForm()


@bp.route("/<username>/admin", methods=["GET", "POST"])
@moderator_required
def admin(username):
    """
    Adjust a user's roles.
    """
    with DataSession() as ds:
        user = UserService.get_by_name(ds, username)
        if not user:
            abort(404)

        session = q.get_session()
        # Exclude admin.
        # (Admin roles should be added manually by the server administrator.)
        user_role_ids = UserService.roles_by_user(ds, user)
        all_roles = UserService.roles(ds).filter(lambda x: x.name != "admin")
        all_roles = sorted(all_roles, key=lambda x: x.name)
        form = _make_role_form(List(all_roles), user_role_ids, user)

        if form.validate_on_submit():
            # delete all roles for user
            UserService.delete_roles_by_user(ds, user)

            id_to_role = {r.id: r for r in all_roles}
            for key, should_have_role in form.data.items():
                if not key.startswith("id_"):
                    continue

                _, _, id = key.partition("_")
                id = int(id)
                r = id_to_role[id]
                UserService.add_role(ds, user, r)

            session.add(user)
            session.commit()

            flash("Saved changes.", "success")

        return render_template(
            "proofing/user/admin.html",
            user=user,
            form=form,
        )
