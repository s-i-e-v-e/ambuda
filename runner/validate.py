from typing import List
from container import install
from unstd import os


def get_valid_os(args: List[str]):
    os_name = "" if os.is_next_arg_an_opt(args) else os.next_arg(args, "")
    os_name = os_name if os_name else "alpine"
    if not install.is_valid_os(os_name):
        print(f'Unsupported OS: {os_name}')
        os.exit(1)
    return os_name
