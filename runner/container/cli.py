from typing import List

from unstd import os
from runner.container import repo
#    ./cli.py create-project <project-title> <path-to-project-pdf>


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
