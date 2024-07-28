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
    util.set_envars_from('/data/ambuda/builder.env', 'deploy/default.builder.env')
    image_name = f"ambuda-release:{util.get_env(AMBUDA_VERSION)}-{util.get_git_sha()}"
    util.set_env(AMBUDA_IMAGE, image_name)
    util.set_env(AMBUDA_IMAGE_LATEST, "ambuda-release:latest")
    util.set_env(AMBUDA_HOST_IP, util.get_external_ip())

def build():
    __env()
    print('podman: BUILD')

    util.run(['podman', 'build', '--tag', util.get_env(AMBUDA_IMAGE), '--tag', util.get_env(AMBUDA_IMAGE_LATEST), '-f', 'deploy/Containerfile', '.'])


def stage():
    __env()
    print('podman: STAGE')

    pod_file = f"/tmp/{util.random_string()}/podman.yml"
    util.copy_file('deploy/podman.yml', pod_file)

    x = util.read_file_as_string(pod_file)
    x = x.replace('${AMBUDA_IMAGE}', util.get_env(AMBUDA_IMAGE))
    x = x.replace('${AMBUDA_HOST_PORT}', util.get_env(AMBUDA_HOST_PORT))
    x = x.replace('${AMBUDA_HOST_IP}', util.get_env(AMBUDA_HOST_IP))
    x = x.replace('${PWD}', util.cwd())
    util.write_file_as_string(pod_file, x)

    util.run(['podman', 'kube', 'down', pod_file])
    util.run(['podman', 'kube', 'play', pod_file])

    print(f"Host: {util.get_env(AMBUDA_HOST_IP)}:{util.get_env(AMBUDA_HOST_PORT)}")
    util.run(['podman', 'logs', '-f', AMBUDA_CONTAINER_NAME])
    
def inspect():
    util.run(['podman', 'inspect', AMBUDA_CONTAINER_NAME, '-f', '{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}'])


def kill():
    util.run(['podman', 'kill', AMBUDA_CONTAINER_NAME])
