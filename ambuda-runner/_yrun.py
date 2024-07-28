def help(args):
    print("""
    ambuda runner v0.1
usage:
    ar gh                               generate github workflows
    ar build                            build ambuda image
    ar stage [--seed all]               run ambuda image in a container after initializing data
    ar inspect                          provide basic information on running container
    ar kill                             shut down container
    ar destroy                          destroy all containers and all images
    ar container init                   TO BE USED ONLY BY podman
    ar container code check             
    ar container code test [--coverage] Test code (optionally with coverage) 
    ar container code lint              Lint code
    ar container code verify            Verify envars match expected environment
                    [--env production
                           staging
                           development
                    ] 
    ar [help]                           display this help message
""".strip())

# TODO: babel
# TODO: cli


def none():
    pass