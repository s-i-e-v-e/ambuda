def help():
    print("""
    ambuda runner v0.1
usage:
    ar gh               generate github workflows
    ar build            builds ambuda image
    ar stage            runs ambuda image in a container after initializing data
    ar container init   TO BE USED ONLY BY podman
    ar [help]           display this help message
""".strip())


def none():
    pass