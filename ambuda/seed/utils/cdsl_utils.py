import io
import itertools
import logging
from xml.etree import ElementTree as ET


#: The maximum number of entries to add to the dictionary at one time.
#:
#: Batching is more efficient than adding entries one at a time. But large
#: batches also take up a lot of memory. I picked 10000 arbitrarily.
BATCH_SIZE = 10000


def iter_entries_as_xml(blob: str):
    """Iterate over CDSL-style dictionary XML."""
    tag_str = (
        "H1 H1A H1B H1C H1E H2 H2A H2B H2C H2E H3 H3A H3B H3C H3E H4 H4A H4B H4C H4E"
    )
    allowed_tags = set(tag_str.split())

    for _, elem in ET.iterparse(io.BytesIO(blob), events=["end"]):
        if elem.tag not in allowed_tags:
            continue

        # NOTE: `key` is not unique.
        key = None
        for child in elem.iter():
            if child.tag == "key1":
                key = child.text
                break
        yield key, elem

        elem.clear()


def iter_entries_as_strings(blob: str):
    for key, elem in iter_entries_as_xml(blob):
        value = ET.tostring(elem, encoding="utf-8")

        assert key and value
        assert len(value) > 50, value
        yield key, value


def batches(generator, n):
    while True:
        batch = list(itertools.islice(generator, n))
        if batch:
            yield batch
        else:
            return


def create_from_scratch(engine, slug: str, title: str, generator):
    from ambuda.repository import DataSession, Dictionary, DictionaryEntry

    with DataSession() as ds:
        # Delete existing dictionary and all of its entries.
        d = Dictionary.select_by_slug(ds, slug)
        if d:
            DictionaryEntry.delete_by_dictionary(ds, d.id)
            Dictionary.delete_by_slug(ds, d.slug)

        # Create a new dictionary
        Dictionary.insert(ds, slug, title)
        d = Dictionary.select_by_slug(ds, slug)

        assert d and d.id

        for i, batch in enumerate(batches(generator, BATCH_SIZE)):
            for key, value in batch:
                DictionaryEntry.insert(ds, d.id, key, value)
            logging.info(BATCH_SIZE * (i + 1))
