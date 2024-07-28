import shutil
import subprocess
from pathlib import Path
import util
REPO = "https://github.com/ambuda-org/ambuda-i18n.git"

def __fetch_git_repo(url: str, path: Path):
    """Fetch the latest version of the given repo."""
    if not path.exists():
        subprocess.run(f"mkdir -p {path}", shell=True)
        subprocess.run(f"git clone --branch=main {url} {path}", shell=True)

    subprocess.call("git fetch origin", shell=True, cwd=path)
    subprocess.call("git checkout main", shell=True, cwd=path)
    subprocess.call("git reset --hard origin/main", shell=True, cwd=path)


def __compile_translations(path: Path):
    subprocess.call(f"pybabel compile -d {path} -f", shell=True, stderr=subprocess.DEVNULL)


def __copy_translation_files(src_dir: Path, dest_dir: Path):
    shutil.copytree(str(src_dir), str(dest_dir), dirs_exist_ok=True)


def generate():
    git_dir = Path("/tmp/ambuda-i18n")
    __fetch_git_repo(REPO, git_dir)

    src_dir = git_dir / "translations"
    __compile_translations(src_dir)

    dest_dir = "/app/ambuda/translations"

    util.make_dir(dest_dir)
    __copy_translation_files(src_dir, dest_dir)

    print("Done.")