"""Config management for the Ambuda Flask app.

All of Ambuda's interesting config values are defined in the project's `.env`
file. Here, we parse that file and map its values to specific config objects,
which we then load into Flask.

Most config values are documented on :class:`BaseConfig`, from which all other
classes inherit. Production-specific config values, which are mainly replated
to deployment, are defined on :class:`ProductionConfig`.

It's considered a best practice to keep this module outside the application
package: From the Flask docs (emphasis added):

    Configuration becomes more useful if you can store it in a separate file,
    *ideally located outside the actual application package*.
"""

import logging

from pathlib import Path
from typing import Dict, Any, Optional
import unstd.os
import os

#: The test environment. For unit tests only.
TESTING = "testing"
#: The development environment. For local development.
DEVELOPMENT = "development"
#: The build environment. For build on github.
BUILD = "build"
#: The staging environment. For testing on staging.
STAGING = "staging"
#: The production environment. For production serving.
PRODUCTION = "production"


def __read_env_file(name) -> Dict[str, str]:
    m = dict()
    if not unstd.os.file_exists(name):
        return m

    with open(name, 'r') as f:
        xs = [x.strip() for x in f.readlines()]
        xs = filter(lambda x: x and not x.startswith('#'), xs)
        xs = [x.split('=') for x in xs]
        for x in xs:
            m[x[0]] = x[1]
    return m


def __read_env(file, default_file) -> Dict[str, str]:
    # load default
    m = __read_env_file(default_file)
    print(f'DEFAULT: {m}')

    # override with one from file
    n = __read_env_file(file)
    print(f'ENV: {n}')
    for k, v in m.items():
        m[k] = n[k] if k in n else m[k]

    return m


class HostConfig:
    AMBUDA_VERSION: str
    AMBUDA_IMAGE: str
    AMBUDA_IMAGE_LATEST: str
    AMBUDA_HOST_IP: str
    AMBUDA_HOST_PORT: int
    AMBUDA_CONTAINER_NAME = "deploy-ambuda"

    def __init__(self, git_sha: str, external_ip: str, dt: Dict[str, Any]) -> None:
        self.AMBUDA_VERSION = dt["AMBUDA_VERSION"]
        self.AMBUDA_HOST_PORT = dt["AMBUDA_HOST_PORT"]
        self.AMBUDA_IMAGE = f"ambuda-release:{self.AMBUDA_VERSION}-{git_sha}"
        self.AMBUDA_IMAGE_LATEST = "ambuda-release:latest"
        self.AMBUDA_HOST_IP = external_ip


class BaseConfig:
    # Core settings
    # -------------

    #: The Flask app environment ("production", "development", etc.). We set
    #: this explicitly so that Celery can have access to it and load an
    #: appropriate application context.
    AMBUDA_ENVIRONMENT: str
    FLASK_ENV: str
    #: Internal secret key for encrypting sensitive data.
    SECRET_KEY: str

    #: URI for the Ambuda database. This URI (also called a URL in some docs)
    #: has the following basic format:
    #:
    #:     dialect+driver://username:password@host:port/database
    #:
    #: For more information, see:
    #:
    #: https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
    SQLALCHEMY_DATABASE_URI: str

    AMBUDA_CONTAINER_IP: str
    #: Where to store user uploads (PDFs, images, etc.).
    FLASK_UPLOAD_FOLDER: str
    VIDYUT_DATA_DIR: str
    VIDYUT_DATA_URL: str

    #: Logger setup
    LOG_LEVEL: int

    # Extensions
    # ----------

    # Flask-Babel

    #: Default locale. This is "en" by default, but declare it here to be
    #: explicit.
    BABEL_DEFAULT_LOCALE: str
    TEMPLATES_AUTO_RELOAD: str

    # Flask-Mail

    #: URL for mail server.
    MAIL_SERVER: str
    #: Port for mail server.
    MAIL_PORT: str
    #: If ``True``, use TLS for email encryption.
    MAIL_USE_TLS: bool  # Default: True
    #: Username for mail server.
    MAIL_USERNAME: str
    #: Password for mail server.
    MAIL_PASSWORD: str
    #: Default sender for site emails.
    MAIL_DEFAULT_SENDER: str

    # Flask-WTF

    #: If True, enable cross-site request forgery (CSRF) protection.
    #: This must be True in production.
    WTF_CSRF_ENABLED: bool # Default: True

    # Services
    # --------

    #: ReCAPTCHA public key.
    RECAPTCHA_PUBLIC_KEY: str

    #: ReCAPTCHA private key.
    RECAPTCHA_PRIVATE_KEY: str

    #: Sentry data source name (DSN).
    #: We use Sentry to get notifications about server errors.
    SENTRY_DSN: str

    REDIS_PORT: str
    REDIS_HOST: str
    # Test-only
    # ---------

    #: If ``True``, enable the Flask debugger.
    DEBUG: bool  # Default: False

    #: If ``True``, enable testing mode.
    TESTING: bool  # Default: False

    # Environment variables
    # ---------------------

    # AMBUDA_BOT_PASSWORD is the password we use for the "ambuda-bot" account.
    # We set this account as an envvar because we need to create this user as
    # part of database seeding.
    AMBUDA_BOT_PASSWORD: str
    # GOOGLE_APPLICATION_CREDENTIALS contains credentials for the Google Vision
    # API, but these credentials are fetched by the Google API implicitly,
    # so we don't need to define it on the Config object here.
    GOOGLE_APPLICATION_CREDENTIALS: str

    def __init__(self, dt: Optional[Dict[str, str]]) -> None:
        if dt:
            self.AMBUDA_ENVIRONMENT = dt['AMBUDA_ENVIRONMENT']
            self.FLASK_ENV = PRODUCTION if self.AMBUDA_ENVIRONMENT == PRODUCTION else DEVELOPMENT
            self.SECRET_KEY = dt["SECRET_KEY"]
            self.SQLALCHEMY_DATABASE_URI = dt["SQLALCHEMY_DATABASE_URI"]
            self.AMBUDA_CONTAINER_IP = dt["AMBUDA_CONTAINER_IP"]
            self.FLASK_UPLOAD_FOLDER = dt["FLASK_UPLOAD_FOLDER"]
            self.VIDYUT_DATA_DIR = dt["VIDYUT_DATA_DIR"]
            self.VIDYUT_DATA_URL = dt["VIDYUT_DATA_URL"]
            self.LOG_LEVEL = logging.getLevelNamesMapping()[dt["LOG_LEVEL"]]
            self.BABEL_DEFAULT_LOCALE = dt["BABEL_DEFAULT_LOCALE"]
            self.TEMPLATES_AUTO_RELOAD = dt["TEMPLATES_AUTO_RELOAD"]
            self.MAIL_SERVER = dt["MAIL_SERVER"]
            self.MAIL_PORT = dt["MAIL_PORT"]
            self.MAIL_USE_TLS = dt["MAIL_USE_TLS"] == "True"
            self.MAIL_USERNAME = dt["MAIL_USERNAME"]
            self.MAIL_PASSWORD = dt["MAIL_PASSWORD"]
            self.MAIL_DEFAULT_SENDER = dt["MAIL_DEFAULT_SENDER"]
            self.WTF_CSRF_ENABLED = dt["WTF_CSRF_ENABLED"] == "True"
            self.RECAPTCHA_PUBLIC_KEY = dt["RECAPTCHA_PUBLIC_KEY"]
            self.RECAPTCHA_PRIVATE_KEY = dt["RECAPTCHA_PRIVATE_KEY"]
            self.SENTRY_DSN = dt["SENTRY_DSN"]
            self.REDIS_PORT = dt["REDIS_PORT"]
            self.REDIS_HOST = dt["REDIS_HOST"]
            self.DEBUG = dt["DEBUG"] == "True"
            self.TESTING = dt["TESTING"] == "True"
            self.AMBUDA_BOT_PASSWORD = dt["AMBUDA_BOT_PASSWORD"]
            self.GOOGLE_APPLICATION_CREDENTIALS = dt["GOOGLE_APPLICATION_CREDENTIALS"]


