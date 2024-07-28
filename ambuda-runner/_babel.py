import util

# Create a new translation file from `messages.pot`.
def init(locale):
    util.run(["pybabel", "init", "-i", "messages.pot", "-d", "/app/ambuda/translations", f"--locale {locale}"])


# Extract all translatable text from the application and save it in `messages.pot`.
def extract():
    util.run(["pybabel", "extract", "--mapping", "babel.cfg", "--keywords", "_l", "--output-file", "messages.pot", "."])


# Update all translation files with new text from `messages.pot`
def update():
    util.run(["pybabel", "update", "-i", "messages.pot", "-d", "/app/ambuda/translations"])


# Compile all translation files.
# NOTE: you probably want `make install-i18n` instead.
def compile():

    util.run(["pybabel", "compile", "-d", "/app/ambuda/translations"])