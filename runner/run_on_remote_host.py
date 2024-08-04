import re
from typing import List
import sys
sys.path.extend(["./", "./ambuda", "./unstd"])
from unstd import config, os
import help

REMOTE_CODE_DIR = "/tmp/ambuda"
GIT_URL = "https://github.com/s-i-e-v-e/ambuda"

def __exec(remote: str, args: List[str]):
    cfg = config.read_remote_host_config(remote)
    xs = []
    xs.extend([
        "ssh",
        f"-p{cfg.REMOTE_PORT}",
        "-i",
        cfg.SSH_KEY_OR_FILE,
        f"{cfg.REMOTE_USER}@{cfg.REMOTE_HOST}"
    ])
    xs.extend(args)
    print(" ".join(xs))
    os.run(xs)


def __setup(remote: str):
    cmd = f"""
        rm -rf {REMOTE_CODE_DIR}
            mkdir -p {REMOTE_CODE_DIR} \
            && cd {REMOTE_CODE_DIR} \
            && git clone {GIT_URL} {REMOTE_CODE_DIR} \
            && cd {REMOTE_CODE_DIR} \
            && git switch podman
            """
    __exec(remote, [cmd])


def __build(remote: str):
    cmd = f"""
            cd {REMOTE_CODE_DIR} \
            && git switch podman \
            && ./ar build
            """
    __exec(remote, [cmd])


def __stage(remote: str):
    cmd = f"""
            cd {REMOTE_CODE_DIR} \
            && git switch podman \
            && ./ar stage
            """
    __exec(remote, [cmd])


def __run(args: List[str]):
    print(f'RUNNING REMOTELY {' '.join(args[1:])}')
    del args[0]
    [cmd, remote] = os.next_arg(args, "help").split(':')
    f = os.switch(cmd, help.none,
                  {
                      "build": lambda args: __build(remote),
                      "stage": lambda args: __stage(remote),
                      "setup": lambda args: __setup(remote),
                      "exec": lambda args: __exec(remote, args),
                  })
    f(args)


__run(sys.argv)