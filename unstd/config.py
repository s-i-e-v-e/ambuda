import logging

from typing import Dict, Any, Optional, List
from unstd import git, os

DEFAULT = "default"
#: The test environment. For unit tests only.
TESTING = "testing"
#: The development environment. For local development.
DEVELOPMENT = "development"
#: The staging environment. For testing on staging.
STAGING = "staging"
#: The production environment. For production serving.
PRODUCTION = "production"

DIR_STD = "/data/ambuda"
CONTAINER_FILE_STD = f"{DIR_STD}/container.toml"
LOCAL = ".local/share/ambuda"
def __get_host_data_dir() -> str:
    host_data_dir = DIR_STD
    if not os.dir_exists(host_data_dir):
        host_data_dir = f"{os.home()}/{LOCAL}"
        if not os.dir_exists(host_data_dir):
            os.make_dir(host_data_dir)
        else:
            pass
    else:
        pass
    return host_data_dir


def __read_env_file(path: str) -> Dict[str, Any]:
    return os.read_toml(path) if os.file_exists(path) else dict()


def __read_env(type: str, default: dict[str, Any], n: dict[str, Any]) -> Dict[str, Any]:
    # load default
    m = default

    # override with one from file
    if not n:
        logging.warning(f"{type} config: going with defaults (if available). If you have defined a custom config,\nplease put it in {DIR_STD}/{type}.toml or ~/{LOCAL}/{type}.toml on the HOST")
    else:
        for k in m.keys():
            v = n[k] if k in n.keys() else m[k]
            m[k] = v
    return m


class RemoteHostConfig:
    REMOTE_HOST: str
    REMOTE_PORT: str
    REMOTE_USER: str
    SSH_KEY_OR_FILE: str

    def __init__(self, dt: Dict[str, str]) -> None:
        self.REMOTE_HOST = dt["REMOTE_HOST"]
        self.REMOTE_PORT = dt["REMOTE_PORT"]
        self.REMOTE_USER = dt["REMOTE_USER"]
        self.SSH_KEY_OR_FILE = dt["SSH_KEY_OR_FILE"]


class HostConfig:
    AMBUDA_VERSION: str
    GIT_BRANCH: str
    GIT_SHA: str
    HOST_DATA_DIR: str
    HOST_IP: str
    HOST_PORT: int
    CONTAINER_NAME = "deploy-ambuda"

    def __init__(self, host_data_dir, git_branch: str, git_sha: str, external_ip: str, dt: Dict[str, Any]) -> None:
        self.AMBUDA_VERSION = dt["AMBUDA_VERSION"]
        self.HOST_DATA_DIR = host_data_dir
        self.HOST_PORT = dt["HOST_PORT"]
        self.GIT_BRANCH = git_branch
        self.GIT_SHA = git_sha
        self.HOST_IP = external_ip


class ContainerConfig:
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
    DATABASE_FILE: str

    AMBUDA_CONTAINER_IP: str
    #: Where to store user uploads (PDFs, images, etc.).
    FLASK_UPLOAD_DIR: str
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
    WTF_CSRF_ENABLED: bool  # Default: True

    # Services
    # --------

    #: ReCAPTCHA public key.
    RECAPTCHA_PUBLIC_KEY: str

    #: ReCAPTCHA private key.
    RECAPTCHA_PRIVATE_KEY: str

    #: Sentry data source name (DSN).
    #: We use Sentry to get notifications about server errors.
    SENTRY_DSN: str

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

    # js/css - main + generated
    STATIC_DIR: str
    # raw files (dict/dcs/gretil/etc)
    RAW_DATA_DIR: str
    is_production: bool
    is_testing: bool

    def __init__(self, dt: Optional[Dict[str, Any]]) -> None:
        if dt:
            self.AMBUDA_ENVIRONMENT = dt["AMBUDA_ENVIRONMENT"]
            self.FLASK_ENV = (
                PRODUCTION if self.AMBUDA_ENVIRONMENT == PRODUCTION else DEVELOPMENT
            )
            self.SECRET_KEY = dt["SECRET_KEY"]
            self.SQLALCHEMY_DATABASE_URI = dt["SQLALCHEMY_DATABASE_URI"]
            self.AMBUDA_CONTAINER_IP = dt["AMBUDA_CONTAINER_IP"]
            self.FLASK_UPLOAD_DIR = dt["FLASK_UPLOAD_DIR"]
            self.VIDYUT_DATA_DIR = dt["VIDYUT_DATA_DIR"]
            self.VIDYUT_DATA_URL = dt["VIDYUT_DATA_URL"]
            self.LOG_LEVEL = logging.getLevelNamesMapping()[dt["LOG_LEVEL"]]
            self.BABEL_DEFAULT_LOCALE = dt["BABEL_DEFAULT_LOCALE"]
            self.TEMPLATES_AUTO_RELOAD = dt["TEMPLATES_AUTO_RELOAD"]
            self.MAIL_SERVER = dt["MAIL_SERVER"]
            self.MAIL_PORT = dt["MAIL_PORT"]
            self.MAIL_USE_TLS = dt["MAIL_USE_TLS"] is True
            self.MAIL_USERNAME = dt["MAIL_USERNAME"]
            self.MAIL_PASSWORD = dt["MAIL_PASSWORD"]
            self.MAIL_DEFAULT_SENDER = dt["MAIL_DEFAULT_SENDER"]
            self.WTF_CSRF_ENABLED = dt["WTF_CSRF_ENABLED"] == "True"
            self.RECAPTCHA_PUBLIC_KEY = dt["RECAPTCHA_PUBLIC_KEY"]
            self.RECAPTCHA_PRIVATE_KEY = dt["RECAPTCHA_PRIVATE_KEY"]
            self.SENTRY_DSN = dt["SENTRY_DSN"]
            self.DEBUG = dt["DEBUG"] is True
            self.TESTING = dt["TESTING"] is True
            self.AMBUDA_BOT_PASSWORD = dt["AMBUDA_BOT_PASSWORD"]
            self.GOOGLE_APPLICATION_CREDENTIALS = dt["GOOGLE_APPLICATION_CREDENTIALS"]
            self.STATIC_DIR = dt["STATIC_DIR"]
            self.RAW_DATA_DIR = dt["RAW_DATA_DIR"]
            self.is_production = self.AMBUDA_ENVIRONMENT == PRODUCTION
            self.is_testing = self.AMBUDA_ENVIRONMENT == TESTING
            self.DATABASE_FILE = self.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')


