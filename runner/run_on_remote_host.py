import sys
sys.path.extend(['./'])

from typing import List, Optional
from unstd import config, os
from runner import help
from runner.host import prepare

REMOTE_CODE_DIR = "/tmp/ambuda"
GIT_URL = "https://github.com/s-i-e-v-e/ambuda"


def __exec(remote: str, args: List[str], return_output=False) -> Optional[str]:
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
    if return_output:
        return os.run_with_string_output(xs)
    else:
        os.run(xs)


def __switch_and_exec(remote: str, cmd_text: str):
    cmd = f"""
            cd {REMOTE_CODE_DIR} \
            && {cmd_text}
            """
    __exec(remote, [cmd])


def __clone_repo(remote: str, args=None):
    cmd = f"""
        rm -rf {REMOTE_CODE_DIR} \
        && mkdir -p {REMOTE_CODE_DIR} \
        && cd {REMOTE_CODE_DIR} \
        && git clone {GIT_URL} {REMOTE_CODE_DIR} \
        && cd {REMOTE_CODE_DIR} \
        && git switch podman
    """
    __exec(remote, [cmd])


def __prepare(remote: str, args: List[str]):
    def exec(args: List[str], return_output = False):
        return __exec(remote, args, return_output)

    prepare.run(args, exec)


def __build(remote: str, args: List[str]):
    __clone_repo(remote)

    cmd = f"""
        ./ar build {' '.join(args)}
    """
    __switch_and_exec(remote, cmd)


def __run(remote: str, args: List[str]):
    __exec(remote, ["pkill caddy"])
    cmd = f"""
        ./ar spawn sudo caddy reverse-proxy --from :80 --to :5000 \
        && ./ar run {' '.join(args)}
    """
    __switch_and_exec(remote, cmd)


def __inspect(remote: str, args: List[str]):
    cmd = f"""
        ./ar inspect {' '.join(args)}
    """
    __switch_and_exec(remote, cmd)


def __destroy(remote: str, args: List[str]):
    cmd = f"""
        ./ar destroy {' '.join(args)}
    """
    __switch_and_exec(remote, cmd)


def __kill(remote: str, args: List[str]):
    cmd = f"""
        ./ar kill {' '.join(args)}
    """
    __switch_and_exec(remote, cmd)


def __main(args: List[str]):
    print(f'RUNNING REMOTELY {' '.join(args[1:])}')
    del args[0]
    remote, cmd = os.next_arg_pair(args)
    f = os.switch(cmd, help.none,
                  {
                      "clone": lambda args: __clone_repo(remote, args),
                      "exec": lambda args: __exec(remote, args),

                      "prepare": lambda args: __prepare(remote, args),
                      "build": lambda args: __build(remote, args),
                      "run": lambda args: __run(remote, args),

                      "inspect": lambda args: __inspect(remote, args),
                      "kill": lambda args: __kill(remote, args),
                      "destroy": lambda args: __destroy(remote, args),
                  })
    f(args)


__main(sys.argv)