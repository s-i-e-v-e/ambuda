# Verifies that the local `.env` file is a is well-formed production config.
# NOTE: run this script in the production environment.
#

from typing import List
from ambuda.flask_config import create_config_only_app
import unstd.os


def verify(args: List[str]):
    ev = unstd.os.next_arg_pair(args)
    if ev[0] == "--env":
        if ev[1] in ["production", "staging", "development"]:
            # Fails if config is malformed.
            app = create_config_only_app(ev[1])
        else:
            raise Exception(f"Unknown environment: {ev[1]}")
