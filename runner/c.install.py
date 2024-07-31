import sys
sys.path.extend(["./", "./unstd"])
import yaml
import unstd.os

def do_filter(xs, name):
    ys = [a[name] if a.get(name) else '' for a in xs]
    return list(filter(lambda a: a, ys))


def normalize(x, k):
    x = x.replace('$', k).replace('.', '-').replace('_', '-')
    x = x.replace('@', k)
    return x


def install_on_os(os_name):
    pip = []
    packages = []
    with open('deploy/deps.runtime.yml', 'r') as f:
        for o in yaml.safe_load(f).get('packages'):
            for k in o:
                xs = o[k]
                if not len(xs):
                    # no entries. key is package name
                    packages.append(k)
                else:
                    ys = do_filter(xs, os_name)
                    if not len(ys):
                        # no entry for os. use pip
                        ys = do_filter(xs, 'py')
                        if not len(ys):
                            raise ValueError(f'Package not found: {k}')
                        else:
                            pip.append(normalize(ys[0], k))
                    else:
                        packages.append(normalize(ys[0], k))

    args = []
    args.extend(["apk", "add", "--no-cache"])
    args.extend(packages)
    unstd.os.run(args)

    args = []
    args.extend(["pip", "install"])
    args.extend(pip)
    unstd.os.run(args)
    #print(' '.join(pip))


install_on_os('alpine')