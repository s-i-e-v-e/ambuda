#
# RUNS ON CONTAINER WHEN DEPLOYMENT IS TRIGGERED
#
import sys
sys.path.extend(["./", "./ambuda", "./unstd"])

from typing import List, Callable, Dict

import unstd.os
import unstd.config
import _yrun
import db_initialize
import vidyut_initialize
import verify
from runner import code

cfg = unstd.config.read_container_config()


def __start():
    unstd.os.run(["redis-server", "--port", cfg.REDIS_PORT, "--daemonize", "yes"])
    unstd.os.run(["celery", "--app", "ambuda.tasks", "worker", "--detach", "--loglevel=INFO"])

    print("podman: FLASK START")
    print(f"{cfg.FLASK_ENV} Flask start @ {cfg.AMBUDA_CONTAINER_IP}:5000")

    if cfg.FLASK_ENV == "development":
        # Start flask server in development mode
        # Dynamically load css and js changes. Docker compose attaches to the ./static directory on localhost.
        unstd.os.run(
            [
                "npx",
                "concurrently",
                f"flask run -h {cfg.AMBUDA_CONTAINER_IP} -p 5000",
                "npx tailwindcss -i /app/static/css/style.css -o /app/static/gen/style.css --watch",
                "npx esbuild /app/static/js/main.js --outfile=/app/static/gen/main.js --bundle --watch",
            ]
        )
    else:
        # Build, Staging, and Production modes take this route. Load site static files that are within the container.
        unstd.os.run(
            [
                "npx",
                "concurrently",
                f"flask run -h {cfg.AMBUDA_CONTAINER_IP} -p 5000",
            ]
        )


def __init(args: List[str]) -> None:
    print("podman: INIT")
    seed_type = unstd.os.next_arg_pair(args)

    # Initialize SQLite database
    db_initialize.run(cfg, seed_type[1] if seed_type[0] == "--seed" else None)

    # Initialize Vidyut data
    vidyut_initialize.run(cfg)

    __start()


Dispatchable = Dict[str, Callable[[List[str]], None]]


def __main():
    unstd.os.fix_venv()
    del sys.argv[0]
    cmd = unstd.os.xs_next(sys.argv, "help")
    switch: Dispatchable = {
        "init": __init,
        "check": code.check,
        "test": code.test,
        "lint": code.lint,
        "verify": verify.verify,
        "help": _yrun.help,
    }
    f = switch.get(cmd, _yrun.none)
    f(sys.argv)


__main()
