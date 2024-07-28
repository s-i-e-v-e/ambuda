#
# RUNS ON VPS/VM/LOCAL
#

import sys
import util
import podman
from gh import gh_generate_workflows
import i18n
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
        'i18n': i18n.generate,

        'gh': gh_generate_workflows,

        'build': podman.build, # build image
        'stage': podman.stage,  # stage container
        'inspect': podman.inspect,
        'kill': podman.kill,

        'help': _yrun.help
    }
    f = switch.get(cmd, _yrun.help)
    f(sys.argv)

# Generate Ambuda's technical documentation.
# After the command completes, open "docs/_build/index.html".

########	cd docs && make html


__main()
