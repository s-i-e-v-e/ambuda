#
# Initializes the database by creating all tables.
#

import subprocess
from pathlib import Path

from sqlalchemy import create_engine

import unstd.config
from ambuda import database as db
from ambuda.seed import lookup
import seeding


def get_db_file_path(sql_uri):
    """get file path from sql alchemy uri"""

    db_file_path = sql_uri.replace("sqlite:///", "")
    if db_file_path == sql_uri:
        print(f"Error! Invalid SQLALCHEMY_DATABASE_URI {sql_uri}")
        raise ValueError(f"Invalid SQLALCHEMY_DATABASE_URI: {sql_uri}")
    return Path(db_file_path)


def run_module(module_name):
    print(f'{"#"}' * 20)
    print(f"Intializing {module_name}")
    module_name.run()
    print(f"{module_name} initialization successful!")
    print(f'{"#"}' * 20)


def init_database(sql_uri, db_file_path, seed_type):
    """Initialize database"""

    print(f"Initializing database at {db_file_path}...")
    # Create tables
    engine = create_engine(sql_uri)
    db.Base.metadata.create_all(engine)

    try:
        if seed_type == "all":
            seeding.all()
        else:
            seeding.basic()
        alembic_migrations()
    except Exception as init_ex:
        print(f"Error: Failed to initialize database. Error: {init_ex}")
        raise init_ex
    print(f"Success! Database initialized at {db_file_path}")


def alembic_migrations():
    try:
        subprocess.run(["alembic", "ensure_version"])
        subprocess.run(["alembic", "stamp", "head"])
        print("Success! Database version check completed.")
    except subprocess.CalledProcessError as mig_ex:
        print(f"Error processing alembic commands - {mig_ex}")
        raise mig_ex


def load_database(db_file_path):
    """Database already initialized. Run lookup module (TODO: Legacy step. Check why?). Update to the latest migration."""
    if not db_file_path.exists():
        print(f"Database not found at {db_file_path}...")
        raise FileNotFoundError("Database file not found")

    try:
        run_module(lookup)
        subprocess.run(["alembic", "upgrade", "head"])
        print(f"Success! Database is ready at {db_file_path}")
    except Exception as load_ex:
        print(f"Error: Failed to load database. Error: {load_ex}")
        raise load_ex


def run(cfg: unstd.config.ContainerConfig, seed_type):
    """
    Initialize db for fresh installs. Load db on restarts.
    Return value is boolean as the caller is a shell script.
    """

    sql_uri = cfg.SQLALCHEMY_DATABASE_URI
    try:
        db_file_path = get_db_file_path(sql_uri)
    except Exception as err:
        print(f"Failed to get db path - {err}")
        return False

    if db_file_path.exists():
        print(f"Database found at {db_file_path}..")
        try:
            load_database(db_file_path)
        except Exception as load_ex:
            print(
                f"Error! Failed to load database from {db_file_path}. Error: {load_ex}"
            )
            return False
    else:
        # This is a new deployment.
        print("Initialize database")
        try:
            init_database(sql_uri, db_file_path, seed_type)
        except Exception as init_ex:
            print(
                f"Error! Failed to initialize database at {db_file_path}. Error: {init_ex}"
            )
            return False
    print("Database set up complete.")
    return True
