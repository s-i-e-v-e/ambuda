import sys
sys.path.extend(['./'])

from typing import List
from unstd import os
from host import code, podman
import help


def __spawn(args: List[str]):
    os.spawn(args)


def __main(args: List[str]) -> None:
    def verify(args):
        xs = []
        xs.append('verify')
        xs.extend(args)
        podman.exec(xs)

    del args[0]
    cmd = os.next_arg(args, "help")
    f = os.switch(cmd, help.none,
        {
            "build": podman.build,  # build image
            "run": podman.run,  # run container
            "inspect": podman.inspect,
            "destroy": podman.destroy,
            "kill": podman.kill,

            "check": code.check,
            "test": code.test,
            "lint": code.lint,
            "verify": verify,
            "spawn": __spawn,
            "user": lambda args: podman.exec(['user']),

            "copy-to": podman.copy_to,
            "help": help.run,
        })
    f(args)


__main(sys.argv)
