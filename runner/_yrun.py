from typing import List


def help(args: List[str]) -> None:
    print(
        """
    ambuda runner v0.1
usage:
    ar gh                                       generate github workflows
    ar build [*alpine/arch/ubuntu]              build ambuda image base on alpine/arch/ubuntu
    ar stage [*alpine/arch/ubuntu] [--seed all] run ambuda image in a container after initializing data
    ar inspect                                  provide basic information on running container
    ar kill                                     shut down container
    ar destroy                                  CAREFUL!!! WILL DESTROY ALL containers and ALL images on the host machine
    ar container init                           TO BE USED ONLY BY podman
    ar container code check             
    ar container code test [--coverage]         Test code (optionally with coverage) 
    ar container code lint                      Lint code
    ar container code verify                    Verify envars match expected environment
                    [--env production
                           staging
                           development
                    ] 
    ar [help]                                   display this help message
""".strip()
    )


# TODO: babel
# TODO: cli


def none(args: List[str]) -> None:
    pass
