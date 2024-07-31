#
# RUNS ON VPS/VM/LOCAL
#
import sys
sys.path.extend(["./", "./ambuda", "./unstd"])

import podman
import _yrun
import unstd.os


def __main():
    del sys.argv[0]

    cmd = unstd.os.next_arg(sys.argv, "help")
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
        "help": _yrun.help,
    }
    f = switch.get(cmd, _yrun.help)
    f(sys.argv)


# Generate Ambuda's technical documentation.
# After the command completes, open "docs/_build/index.html".

########	cd docs && make html


__main()
