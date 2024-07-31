#
# Podman images and containers/pods
#
import os
from typing import List
import unstd.os
import unstd.config
import c_install

cfg = unstd.config.read_host_config()

def __get_image_names(os_name: str, cfg: unstd.config.HostConfig) -> List[str]:
    base = f"ambuda-{cfg.GIT_BRANCH}-{os_name}"
    return [
        f"{base}:{cfg.AMBUDA_VERSION}-{cfg.GIT_SHA}",
        f"{base}:latest",
    ]

def __get_valid_os(args: List[str]):
    os_name = "" if unstd.os.is_next_arg_an_opt(args) else unstd.os.next_arg(args, "")
    os_name = os_name if os_name else "alpine"
    if not c_install.is_valid_os(os_name):
        print(f'Unsupported OS: {os_name}')
        unstd.os.exit(1)
    return os_name


def build(args: List[str]):
    os_name = __get_valid_os(args)
    [AMBUDA_IMAGE, AMBUDA_IMAGE_LATEST] = __get_image_names(os_name, cfg)
    print(f"podman: BUILDING {os_name}")

    of = "/tmp/podman/Containerfile"
    a = unstd.os.read_file_as_string(f"deploy/Containerfile.{os_name}")
    b = unstd.os.read_file_as_string("deploy/Containerfile.common")
    c = a + b
    c = c.replace("${OS_NAME}", os_name)
    unstd.os.write_file_as_string(of, c)
    unstd.os.run(
        [
            "podman",
            "build",
            "--tag",
            AMBUDA_IMAGE,
            "--tag",
            AMBUDA_IMAGE_LATEST,
            "-f",
            of,
            ".",
        ]
    )


def stage(args: List[str]):
    os_name = __get_valid_os(args)
    [AMBUDA_IMAGE, AMBUDA_IMAGE_LATEST] = __get_image_names(os_name, cfg)
    print(f"podman: STAGING {os_name}")

    pod_file = f"/tmp/podman/{unstd.os.random_string()}.yml"
    unstd.os.copy_file("deploy/podman.yml", pod_file)

    # pass arguments to init script
    xs = ["/app/ar", "container", "init"]
    for a in args:
        xs.append(a)

    ys = [f'"{str(a)}"' for a in xs]
    cmd = f'[{", ".join(ys)}]'

    x = unstd.os.read_file_as_string(pod_file)
    x = x.replace("${AMBUDA_IMAGE}", AMBUDA_IMAGE)
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
