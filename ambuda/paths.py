#
# Specify all the fs paths used in the application
#
from pathlib import Path

TMP_DIR = Path("/tmp") / "ambuda-seeding"
GRETIL_DATA_DIR = TMP_DIR / "ambuda-gretil"
DCS_DATA_DIR = TMP_DIR / "ambuda-dcs"
DCS_RAW_FILE_DIR = TMP_DIR / "dcs-raw" / "files"
CACHE_DIR = TMP_DIR / "download-cache"
