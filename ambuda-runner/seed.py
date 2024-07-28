import ambuda


sources = [
    ambuda.seed.lookup.role,
    ambuda.seed.lookup.page_status,
    ambuda.seed.texts.gretil,
    ambuda.seed.texts.ramayana,
    ambuda.seed.texts.mahabharata,
    ambuda.seed.dcs,
    ambuda.seed.dictionaries.amarakosha,
    ambuda.seed.dictionaries.apte,
    ambuda.seed.dictionaries.apte_sanskrit_hindi,
    ambuda.seed.dictionaries.monier,
    ambuda.seed.dictionaries.shabdakalpadruma,
    ambuda.seed.dictionaries.shabdartha_kaustubha,
    ambuda.seed.dictionaries.shabdasagara,
    ambuda.seed.dictionaries.vacaspatyam,
]


def __seed(xs):
    for x in xs:
        x.run()


# Seed the database with a minimal dataset for CI. We fetch data only if it is
# hosted on GitHub. Other resources are less predictable.
def ci():
    __seed([a for a in sources if a in [
        ambuda.seed.lookup,
        ambuda.seed.texts.gretil,
        ambuda.seed.dcs
    ]])


# Seed the database with just enough data for the devserver to be interesting.
def basic():
    __seed([a for a in sources if a in [
        ambuda.seed.lookup,
        ambuda.seed.texts.gretil,
        ambuda.seed.dcs,
        ambuda.seed.dictionaries.monier
    ]])


# Seed the database with all of the text, parse, and dictionary data we serve
# in production.
def all():
    __seed(sources)
