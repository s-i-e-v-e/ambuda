import getpass
from typing import List
from unstd import os
from runner.host import podman

def __ui_user_add() -> None:
    name = input("Username: ")
    password = getpass.getpass("Password: ")
    email = input("Email: ")
    podman.exec(["user", "add", name, password, email])
    print("User created successfully.")


def __ui_role_add() -> None:
    name = input("Username: ")
    role = input("Role: ")
    podman.exec(["user", "role", "add", name, role])
    print(f"User role added successfully. {name} is {role}")


def run(args: List[str]) -> None:
    cmd = os.next_arg(args, '')
    if cmd == 'add':
        __ui_user_add()
    elif cmd == 'role':
        cmd = os.next_arg(args, '')
        if cmd == 'add':
            __ui_role_add()
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
