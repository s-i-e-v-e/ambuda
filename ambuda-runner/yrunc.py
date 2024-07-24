#
# RUNS ON CONTAINER WHEN DEPLOYMENT IS TRIGGERED
#

import util
import _yrun
import sys

AMBUDA_CONTAINER_IP="AMBUDA_CONTAINER_IP"
REDIS_PORT="REDIS_PORT"
FLASK_ENV="FLASK_ENV"

def __start():
    util.run(['redis-server', '--port', util.get_env(REDIS_PORT), '--daemonize', 'yes'])
    util.run(['celery', '-A', 'ambuda.tasks', 'worker', '--detach', '--loglevel=INFO'])

    print('podman: FLASK START')
    print(f"{util.get_env(FLASK_ENV)} Flask start from /venv/bin/flask with {util.get_env(AMBUDA_CONTAINER_IP)} on port 5000")

    if util.get_env(FLASK_ENV) == "development":
        # Start flask server in development mode
        # Dynamically load css and js changes. Docker compose attaches to the ambuda/static directory on localhost.
        util.run(['./node_modules/.bin/concurrently',
                  f"/venv/bin/flask run -h {util.get_env(AMBUDA_CONTAINER_IP)} -p 5000",
                  "npx tailwindcss -i /app/ambuda/static/css/style.css -o /app/ambuda/static/gen/style.css --watch",
                  "npx esbuild /app/ambuda/static/js/main.js --outfile=/app/ambuda/static/gen/main.js --bundle --watch"
                  ])
    else:
        # Build, Staging, and Production modes take this route. Load site static files that are within the container.
        util.run(['./node_modules/.bin/concurrently',
                  f"/venv/bin/flask run -h {util.get_env(AMBUDA_CONTAINER_IP)} -p 5000"
                  ])


def __init():
    print('podman: INIT')

    util.run(['sh', '/app/scripts/initialize_data.sh'])
    __start()


def __main():
    print(sys.argv)
    util.set_envars_from('deploy/env.container')
    del sys.argv[0]

    cmd = util.xs_next(sys.argv, 'help')

    print(cmd)
    switch = {
        'init': __init,

        'help': _yrun.help
    }
    f = switch.get(cmd, _yrun.none)
    f()


__main()
