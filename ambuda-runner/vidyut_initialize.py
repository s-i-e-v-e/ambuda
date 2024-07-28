import util
import ambuda.system

def __init():
    if not util.get_env(ambuda.system.ENV_VIDYUT_DATA_DIR):
        print("Error! VIDYUT_DATA_DIR is not set. Please set environment variable VIDYUT_DATA_DIR")
        return False
    VIDYUT_DATA_DIR = util.get_env(ambuda.system.ENV_VIDYUT_DATA_DIR)

    if not util.get_env(ambuda.system.ENV_VIDYUT_DATA_URL):
        print("Error! URL to fetch Vidyut data is not set. Please set environment variable VIDYUT_DATA_URL")
        return False

    VIDYUT_DATA_URL=util.get_env(ambuda.system.ENV_VIDYUT_DATA_URL)

    VIDYUT_MARKER=f"{VIDYUT_DATA_DIR}/vidyut_is_here"
    if (util.file_exists(VIDYUT_MARKER)):
        # TODO: calculate SHA256 of installed files and compare
        print("Vidyut data found!")
        return True

    print(f"Fetching Vidyut data from {VIDYUT_DATA_URL} to {VIDYUT_DATA_DIR}.")
    util.make_dir(VIDYUT_DATA_DIR)

    VIDYUT_DATA_FILE = util.extract_file_name(VIDYUT_DATA_URL)
    fp = f"{VIDYUT_DATA_DIR}/{VIDYUT_DATA_FILE}"

    if util.run(["wget", "-P" ,VIDYUT_DATA_DIR, VIDYUT_DATA_URL, "-q"]):
        if util.run(["unzip", "-d", VIDYUT_DATA_DIR, "-j", fp]):
            pass
        else:
            print(f"Unable to unzip {fp}")
            return False
    else:
        print(f"Error! Failed to fetch from {VIDYUT_DATA_URL}")
        return False

    # Successfully installed. Leave a mark.
    util.run(["touch",  VIDYUT_MARKER])
    return True


def run():
    if __init():
        print("Vidyut data initialization completed")
    else:
        print("Error pulling from Vidyut. Fetch vidyut data later.")