import os

#
# Specify all the fs paths used in the application
#
from pathlib import Path

TMP_DIR = Path("/tmp") / "ambuda-seeding"
GRETIL_DATA_DIR = TMP_DIR / "ambuda-gretil"
DCS_DATA_DIR = TMP_DIR / "ambuda-dcs"
DCS_RAW_FILE_DIR = TMP_DIR / "dcs-raw" / "files"
CACHE_DIR = TMP_DIR / "download-cache"

ENV_VIDYUT_DATA_DIR="VIDYUT_DATA_DIR"
ENV_VIDYUT_DATA_URL="VIDYUT_DATA_URL"
ENV_SQLALCHEMY_DATABASE_URI="SQLALCHEMY_DATABASE_URI"

def __get_env(k):
    return os.environ[k] if k in os.environ else None

def sql_uri():
    return __get_env(ENV_SQLALCHEMY_DATABASE_URI)