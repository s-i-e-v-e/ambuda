#
# Podman images and containers/pods
#

import util
AMBUDA_VERSION="AMBUDA_VERSION"
AMBUDA_IMAGE="AMBUDA_IMAGE"
AMBUDA_IMAGE_LATEST="AMBUDA_IMAGE_LATEST"
AMBUDA_HOST_IP="AMBUDA_HOST_IP"
AMBUDA_HOST_PORT="AMBUDA_HOST_PORT"

AMBUDA_CONTAINER_NAME="deploy-ambuda"
def __env():
    util.set_envars_from('/data/ambuda/host.env', 'deploy/default.host.env')
    image_name = f"ambuda-release:{util.get_env(AMBUDA_VERSION)}-{util.get_git_sha()}"
    util.set_env(AMBUDA_IMAGE, image_name)
    util.set_env(AMBUDA_IMAGE_LATEST, "ambuda-release:latest")
    util.set_env(AMBUDA_HOST_IP, util.get_external_ip())

def build(args):
    __env()
    print('podman: BUILD')

    util.run(['podman', 'build', '--tag', util.get_env(AMBUDA_IMAGE), '--tag', util.get_env(AMBUDA_IMAGE_LATEST), '-f', 'deploy/Containerfile', '.'])


def stage(args):
    __env()
    print('podman: STAGE')

    pod_file = f"/tmp/{util.random_string()}/podman.yml"
    util.copy_file('deploy/podman.yml', pod_file)

    xs = ["/app/ar", "container", "init"]
    for a in args:
        xs.append(a)

    ys = [f'"{str(a)}"' for a in xs]
    cmd = f'[{", ".join(ys)}]'

    x = util.read_file_as_string(pod_file)
    x = x.replace('${AMBUDA_IMAGE}', util.get_env(AMBUDA_IMAGE))
    x = x.replace('${AMBUDA_HOST_PORT}', util.get_env(AMBUDA_HOST_PORT))
    x = x.replace('${AMBUDA_HOST_IP}', util.get_env(AMBUDA_HOST_IP))
    x = x.replace('${PWD}', util.cwd())
    x = x.replace('${CMD}', cmd)
    util.write_file_as_string(pod_file, x)

    util.run(['podman', 'kube', 'down', pod_file])
    util.run(['podman', 'kube', 'play', pod_file])

    print(f"Host: {util.get_env(AMBUDA_HOST_IP)}:{util.get_env(AMBUDA_HOST_PORT)}")
    util.run(['podman', 'logs', '-f', AMBUDA_CONTAINER_NAME])
    
def inspect(args):
    util.run(['podman', 'inspect', AMBUDA_CONTAINER_NAME, '-f', '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'])


def kill(args):
    util.run(['podman', 'kill', AMBUDA_CONTAINER_NAME])


def destroy(args):
    util.run(['podman', 'image', 'rm', '-a', '-f'])
    #kill(args)
    #util.run(['podman', 'pod', 'rm', '-a', '-f'])
    #util.run(['podman', 'container', 'rm', '-a', '-f'])
