from typing import List
import sys
sys.path.extend(['./'])
from host import code, podman
import unstd.os as os
import help


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
            "stage": podman.stage,  # stage container
            "inspect": podman.inspect,
            "destroy": podman.destroy,
            "kill": podman.kill,

            "check": code.check,
            "test": code.test,
            "lint": code.lint,
            "verify": verify,
            "user": lambda args: podman.exec(['user']),

            "copy-to": podman.copy_to,
            "help": help.run,
        })
    f(args)


__main(sys.argv)
