"""Main entrypoint for the Ambuda application.

For a high-level overview of the application and how to operate it, see:

https://ambuda.readthedocs.io/en/latest/
"""

import logging
import sys

import sentry_sdk
from flask import Flask, session
from flask_babel import Babel, pgettext
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy import exc

from unstd import config
from ambuda import admin as admin_manager
from ambuda import auth as auth_manager
from ambuda import checks, filters, queries
from ambuda.consts import LOCALES
from ambuda.mail import mailer
from ambuda.utils import assets
from ambuda.utils.json_serde import AmbudaJSONEncoder
from ambuda.utils.url_converters import ListConverter
from ambuda.views.about import bp as about
from ambuda.views.api import bp as api
from ambuda.views.auth import bp as auth
from ambuda.views.blog import bp as blog
from ambuda.views.dictionaries import bp as dictionaries
from ambuda.views.proofing import bp as proofing
from ambuda.views.reader.parses import bp as parses
from ambuda.views.reader.texts import bp as texts
from ambuda.views.site import bp as site


def _initialize_sentry(sentry_dsn: str):
    """Initialize basic monitoring through the third-party Sentry service."""
    sentry_sdk.init(
        dsn=sentry_dsn, integrations=[FlaskIntegration()], traces_sample_rate=0
    )


def _initialize_db_session(app, config_spec: config.ContainerConfig):
    """Ensure that our SQLAlchemy session behaves well.

    The Flask-SQLAlchemy library manages all of this boilerplate for us
    automatically, but Flask-SQLAlchemy has relatively poor support for using
    our models outside of the application context, e.g. when running seed
    scripts or other batch jobs. So instead of using that extension, we manage
    the boilerplate ourselves.
    """

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Reset session state to prevent caching and memory leaks."""
        queries.get_session_class().remove()

    if config_spec.is_production:
        # The hook below hides database errors. So, install the hook only if
        # we're in production.

        @app.errorhandler(exc.SQLAlchemyError)
        def handle_db_exceptions(error):
            """Rollback errors so that the db can handle future requests."""
            session = queries.get_session()
            session.rollback()


def _initialize_logger(log_level: int) -> None:
    """Initialize a simple logger for all requests."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    )
    logging.getLogger().setLevel(log_level)
    logging.getLogger().addHandler(handler)


def create_app():
    """Initialize the Ambuda application."""

    config_spec = config.current

    # Initialize Sentry monitoring only in production so that our Sentry page
    # contains only production warnings (as opposed to dev warnings).
    #
    # "Configuration should happen as early as possible in your application's
    # lifecycle." -- Sentry docs
    if config_spec.is_production:
        _initialize_sentry(config_spec.SENTRY_DSN)

    app = Flask(__name__)

    # Config
    app.config.from_object(config_spec)

    # Sanity checks
    if not config_spec.is_testing:
        with app.app_context():
            checks.check_database_uri(config_spec.SQLALCHEMY_DATABASE_URI)

    # Logger
    _initialize_logger(config_spec.LOG_LEVEL)

    # Database
    _initialize_db_session(app, config_spec)

    # A custom Babel locale_selector.
    def get_locale():
        return session.get("locale", config_spec.BABEL_DEFAULT_LOCALE)

    # Extensions
    Babel(app, locale_selector=get_locale)

    login_manager = auth_manager.create_login_manager()
    login_manager.init_app(app)

    mailer.init_app(app)

    with app.app_context():
        _ = admin_manager.create_admin_manager(app)

    # Route extensions
    app.url_map.converters["list"] = ListConverter

    # Blueprints
    app.register_blueprint(about, url_prefix="/about")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth)
    app.register_blueprint(blog, url_prefix="/blog")
    app.register_blueprint(dictionaries, url_prefix="/tools/dictionaries")
    app.register_blueprint(parses, url_prefix="/parses")
    app.register_blueprint(proofing, url_prefix="/proofing")
    app.register_blueprint(site)
    app.register_blueprint(texts, url_prefix="/texts")

    # Debug-only routes for local development.
    if app.debug or config_spec.is_testing:
        from ambuda.views.debug import bp as debug_bp

        app.register_blueprint(debug_bp, url_prefix="/debug")

    # i18n string trimming
    app.jinja_env.policies["ext.i18n.trimmed"] = True
    # Template functions and filters
    app.jinja_env.filters.update(
        {
            "d": filters.devanagari,
            "slp2dev": filters.slp_to_devanagari,
            "devanagari": filters.devanagari,
            "roman": filters.roman,
            "markdown": filters.markdown,
            "time_ago": filters.time_ago,
        }
    )
    app.jinja_env.globals.update(
        {
            "asset": assets.hashed_static,
            "pgettext": pgettext,
            "ambuda_locales": LOCALES,
        }
    )

    app.json_encoder = AmbudaJSONEncoder
    return app
