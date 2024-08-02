from typing import List
import sys
sys.path.extend(["./", "./ambuda", "./unstd"])
from unstd import config, os
import help

REMOTE_DIR = "/tmp/ambuda"
GIT_URL = "https://github.com/s-i-e-v-e/ambuda"
cfg = config.read_remote_host_config()

def __exec(args: List[str]):
    xs = []
    xs.extend([
        "ssh",
        f"-p{cfg.REMOTE_PORT}",
        #"-o",
        #"UserKnownHostsFile " + HOST_FILE,
        "-i",
        cfg.SSH_KEY_OR_FILE,
        f"{cfg.REMOTE_USER}@{cfg.REMOTE_HOST}"
    ])
    xs.extend(args)
    print(" ".join(xs))
    os.run(xs)


def __setup(args: List[str]):
    cmd = f"""
        rm -rf {REMOTE_DIR}
            mkdir -p {REMOTE_DIR} \
            && cd {REMOTE_DIR} \
            && git clone {GIT_URL} {REMOTE_DIR} \
            && cd {REMOTE_DIR} \
            && git switch podman
            """
    __exec([cmd])


def __build(args: List[str]):
    cmd = f"""
            cd {REMOTE_DIR} \
            && git switch podman \
            && ./ar build
            """
    __exec([cmd])


def __stage(args: List[str]):
    cmd = f"""
            cd {REMOTE_DIR} \
            && git switch podman \
            && ./ar stage
            """
    __exec([cmd])


def __run(args: List[str]):
    print(f'RUNNING REMOTELY {' '.join(args[1:])}')
    del args[0]
    cmd = os.next_arg(args, "help")
    f = os.switch(cmd, help.none,
                  {
                      "build": __build,
                      "stage": __stage,
                      "setup": __setup,
                      "exec": __exec,
                  })
    f(args)


__run(sys.argv)