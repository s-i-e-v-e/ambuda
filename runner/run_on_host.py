import sys
sys.path.extend(["./", "./ambuda", "./unstd"])

from host import podman
from unstd import os
import help


def __main():
    del sys.argv[0]

    cmd = os.next_arg(sys.argv, "help")
    # is_remote = cmd == 'remotely'
    # del sys.argv[0]
    #
    # if is_remote:
    #     # command has to be executed on remote server
    #     cmd = unstd.os.xs_next(sys.argv, 'help')
    #     del sys.argv[0]
    #     print(f'will execute remotely: {cmd}')
    #     remote_exec(cmd)
    #     return 0
    # else:
    #     # command has to be executed locally
    #     pass
    switch = {
        "build": podman.build,  # build image
        "stage": podman.stage,  # stage container
        "inspect": podman.inspect,
        "destroy": podman.destroy,
        "kill": podman.kill,
        "copy-to": podman.copy_to,
        "help": help.run,
    }
    f = switch.get(cmd, help.run)
    f(sys.argv)


__main()
