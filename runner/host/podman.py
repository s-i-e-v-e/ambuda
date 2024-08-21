import json
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
    xs = ["/ambuda/app/ar", "container", "init"]
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
    x = os.run_with_string_output(
        [
            "podman",
            "inspect",
            cfg.CONTAINER_NAME,
        ]
    )
    ci = json.loads(x)[0]
    ci_oci = f"{ci['OCIRuntime']} [oci_version: {ci['State']['OciVersion']}]"
    ci_ports = []
    ci_ns_ports = ci['NetworkSettings']['Ports']
    for k in ci_ns_ports:
        protocol = k.split('/')[1]
        for x in ci_ns_ports[k]:
            ci_ports.append(f"{x['HostIp']}:{x['HostPort']}/{protocol}")

    print('Container Information')
    print('---------------------')
    print(f"Name: {ci['Name']}")
    print(f"ID: {ci['Id']}")
    print(f"Created: {ci['Created']}")
    print(f"Started: {ci['State']['StartedAt']}")
    print(f"OCI: {ci_oci}")
    print(f"FS Driver: {ci['Driver']}")
    print(f"Host Name: {ci['Config']['Hostname']}")
    print(f"Domain Name: {ci['Config']['Domainname']}")
    print(f"IP Addr: {ci['NetworkSettings']['IPAddress']}")
    print("Ports:")
    for p in ci_ports:
        print(f"  {p}")


def kill(args: List[str]):
    print(f"Shutting down container: {cfg.CONTAINER_NAME}")
    os.run(["podman", "kill", cfg.CONTAINER_NAME])


def destroy(args: List[str]):
    y = input(f"\nThis operation CANNOT be reversed. Are you sure that you wish to\nDELETE ALL containers, ALL pods and ALL images from this system.\nIf yes, please type 'DESTROY' to continue: ")
    if y == "DESTROY":
        os.run(["podman", "image", "rm", "-a", "-f"])
        print('All containers, pods and images have been deleted from this system')
    else:
        print('No harm done')


def copy_to(args: List[str]):
    s = args[0]
    d = args[1]
    os.run(["podman", "cp", s, f"{cfg.CONTAINER_NAME}:{d}"])


def exec(args: List[str]):
    xs = []
    xs.extend(["podman", "exec", cfg.CONTAINER_NAME, "/ambuda/app/ar", "container"])
    xs.extend(args)
    os.run(xs)
