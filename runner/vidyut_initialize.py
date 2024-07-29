import unstd.os
import unstd.config


def __init(cfg: unstd.config.BaseConfig):
    vidyut_marker = f"{cfg.VIDYUT_DATA_DIR}/vidyut_is_here"
    if unstd.os.file_exists(vidyut_marker):
        # TODO: calculate SHA256 of installed files and compare
        print("Vidyut data found!")
        return True

    print(f"Fetching Vidyut data from {cfg.VIDYUT_DATA_URL} to {cfg.VIDYUT_DATA_DIR}.")
    unstd.os.make_dir(cfg.VIDYUT_DATA_DIR)

    vidyut_data_file = unstd.os.extract_file_name(cfg.VIDYUT_DATA_URL)
    fp = f"{cfg.VIDYUT_DATA_DIR}/{vidyut_data_file}"

    if unstd.os.run(["wget", "-P", cfg.VIDYUT_DATA_DIR, cfg.VIDYUT_DATA_URL, "-q"]):
        if unstd.os.run(["unzip", "-d", cfg.VIDYUT_DATA_DIR, "-j", fp]):
            pass
        else:
            print(f"Unable to unzip {fp}")
            return False
    else:
        print(f"Error! Failed to fetch from {cfg.VIDYUT_DATA_URL}")
        return False

    # Successfully installed. Leave a mark.
    unstd.os.run(["touch", vidyut_marker])
    return True


def run(cfg):
    if __init(cfg):
        print("Vidyut data initialization completed")
    else:
        print("Error pulling from Vidyut. Fetch vidyut data later.")
