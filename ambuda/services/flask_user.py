"""
Manages the auth/authentication data flow.
"""
from http import HTTPStatus
from flask import abort, redirect, request, url_for
from flask_login import LoginManager

from ambuda.services import DataSession, AmbudaUser, AmbudaAnonymousUser, UserService



def _load_user(user_id: int) -> AmbudaUser | None:
    """Load a user from the database.

    Flask-Login uses this function to populate the `current_user` variable.
    This variable is made available both by direct import (`from flask_login
    import current_user`) and as a template variable injected into each template.
    """
    with DataSession() as ds:
        return UserService.get(ds, user_id)


def _unauthorized():
    """Defines how to handle unauth requests to routes that expect auth."""

    # An example of an auth API is our Google OCR endpoint.
    if request.blueprint == "api":
        abort(HTTPStatus.UNAUTHORIZED)

    # For regular pages, just prompt the user to sign in.
    return redirect(url_for("auth.sign_in"))


def create_login_manager() -> LoginManager:
    login_manager = LoginManager()
    login_manager.user_loader(_load_user)
    login_manager.unauthorized_handler(_unauthorized)
    login_manager.anonymous_user = AmbudaAnonymousUser

    return login_manager