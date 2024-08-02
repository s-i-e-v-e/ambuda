import ambuda.seed.texts
import ambuda.seed.lookup
import ambuda.seed.dcs
import ambuda.seed.dictionaries

sources = [
    ambuda.seed.lookup,
    ambuda.seed.texts.gretil,
    # ambuda.seed.texts.ramayana,
    # ambuda.seed.texts.mahabharata,
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
        try:
            print(f"Seeding: {x.__name__}")
            x.run()
        except Exception as e:
            print(f"Error: Unable to seed: {x.__name__}")
            print(e)


# Seed the database with a minimal dataset for CI. We fetch data only if it is
# hosted on GitHub. Other resources are less predictable.
def ci():
    __seed(
        [
            a
            for a in sources
            if a in [ambuda.seed.lookup, ambuda.seed.texts.gretil, ambuda.seed.dcs]
        ]
    )


# Seed the database with just enough data for the devserver to be interesting.
def basic():
    __seed(
        [
            a
            for a in sources
            if a
            in [
                ambuda.seed.lookup,
                ambuda.seed.texts.gretil,
                ambuda.seed.dcs,
                ambuda.seed.dictionaries.monier,
            ]
        ]
    )


# Seed the database with all of the text, parse, and dictionary data we serve
# in production.
def all():
    __seed(sources)
