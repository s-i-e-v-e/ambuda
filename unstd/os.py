import sys
import os
import shutil
import subprocess
from typing import List, Any


def random_string() -> str:
    import uuid

    return uuid.uuid4().__str__()


def copy(s, d):
    shutil.copytree(s, d, dirs_exist_ok=True)


def copy_file(s, d):
    xs = d.split(os.sep)
    xs.pop()
    os.makedirs(os.sep.join(xs), exist_ok=True)
    shutil.copyfile(s, d)


def read_file_as_string(p) -> str:
    with open(p, "r") as f:
        return f.read()


def write_file_as_string(p, data):
    with open(p, "w") as f:
        f.write(data)


def make_dir(p):
    os.makedirs(p, exist_ok=True)


def rmdir(d):
    shutil.rmtree(d, ignore_errors=True)


def cwd() -> str:
    return os.getcwd()


def run(xs, cwd: Any = None) -> bool:
    return subprocess.run(xs, cwd=cwd).returncode == 0


def rm(f):
    os.remove(f)


def file_exists(f) -> bool:
    return os.path.isfile(f)


def extract_file_name(f) -> str:
    xs = f.split(os.sep)
    return xs.pop()


def exit(code: int) -> None:
    sys.exit(code)


def xs_next(xs, default) -> str:
    x = xs[0] if len(xs) > 0 else default
    if len(xs) > 0:
        del xs[0]
    return x


def next_arg_pair(xs: List[str]):
    a = xs_next(xs, None)
    b = xs_next(xs, None) if a else None
    return a, b


def get_git_sha() -> str:
    p = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    )
    return p.stdout.strip()


def get_git_branch() -> str:
    p = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True
    )
    return p.stdout.strip()


def get_external_ip() -> str:
    # return requests.get('https://checkip.amazonaws.com').text.strip()
    x = subprocess.run(["ip", "route", "get", "1"], capture_output=True).stdout.decode(
        "utf-8"
    )
    return x.split(" ")[6]


def fix_venv():
    os.environ['PYTHONPATH'] = f"/venv/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"