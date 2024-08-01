from unstd import os

def head_sha() -> str:
    return os.run_with_string_output(["git", "rev-parse", "--short", "HEAD"])


def current_branch() -> str:
    return os.run_with_string_output(["git", "branch", "--show-current"])