def __validate_config(config: ContainerConfig):
    """Examine the given config and fail if the config is malformed.

    :param config: the config to test
    """
    assert config.AMBUDA_ENVIRONMENT in {
        TESTING,
        DEVELOPMENT,
        STAGING,
        PRODUCTION,
    }

    if not config.SQLALCHEMY_DATABASE_URI:
        raise ValueError("This config does not define SQLALCHEMY_DATABASE_URI")

    if not config.FLASK_UPLOAD_DIR:
        raise ValueError("This config does not define FLASK_UPLOAD_DIR.")

    if not os.path_is_absolute(config.FLASK_UPLOAD_DIR):
        raise ValueError("FLASK_UPLOAD_DIR must be an absolute path.")

    if not config.VIDYUT_DATA_DIR:
        print(
            "Error! VIDYUT_DATA_DIR is not set. Please set environment variable VIDYUT_DATA_DIR"
        )
        return False

    if not config.VIDYUT_DATA_URL:
        print(
            "Error! URL to fetch Vidyut data is not set. Please set environment variable VIDYUT_DATA_URL"
        )
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
        assert os.file_exists(google_creds)


def __get_container_config_from(type: str, file_path: str) -> ContainerConfig:
    if type not in [DEFAULT, TESTING, DEVELOPMENT, STAGING, PRODUCTION]:
        raise ValueError(f"Unknown container config type: {type}")

    de = __read_env_file("/app/deploy/envars/container.toml")[DEFAULT]
    ce = __read_env_file(file_path) if file_path else __read_env_file("/app/deploy/envars/container.toml")[type]
    e = __read_env(
        "container",
        de,
        ce,)
    return ContainerConfig(e)


def load_config_object(name: str):
    """Load and validate an application config."""
    config = __get_container_config_from(name, '')
    __validate_config(config)
    return config


def read_remote_host_config(section: str) -> RemoteHostConfig:
    file = f"{__get_host_data_dir()}/remote.toml"
    template = "deploy/envars/remote.toml.template"
    if not os.file_exists(file):
        logging.warning(f"{file} does not exist")
        print("Please create a TOML using the follow variables.")
        print("You can define multiple remote hosts each with a different [label]")
        print('# ambuda remote host config')
        print(os.read_file_as_string(template))
        os.exit(-1)
    e = __read_env(
        "remote",
        __read_env_file(template)['label'],
        __read_env_file(file)[section]
    )
    return RemoteHostConfig(e)


def read_host_config() -> HostConfig:
    return HostConfig(
        __get_host_data_dir(),
        git.current_branch(),
        git.head_sha(),
        "127.0.0.1",
        __read_env(
            "host",
            __read_env_file("deploy/envars/host.toml"),
            __read_env_file(f"{__get_host_data_dir()}/host.toml"),
        )
    )


def __read_container_config() -> ContainerConfig:
    config = __get_container_config_from(DEFAULT, CONTAINER_FILE_STD)
    __validate_config(config)
    return config


if __file__ == "/app/unstd/config.py" or os.file_exists("/app/unstd/config.py"):
    current = __read_container_config()
else:
    current = ContainerConfig(None)
