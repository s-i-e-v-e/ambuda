from typing import List
from unstd import os

# TODO: babel
# TODO: cli


def run(args: List[str]) -> None:
    print(
        f"""
ambuda runner v0.1
running on:{os.running_on()}
usage:
    ar [help]                                   display this help message
    ar gh                                       generate github workflows

    HOST
    ----
    ar build [*alpine/arch/ubuntu]              build ambuda image base on alpine/arch/ubuntu
    ar run   [*alpine/arch/ubuntu] [--seed all] run ambuda image in a container after initializing data
    ar inspect                                  provide basic information on running container
    ar kill                                     shut down container
    ar destroy                                  CAREFUL!!! WILL DESTROY ALL containers and ALL images on the host machine

    REMOTE HOST (as defined in remote.toml)
    -----------
    ar remote <host> <command>                  Execute command (see HOST section) on remote host
    ar remote <host> exec <command>             Execute adhoc command on remote host
    
    CONTAINER
    ---------
    ar container init                           TO BE USED ONLY BY podman
    ar container code check             
    ar container code test [--coverage]         Test code (optionally with coverage) 
    ar container code lint                      Lint code
    ar container code verify                    Verify envars match expected environment
                    [--env production
                           staging
                           development
                    ]
""".strip()
    )


def none(args: List[str]) -> None:
    print('Unknown argument')
