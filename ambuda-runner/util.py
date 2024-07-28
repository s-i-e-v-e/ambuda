import os
import shutil
import subprocess
import dotenv

def random_string():
    import uuid
    return uuid.uuid4()


def set_env(k, v):
    import os
    os.environ[k] = v


def get_env(k):
    return os.environ[k] if k in os.environ else None


def set_envars_from(f, default):
    ef = f if os.path.isfile(f) else default
    dotenv.load_dotenv(ef)
    d = dotenv.dotenv_values(ef)
    for k, v in d.items():
        os.environ[k] = v

#
# OS
#
def copy_file(s, d):
    xs = d.split(os.sep)
    xs.pop()
    dir=os.sep.join(xs)
    os.makedirs(dir, exist_ok=True)
    shutil.copyfile(s, d)


def read_file_as_string(p):
    with open(p, 'r') as f:
        return f.read()


def write_file_as_string(p, data):
    with open(p, 'w') as f:
        f.write(data)

def make_dir(p):
    os.makedirs(p, exist_ok=True)


def rmdir(d):
    shutil.rmtree(d, ignore_errors=True)


def cwd():
    return os.getcwd()


def run(xs):
    return subprocess.run(xs).returncode == 0

def rm(f):
    os.remove(f)


def file_exists(f):
    return os.path.isfile(f)


def extract_file_name(f):
    xs = f.split(os.sep)
    return xs.pop()

def xs_next(xs, default):
    x = xs[0] if len(xs) > 0 else default
    if x:
        del xs[0]
    return x

def next_arg_pair(xs):
    a = xs_next(xs, None)
    b = xs_next(xs, None) if a else None
    return a, b

def get_external_ip():
    x = subprocess.run(['/bin/ip', 'route', 'get', '1'], capture_output=True).stdout.decode('utf-8');
    return x.split(' ')[6]
    #return requests.get('https://checkip.amazonaws.com').text.strip()

def get_git_sha():
    p = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True)
    return p.stdout.strip()