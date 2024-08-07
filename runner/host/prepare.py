from typing import List, Callable, Optional

from unstd import os

PREPARE_CMD = ["sudo", "pacman", "-Syu", "git", "podman", "crun", "python", "python-yaml", "python-toml", "caddy"]


def run(args: List[str], remote_exec: Optional[Callable] = None) -> None:
    # ARE WE ON LOCAL HOST OR REMOTE HOST
    if remote_exec:
        # determine remote os
        os_name = remote_exec([os.OS_DETECTION], return_output=True)
        if os_name == "arch":
            remote_exec(PREPARE_CMD)
        else:
            raise Exception("Unsupported OS")

        reboot = os.is_next_arg_an_opt(args) and os.next_arg(args, '') == '--reboot'
        if reboot:
            remote_exec(["sudo", "reboot"])
    else:
        os_name = os.running_on()
        if os_name == 'arch':
            os.run(PREPARE_CMD)
        else:
            raise Exception("Unsupported OS")
