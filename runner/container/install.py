from os import path
import sys
from typing import List
sys.path.extend(["./", "./unstd"])
import pathlib
for p in sys.path:
    print(pathlib.Path(p).resolve())

import yaml
import unstd.os

def __do_filter(xs, name):
    ys = [a[name] if a.get(name) else '' for a in xs]
    return list(filter(lambda a: a, ys))


def __normalize(x: str, k: str) -> str:
    y = x
    if len(x.split('@')) == 2:
        x = x.replace('@', k)
    elif len(x.split('$')) == 2:
        x = x.replace('$', k).replace('.', '-').replace('_', '-')
    else:
        pass
    return x


os_pm = {
    'alpine' : ["apk", "add", "--no-cache"],
    'arch' : ["pacman", "-S", "--noconfirm"],
    'ubuntu' : ["apt-get", "install", "--yes"],
}


def __collect(d, k, os_name, packages, pip):
    for o in d.get(k):
        for k in o:
            xs = o[k]
            if not len(xs):
                # no entries. key is package name
                packages.append(k)
            else:
                ys = __do_filter(xs, os_name)
                if not len(ys):
                    # no entry for os. use pip
                    ys = __do_filter(xs, 'py')
                    if not len(ys):
                        raise ValueError(f'Package not found: {k}')
                    else:
                        pip.append(__normalize(ys[0], k))
                else:
                    packages.append(__normalize(ys[0], k))


def __install_on_os(os_name):
    pip = []
    packages = []
    with open('deploy/deps.runtime.yml', 'r') as f:
        d = yaml.safe_load(f)
        __collect(d, 'packages', os_name, packages, pip)
        __collect(d, 'tools', os_name, packages, pip)

    args = []
    args.extend(os_pm[os_name])
    args.extend(packages)
    unstd.os.run(args)

    args = []
    args.extend(["pip", "install"])
    args.extend(pip)
    unstd.os.run(args)


def is_valid_os(os_name: str) -> bool:
    return os_name in os_pm


def __main(args: List[str]) -> None:
    del sys.argv[0]
    cmd = unstd.os.next_arg(sys.argv, '')
    __install_on_os(cmd)


if __name__ == '__main__':
    __main(sys.argv)