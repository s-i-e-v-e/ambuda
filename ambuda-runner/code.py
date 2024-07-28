import util

def __js_test():
    util.run(["npx", "jest"])


def __js_test_coverage():
    util.run(["npx", "jest", "--coverage"])


def __py_test():
    util.run(["pytest", "."])


def __py_test_coverage():
    util.run(["pytest", "--cov=ambuda", "--cov-report=html", "test/"])
    util.run(["coverage", "report", "--fail-under=80"])


def __js_check():
    util.run(["npx", "tsc", "/app/ambuda/static/js/*.ts" "-noEmit"])


def __js_lint():
    util.run(["npx", "eslint", "--fix", "/app/ambuda/static/js/*", "--ext" ".js,.ts"])


def __py_lint_check():
    util.run(["black", ".", "--diff"])


def __py_lint():
    __py_lint_check()
    util.run(["ruff", ".", "-fix"])
    util.run(["black", "."])


def check(args):
    print("Checking TYPES")
    __js_check()


def __test_with_coverage():
    print("Testing JS + PY with coverage reporting")
    __js_test_coverage()
    __py_test_coverage()


def test(args):
    cv = util.xs_next(args, None)
    if cv == '--coverage':
        __test_with_coverage()
    else:
        print("Testing JS + PY")
        __js_test()
        __py_test()


def lint(args):
    print("Linting JS + PY")
    __js_lint()
    __py_lint()