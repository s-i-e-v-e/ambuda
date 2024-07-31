import sys
import os
import shutil
import subprocess
from typing import List, Any


def random_string() -> str:
    import uuid

    return uuid.uuid4().__str__()


def copy(s: str, d: str):
    shutil.copytree(s, d, dirs_exist_ok=True)


def copy_file(s: str, d: str):
    dir_path = extract_dir_path(d)
    os.makedirs(dir_path, exist_ok=True)
    shutil.copyfile(s, d)


def read_file_as_string(p: str) -> str:
    with open(p, "r") as f:
        return f.read()


def write_file_as_string(p: str, data: str):
    with open(p, "w") as f:
        f.write(data)


def make_dir(p: str):
    os.makedirs(p, exist_ok=True)


def rmdir(d: str):
    shutil.rmtree(d, ignore_errors=True)


def cwd() -> str:
    return os.getcwd()


def run(xs: List[str], cwd: Any = None) -> bool:
    return subprocess.run(xs, cwd=cwd).returncode == 0


def rm(f: str):
    os.remove(f)


def file_exists(x: str) -> bool:
    return os.path.isfile(x)


def dir_exists(x: str) -> bool:
    return os.path.isdir(x)


def extract_file_name(x: str) -> str:
    xs = x.split(os.sep)
    return xs.pop()


def extract_dir_path(x: str) -> str:
    xs = x.split(os.sep)
    xs.pop()
    return os.sep.join(xs)


def exit(code: int) -> None:
    sys.exit(code)


def next_arg(xs: List[str], default: str) -> str:
    x = xs[0] if len(xs) > 0 else default
    if len(xs) > 0:
        del xs[0]
    return x


def next_arg_pair(xs: List[str]):
    a = next_arg(xs, '')
    b = next_arg(xs, '') if a else None
    return a, b

def is_next_arg_an_opt(xs: List[str]) -> bool:
    return xs[0].startswith('--') if len(xs) > 0 else False

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


def get_tmp_dir() -> str:
    return f"/tmp/{random_string()}"