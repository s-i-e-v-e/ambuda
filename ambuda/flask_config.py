from flask import Flask
import unstd.config


def create_config_only_app(config_name: str):
    """Create the application with just its config options set.

    We use this function in Celery to get access to the app context while
    avoiding any other setup work related to the application.
    """
    app = Flask(__name__)
    app.config.from_object(unstd.config.load_config_object(config_name))
    return app
