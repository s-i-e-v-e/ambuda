import sys
sys.path.extend(['./'])

from typing import List
from unstd import os
from host import code, podman, user
import help
from runner.host import prepare


def __spawn(args: List[str]):
    os.spawn(args)


def __main(args: List[str]) -> None:
    def verify(args):
        xs = []
        xs.append('verify')
        xs.extend(args)
        podman.exec(xs)

    def test(args):
        xs = []
        xs.append('test')
        xs.extend(args)
        podman.exec(xs)

    del args[0]
    cmd = os.next_arg(args, "help")
    f = os.switch(cmd, help.none,
        {
            "prepare": prepare.run,

            "build": podman.build,  # build image
            "run": podman.run,  # run container
            "inspect": podman.inspect,
            "destroy": podman.destroy,
            "kill": podman.kill,

            "check": code.check,
            "test": test,
            "lint": code.lint,
            "verify": verify,
            "spawn": __spawn,
            "user": user.run,

            "copy-to": podman.copy_to,
            "help": help.run,
        })
    f(args)


__main(sys.argv)
