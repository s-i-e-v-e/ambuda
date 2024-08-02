from typing import List, Callable, Dict
import sys
sys.path.extend(["./", "./ambuda", "./unstd"])

from unstd import config, os
os.fix_venv()
from container import vidyut_initialize, db_initialize, verify, code
import help

cfg = config.read_container_config()


def __start():
    os.run(["redis-server", "--port", cfg.REDIS_PORT, "--daemonize", "yes"])
    os.run(["celery", "--app", "ambuda.tasks", "worker", "--detach", "--loglevel=INFO"])

    print("podman: FLASK START")
    print(f"{cfg.FLASK_ENV} Flask start @ {cfg.AMBUDA_CONTAINER_IP}:5000")

    if cfg.FLASK_ENV == "development":
        # Start flask server in development mode
        # Dynamically load css and js changes. Docker compose attaches to the ./static directory on localhost.
        os.run(
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
        os.run(
            [
                "flask", "run", "-h", cfg.AMBUDA_CONTAINER_IP, "-p", "5000",
            ]
        )


def __init(args: List[str]) -> None:
    print("podman: INIT")
    seed_type = os.next_arg_pair(args)

    # Initialize SQLite database
    db_initialize.run(cfg, seed_type[1] if seed_type[0] == "--seed" else '')

    # Initialize Vidyut data
    vidyut_initialize.run(cfg)

    __start()


Dispatchable = Dict[str, Callable[[List[str]], None]]


def __main():
    del sys.argv[0]
    cmd = os.next_arg(sys.argv, "help")
    switch: Dispatchable = {
        "init": __init,
        "check": code.check,
        "test": code.test,
        "lint": code.lint,
        "verify": verify.verify,
        "help": help.run,
    }
    f = switch.get(cmd, help.none)
    f(sys.argv)


__main()
