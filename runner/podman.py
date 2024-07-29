#
# Podman images and containers/pods
#
from typing import List

import unstd.os
import unstd.config

cfg = unstd.config.read_host_config()


def build(args: List[str]):
    print("podman: BUILD")

    unstd.os.run(
        [
            "podman",
            "build",
            "--tag",
            cfg.AMBUDA_IMAGE,
            "--tag",
            cfg.AMBUDA_IMAGE_LATEST,
            "-f",
            "deploy/Containerfile",
            ".",
        ]
    )


def stage(args: List[str]):
    print("podman: STAGE")

    pod_file = f"/tmp/{unstd.os.random_string()}/podman.yml"
    unstd.os.copy_file("deploy/podman.yml", pod_file)

    xs = ["/app/ar", "container", "init"]
    for a in args:
        xs.append(a)

    ys = [f'"{str(a)}"' for a in xs]
    cmd = f'[{", ".join(ys)}]'

    x = unstd.os.read_file_as_string(pod_file)
    x = x.replace("${AMBUDA_IMAGE}", cfg.AMBUDA_IMAGE)
    x = x.replace("${AMBUDA_HOST_PORT}", str(cfg.AMBUDA_HOST_PORT))
    x = x.replace("${AMBUDA_HOST_IP}", cfg.AMBUDA_HOST_IP)
    x = x.replace("${PWD}", unstd.os.cwd())
    x = x.replace("${CMD}", cmd)
    unstd.os.write_file_as_string(pod_file, x)

    unstd.os.run(["podman", "kube", "down", pod_file])
    unstd.os.run(["podman", "kube", "play", pod_file])
    unstd.os.run(["podman", "logs", "-f", cfg.AMBUDA_CONTAINER_NAME])


def inspect(args: List[str]):
    unstd.os.run(
        [
            "podman",
            "inspect",
            cfg.AMBUDA_CONTAINER_NAME,
            "-f",
            "{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}",
        ]
    )


def kill(args: List[str]):
    unstd.os.run(["podman", "kill", cfg.AMBUDA_CONTAINER_NAME])


def destroy(args: List[str]):
    unstd.os.run(["podman", "image", "rm", "-a", "-f"])
    # kill(args)
    # unstd.os.run(['podman', 'pod', 'rm', '-a', '-f'])
    # unstd.os.run(['podman', 'container', 'rm', '-a', '-f'])


def copy_to(args: List[str]):
    s = args[0]
    d = args[1]
    unstd.os.run(["podman", "cp", s, f"{cfg.AMBUDA_CONTAINER_NAME}:{d}"])
