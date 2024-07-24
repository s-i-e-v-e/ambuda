#
# RUNS ON VPS/VM/LOCAL
#

import sys
import util
import podman
from gh import gh_generate_workflows
from remote import remote_exec
import _yrun

def __main():
    del sys.argv[0]

    cmd = util.xs_next(sys.argv, 'help')
    # is_remote = cmd == 'remotely'
    # del sys.argv[0]
    #
    # if is_remote:
    #     # command has to be executed on remote server
    #     cmd = util.xs_next(sys.argv, 'help')
    #     del sys.argv[0]
    #     print(f'will execute remotely: {cmd}')
    #     remote_exec(cmd)
    #     return 0
    # else:
    #     # command has to be executed locally
    #     pass

    switch = {
        #'gh': gh_generate_workflows,

        'build': podman.build, # build image
        'stage': podman.stage,  # stage container
        'inspect': podman.inspect,

        'help': _yrun.help
    }
    f = switch.get(cmd, _yrun.none)
    f()

__main()
