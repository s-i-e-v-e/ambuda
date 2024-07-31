from typing import List

import unstd.os


def __js_test():
    unstd.os.run(["npx", "jest"])


def __js_test_coverage():
    unstd.os.run(["npx", "jest", "--coverage"])


def __py_test():
    unstd.os.run(["pytest", "."])


def __py_test_coverage():
    unstd.os.run(["pytest", "--cov=ambuda", "--cov-report=html", "test/"])
    unstd.os.run(["coverage", "report", "--fail-under=80"])


def __js_check():
    unstd.os.run(["npx", "tsc", "/app/static/js/*.ts" "-noEmit"])


def __js_lint():
    unstd.os.run(
        ["npx", "eslint", "--fix", "/app/static/js/*", "--ext" ".js,.ts"]
    )


def __py_lint_check():
    unstd.os.run(["black", ".", "--diff"])


def __py_lint():
    __py_lint_check()
    unstd.os.run(["ruff", ".", "-fix"])
    unstd.os.run(["black", "."])


def check(args: List[str]) -> None:
    print("Checking TYPES")
    __js_check()


def __test_with_coverage():
    print("Testing JS + PY with coverage reporting")
    __js_test_coverage()
    __py_test_coverage()


def test(args: List[str]) -> None:
    cv = unstd.os.xs_next(args, None)
    if cv == "--coverage":
        __test_with_coverage()
    else:
        print("Testing JS + PY")
        __js_test()
        __py_test()


def lint(args: List[str]) -> None:
    print("Linting JS + PY")
    __js_lint()
    __py_lint()
