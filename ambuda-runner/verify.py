# Verifies that the local `.env` file is a is well-formed production config.
# NOTE: run this script in the production environment.
#

from ambuda.config import create_config_only_app

def production(args):
    # Fails if config is malformed.
    app = create_config_only_app("production")
