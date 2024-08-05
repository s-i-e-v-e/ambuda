from typing import List
from runner import validate
from unstd import config, os


def __get_image_names(os_name: str, hc: config.HostConfig) -> tuple[str, str]:
    base = f"ambuda-{hc.GIT_BRANCH}-{os_name}"
    return f"{base}:{hc.AMBUDA_VERSION}-{hc.GIT_SHA}", f"{base}:latest"

cfg = config.read_host_config()
PODMAN_DIR = f"/{os.get_tmp_dir()}/podman"


def build(args: List[str]):
    os_name = validate.get_valid_os(args)
    ambuda_image, ambuda_image_latest = __get_image_names(os_name, cfg)
    print(f"podman: BUILDING {os_name}")

    os.make_dir(PODMAN_DIR)
    of = f"{PODMAN_DIR}/Containerfile"

    a = os.read_file_as_string(f"deploy/containers/Containerfile.{os_name}")
    b = os.read_file_as_string("deploy/containers/Containerfile.common")
    c = a + b
    c = c.replace("${OS_NAME}", os_name)
    os.write_file_as_string(of, c)
    os.run(
        [
            "podman",
            "build",
            "--tag",
            ambuda_image,
            "--tag",
            ambuda_image_latest,
            "-f",
            of,
            ".",
        ]
    )


def run(args: List[str]):
    os_name = validate.get_valid_os(args)
    ambuda_image, _ = __get_image_names(os_name, cfg)
    print(f"podman: RUNNING {os_name}")

    pod_file = f"/{PODMAN_DIR}/podman.yml"
    os.copy_file("deploy/containers/podman.yml", pod_file)

    # pass arguments to init script
    xs = ["/app/ar", "container", "init"]
    for a in args:
        xs.append(a)

    ys = [f'"{str(a)}"' for a in xs]
    cmd = f'[{", ".join(ys)}]'

    x = os.read_file_as_string(pod_file)
    x = x.replace("${AMBUDA_IMAGE}", ambuda_image)
    x = x.replace("${HOST_PORT}", str(cfg.HOST_PORT))
    x = x.replace("${HOST_IP}", cfg.HOST_IP)
    x = x.replace("${PWD}", os.cwd())
    x = x.replace("${CMD}", cmd)
    x = x.replace("${HOST_DATA_DIR}", cfg.HOST_DATA_DIR)

    os.write_file_as_string(pod_file, x)

    os.run(["podman", "kube", "down", pod_file])
    os.run(["podman", "kube", "play", pod_file])
    os.run(["podman", "logs", "-f", cfg.CONTAINER_NAME])


def inspect(args: List[str]):
    os.run(
        [
            "podman",
            "inspect",
            cfg.CONTAINER_NAME,
            "-f",
            "{{ .NetworkSettings.IPAddress }} {{ .NetworkSettings.Ports }}",
        ]
    )


def kill(args: List[str]):
    os.run(["podman", "kill", cfg.CONTAINER_NAME])


def destroy(args: List[str]):
    os.run(["podman", "image", "rm", "-a", "-f"])
    # kill(args)
    # unstd.os.run(['podman', 'pod', 'rm', '-a', '-f'])
    # unstd.os.run(['podman', 'container', 'rm', '-a', '-f'])


def copy_to(args: List[str]):
    s = args[0]
    d = args[1]
    os.run(["podman", "cp", s, f"{cfg.CONTAINER_NAME}:{d}"])


def exec(args: List[str]):
    xs = []
    xs.extend(["podman", "exec", cfg.CONTAINER_NAME, "/app/ar", "container"])
    xs.extend(args)
    os.run(xs)
