from typing import List

from unstd import os
from runner.container import repo

DEFAULT_USER = "ambuda"
DEFAULT_USER_PASS = f"{DEFAULT_USER}00"
DEFAULT_USER_EMAIL = f"{DEFAULT_USER}@ambuda.org"

def user_add_default() -> None:
    if not repo.user_exists(DEFAULT_USER, DEFAULT_USER_EMAIL):
        repo.user_add(DEFAULT_USER, DEFAULT_USER_PASS, DEFAULT_USER_EMAIL)
        repo.role_add(DEFAULT_USER, "admin")
        repo.role_add(DEFAULT_USER, "p2")


def __user_add(args: List[str]) -> None:
    name = os.next_arg(args, '')
    password = os.next_arg(args, '')
    email = os.next_arg(args, '')
    repo.user_add(name, password, email)


def __user_role_add(args: List[str]) -> None:
    name = os.next_arg(args, '')
    role = os.next_arg(args, '')
    repo.role_add(name, role)


def user(args: List[str]) -> None:
    print(args)
    cmd = os.next_arg(args, '')
    if cmd == 'add':
        __user_add(args)
    elif cmd == 'role':
        cmd = os.next_arg(args, '')
        if cmd == 'add':
            __user_role_add(args)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
