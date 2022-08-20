# src/fogdb/dbs/cassy.py
"""Module providing casandra database functionalities via cassy."""
from collections import defaultdict


def create_model_from_raw(raw_data_map):
    """Create hardcoded Data Model from raw data map."""
    attributes = defaultdict(dict)
    for category in raw_data_map:
        for subcategory in raw_data_map[category]:
            attributes[category][subcategory] = set()
            for data_object in raw_data_map[category][subcategory]:
                for attribute, value in raw_data_map[category][subcategory][
                    data_object
                ].items():
                    attributes[category][subcategory].add(
                        (str(attribute).lower(), type(value))
                    )

    return dict(attributes)
