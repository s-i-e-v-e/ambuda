import sys
from typing import List

sys.path.extend(["./", "./unstd"])
import unstd.os

REPO = "https://github.com/ambuda-org/ambuda-i18n.git"


def __fetch_git_repo(url: str, path: str):
    """Fetch the latest version of the given repo."""
    if not unstd.os.file_exists(path):
        unstd.os.make_dir(path)
        unstd.os.run(["git", "clone", "--branch=main", url, path])

    unstd.os.run(["git", "fetch", "origin"], cwd=path)
    unstd.os.run(["git", "checkout", "main"], cwd=path)
    unstd.os.run(["git", "reset", "--hard", "origin/main"], cwd=path)


def __compile_translations(path: str):
    unstd.os.run(["pybabel", "compile", "-d", path, "-f"])


def __copy_translation_files(src_dir: str, dest_dir: str):
    unstd.os.copy(src_dir, dest_dir)


def generate(args: List[str]):
    git_dir = "/tmp/ambuda-i18n"
    __fetch_git_repo(REPO, git_dir)

    src_dir = git_dir + "/translations"
    __compile_translations(src_dir)

    dest_dir = "/app/ambuda/translations"

    unstd.os.make_dir(dest_dir)
    __copy_translation_files(src_dir, dest_dir)


generate([])