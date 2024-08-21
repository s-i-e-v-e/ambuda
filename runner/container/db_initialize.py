#
# Initializes the database by creating all tables.
#

import subprocess

from unstd import config, os
from ambuda import database as db
from ambuda.seed import lookup
from sqlalchemy import create_engine
from container import seeding


def get_db_file_path(sql_uri: str) -> str:
    """get file path from sql alchemy uri"""

    db_file_path = sql_uri.replace("sqlite:///", "")
    if db_file_path == sql_uri:
        print(f"Error! Invalid SQLALCHEMY_DATABASE_URI {sql_uri}")
        raise ValueError(f"Invalid SQLALCHEMY_DATABASE_URI: {sql_uri}")
    return db_file_path


def run_module(module):
    print(f'{"#"}' * 20)
    print(f"Intializing {module}")
    module.run()
    print(f"{module} initialization successful!")
    print(f'{"#"}' * 20)


def init_database(sql_uri: str, db_file_path: str, seed_type: str):
    import unstd.os
    """Initialize database"""

    print(f"Initializing database at {db_file_path}...")
    dir_path = unstd.os.extract_dir_path(db_file_path)
    # always make dir
    unstd.os.make_dir(dir_path)

    # Create tables
    engine = create_engine(sql_uri)
    db.Base.metadata.create_all(engine)

    from ambuda.repository import DataSession, generate_schema
    with DataSession() as ds:
        generate_schema(ds)

    try:
        if seed_type == "all":
            seeding.all()
        else:
            seeding.basic()
    except Exception as init_ex:
        print(f"Error: Failed to initialize database. Error: {init_ex}")
        raise init_ex
    print(f"Success! Database initialized at {db_file_path}")


def load_database(db_file_path: str):
    """Database already initialized. Run lookup module (TODO: Legacy step. Check why?). Update to the latest migration."""
    if not os.file_exists(db_file_path):
        print(f"Database not found at {db_file_path}...")
        raise FileNotFoundError("Database file not found")

    try:
        run_module(lookup)
        print(f"Success! Database is ready at {db_file_path}")
    except Exception as load_ex:
        print(f"Error: Failed to load database. Error: {load_ex}")
        raise load_ex


def run(cfg: config.ContainerConfig, seed_type: str):
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

    if os.file_exists(db_file_path):
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
