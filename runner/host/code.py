from typing import List
from unstd import os








def __js_check():
    os.run(["npx", "tsc", "static/js/*.ts" "-noEmit"])


def __js_lint():
    os.run(
        ["npx", "eslint", "--fix", "static/js/*", "--ext", ".js,.ts"]
    )


def __py_lint_check():
    os.run(["black", ".", "--diff"])


def __py_lint():
    __py_lint_check()
    os.run(["ruff", ".", "-fix"])
    os.run(["black", "."])


def check(args: List[str]) -> None:
    print("Checking TYPES")
    __js_check()





def lint(args: List[str]) -> None:
    print("Linting JS + PY")
    __js_lint()
    __py_lint()
