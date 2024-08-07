import os
from pathlib import Path

from dotenv import load_dotenv
from fabric import Connection, task

load_dotenv()
APP_DIRECTORY = Path(os.environ["REMOTE_APP_DIRECTORY"])
UPLOADS_DIRECTORY = Path(os.environ["REMOTE_UPLOADS_DIRECTORY"])
SECRETS_DIRECTORY = Path(os.environ["REMOTE_SECRETS_DIRECTORY"])

USER = os.environ["REMOTE_USER"]
HOST = os.environ["REMOTE_HOST"]

r = Connection(f"root@{HOST}")
c = Connection(f"{USER}@{HOST}")


@task
def init_secrets(_):
    c.run(f"mkdir -p {SECRETS_DIRECTORY}")
    json_path = str(SECRETS_DIRECTORY / "google-cloud-credentials.json")
    c.put("production/google-cloud-credentials.json", json_path)


def deploy_to_commit(_, pointer: str):
    """Deploy the given branch pointer to production.

    :param pointer: a commit SHA, branch name, etc.
    """
    with c.cd(APP_DIRECTORY):
        # Verify that unit tests pass on prod.
        with c.prefix("source env/bin/activate"):
            c.run("make test")

        # Copy production config settings.
        env_path = str(APP_DIRECTORY / ".env")
        c.put("production/prod-env", env_path)

    c.local("python test_prod.py")
    print("Deploy complete")