def _validate_config(config: BaseConfig):
    """Examine the given config and fail if the config is malformed.

    :param config: the config to test
    """
    assert config.AMBUDA_ENVIRONMENT in {
        TESTING,
        DEVELOPMENT,
        BUILD,
        STAGING,
        PRODUCTION,
    }

    if not config.SQLALCHEMY_DATABASE_URI:
        raise ValueError("This config does not define SQLALCHEMY_DATABASE_URI")

    if not config.FLASK_UPLOAD_FOLDER:
        raise ValueError("This config does not define FLASK_UPLOAD_FOLDER.")

    if not Path(config.FLASK_UPLOAD_FOLDER).is_absolute():
        raise ValueError("FLASK_UPLOAD_FOLDER must be an absolute path.")

    if not config.VIDYUT_DATA_DIR:
        print("Error! VIDYUT_DATA_DIR is not set. Please set environment variable VIDYUT_DATA_DIR")
        return False

    if not config.VIDYUT_DATA_URL:
        print("Error! URL to fetch Vidyut data is not set. Please set environment variable VIDYUT_DATA_URL")
        return False

    # Production-specific validation.
    if config.AMBUDA_ENVIRONMENT == PRODUCTION:
        # All keys must be set.
        for key in dir(config):
            if key.isupper():
                value = getattr(config, key)
                assert value is not None, f"Config param {key} must not be `None`"

        # App must not be in debug/test mode.
        assert config.WTF_CSRF_ENABLED
        assert not config.DEBUG
        assert not config.TESTING

        # Google credentials must be set and exist.
        google_creds = config.GOOGLE_APPLICATION_CREDENTIALS
        assert google_creds
        assert Path(google_creds).exists()


def is_production_config(c: BaseConfig) -> bool:
    return c.AMBUDA_ENVIRONMENT == PRODUCTION


def is_testing_config(c: BaseConfig) -> bool:
    return c.AMBUDA_ENVIRONMENT == TESTING


def load_config_object(name: str):
    """Load and validate an application config."""
    read = lambda x: BaseConfig(__read_env('/data/container.env', f'/app/deploy/{x}.container.env'))
    config_map = {
        TESTING: read('testing'),
        DEVELOPMENT: read('development.container.env'),
        BUILD: read('build.container.env'),
        STAGING: read('staging.container.env'),
        PRODUCTION: read('production.container.env'),
    }
    config = config_map[name]
    _validate_config(config)
    return config


def read_host_config() -> HostConfig:
    return HostConfig(
        unstd.os.get_git_sha(),
        unstd.os.get_external_ip(),
        __read_env('/data/ambuda/host.env', 'deploy/envars/default.host.env')
    )


def read_container_config() -> BaseConfig:
    return BaseConfig(__read_env('/data/container.env', '/app/deploy/envars/default.container.env'))


print(f'os_file: {__file__}')
if __file__ == '/app/unstd/config.py':
    current = read_container_config()
else:
    current = BaseConfig(None)

from pathlib import Path

TMP_DIR = Path("/tmp") / "ambuda-seeding"
GRETIL_DATA_DIR = TMP_DIR / "ambuda-gretil"
DCS_DATA_DIR = TMP_DIR / "ambuda-dcs"
DCS_RAW_FILE_DIR = TMP_DIR / "dcs-raw" / "files"
CACHE_DIR = TMP_DIR / "download-cache"