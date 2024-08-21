import sys
sys.path.extend(["./"])

from typing import List
from unstd import config, os
os.fix_venv('/ambuda/.venv')
from container import vidyut_initialize, db_initialize, verify, code_test, cli
from runner import help

cfg = config.current


def __start():
    print("podman: FLASK START")
    if not cfg.is_production:
        cli.user_add_default()

    print(f"{cfg.FLASK_ENV} Flask start @ {cfg.AMBUDA_CONTAINER_IP}:5000")
    os.run(["flask", "run", "-h", cfg.AMBUDA_CONTAINER_IP, "-p", "5000"])


def __init(args: List[str]) -> None:
    print("podman: INIT")
    seed_type = os.next_arg_pair(args)

    # Initialize SQLite database
    db_initialize.run(cfg, seed_type[1] if seed_type[0] == "--seed" else '')

    # Initialize Vidyut data
    vidyut_initialize.run(cfg)

    __start()


def __main(args: List[str]) -> None:
    del args[0]
    cmd = os.next_arg(args, "help")
    f = os.switch(cmd, help.none,
        {
            "init": __init,
            "verify": verify.verify,
            "test": code_test.test,
            "user": cli.user,
            "help": help.run,
        })
    f(args)


__main(sys.argv)
