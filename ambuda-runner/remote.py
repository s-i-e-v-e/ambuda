import subprocess
import os
import unstd.os

def write_text(file_name, data):
    with open(file_name, "w") as text_file:
        text_file.write(data)

    subprocess.run(["chmod", "0600", file_name])

GIT_URL = "https://github.com/s-i-e-v-e/ambuda"
def remote_exec(cmd):
    SSH_HOST = os.environ['SSH_HOST']
    SSH_KEY = os.environ['SSH_KEY']
    SSH_KNOWN_HOSTS = os.environ['SSH_KNOWN_HOSTS'].replace('$SSH_HOST', SSH_HOST.split(':')[0])

    KEY_FILE = "/tmp/ssh.key"
    HOST_FILE = "/tmp/known_hosts"
    write_text(KEY_FILE, SSH_KEY)
    write_text(HOST_FILE, SSH_KNOWN_HOSTS)

    dir = unstd.os.random_string()
    remote_cmd = f"""
    mkdir -p /tmp/{dir} \
    && cd /tmp/{dir} \
    && git clone {GIT_URL} \
    && cd ambuda \
    && git switch podman \
    && ./ar {cmd}
    """

    #subprocess.run(["bash", "-c", remote_cmd])
    subprocess.run(["ssh", "-o", "UserKnownHostsFile "+HOST_FILE, "-i", KEY_FILE, "$SSH_HOST", remote_cmd])
    print('done')