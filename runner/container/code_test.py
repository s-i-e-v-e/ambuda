from typing import List

from unstd import os


def __js_test():
    os.run(["npx", "jest"])


def __js_test_coverage():
    os.run(["npx", "jest", "--coverage"])


def __py_test():
    os.run(["pytest", "."])


def __py_test_coverage():
    os.run(["pytest", "--cov=ambuda", "--cov-report=html", "test/"])
    os.run(["coverage", "report", "--fail-under=80"])


def __test_with_coverage():
    print("Testing JS + PY with coverage reporting")
    __js_test_coverage()
    __py_test_coverage()


def test(args: List[str]) -> None:
    cv = os.next_arg(args, '')
    if cv == "--coverage":
        __test_with_coverage()
    else:
        print("Testing JS + PY")
        __js_test()
        __py_test()