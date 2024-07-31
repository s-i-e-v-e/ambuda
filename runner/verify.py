# Verifies that the local `.env` file is a well-formed production config.
# NOTE: run this script in the production environment.
#

from typing import List
from ambuda.flask_config import create_config_only_app
import unstd.os
from unstd import config


def verify(args: List[str]):
    e, v = unstd.os.next_arg_pair(args)
    if e == "--env":
        if v in [config.PRODUCTION, config.STAGING, config.DEVELOPMENT]:
            # Fails if config is malformed.
            app = create_config_only_app(v)
        else:
            raise Exception(f"Unknown environment: {v}")
