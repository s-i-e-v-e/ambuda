import unstd.os


# Create a new translation file from `messages.pot`.
def init(locale):
    unstd.os.run(
        [
            "pybabel",
            "init",
            "-i",
            "messages.pot",
            "-d",
            "/ambuda/app/ambuda/translations",
            f"--locale {locale}",
        ]
    )


# Extract all translatable text from the application and save it in `messages.pot`.
def extract():
    unstd.os.run(
        [
            "pybabel",
            "extract",
            "--mapping",
            "babel.cfg",
            "--keywords",
            "_l",
            "--output-file",
            "messages.pot",
            ".",
        ]
    )


# Update all translation files with new text from `messages.pot`
def update():
    unstd.os.run(
        ["pybabel", "update", "-i", "messages.pot", "-d", "/ambuda/app/ambuda/translations"]
    )


# Compile all translation files.
# NOTE: you probably want `make install-i18n` instead.
def compile():
    unstd.os.run(["pybabel", "compile", "-d", "/ambuda/app/ambuda/translations"])
