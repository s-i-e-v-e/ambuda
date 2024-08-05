import sys
sys.path.extend(['./'])

from typing import List
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


def __build(remote: str, args: List[str]):
    def clone(remote: str):
        cmd = f"""
            rm -rf {REMOTE_CODE_DIR}
                mkdir -p {REMOTE_CODE_DIR} \
                && cd {REMOTE_CODE_DIR} \
                && git clone {GIT_URL} {REMOTE_CODE_DIR} \
                && cd {REMOTE_CODE_DIR} \
                && git switch podman
                """
        __exec(remote, [cmd])

    clone(remote)

    cmd = f"""
            cd {REMOTE_CODE_DIR} \
            && git switch podman \
            && ./ar build {' '.join(args)} \
            """
    __exec(remote, [cmd])


def __run(remote: str, args: List[str]):
    cmd = f"""
            cd {REMOTE_CODE_DIR} \
            && git switch podman \
            && ./ar run {' '.join(args)} \
            """
    __exec(remote, [cmd])


def __main(args: List[str]):
    print(f'RUNNING REMOTELY {' '.join(args[1:])}')
    del args[0]
    [remote, cmd] = os.next_arg_pair(args)
    f = os.switch(cmd, help.none,
                  {
                      "build": lambda args: __build(remote, args),
                      "run": lambda args: __run(remote, args),
                      "exec": lambda args: __exec(remote, args),
                  })
    f(args)


__main(sys.argv)