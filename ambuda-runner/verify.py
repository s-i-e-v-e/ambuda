# Verifies that the local `.env` file is a is well-formed production config.
# NOTE: run this script in the production environment.
#

from ambuda.config import create_config_only_app
import util


def verify(args):
    ev = util.next_arg_pair(args)
    if ev[0] == '--env':
        if ev[1] in ['production', 'staging', 'development']:
            # Fails if config is malformed.
            app = create_config_only_app(ev[1])
        else:
            raise f"Unknown environment: {ev[1]}"