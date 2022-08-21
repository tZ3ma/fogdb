# src/fogdb/dbs/cassy.py
"""Module providing casandra database functionalities via cassy."""
import logging
from collections import defaultdict
from configparser import ConfigParser
from pathlib import Path

from cassy.model import MetaModel, create_data_model

logger = logging.getLogger(__name__)
dtypes = {
    str: "Text",
    int: "Integer",
    bool: "Boolean",
    dict: "Map",
    list: "List",
}
"""Python to cassandra column data type mapping."""


def map_model_attributes(raw_data_map):
    """Map required data model attributes from raw data map.

    Creates a set of tuples for each subcategory listing all found attribute
    specifiers as well as their types as in::

        (attribute, cassandra_type(attribute-value))

    Parameters
    ----------
    raw_data_map: dict
        Raw data map as returned by :func:`fogdb.raw.to_dict`.

    Returns
    -------
    dict
        Map mimicking the structure of
        :paramref:`~map_model_attributes.raw_data_map` replacing the actual
        data entries by a set of tuples representing found attributes and
        corresponding cassandra data types.

    Examples
    --------
    Design Use Case:

    >>> data_map = {
    ...     "test_crawford": {
    ...         "common_fruiting_trees": {
    ...             "Cydonia_oblonga": {
    ...                 "latin": "Cydonia oblonga",
    ...                 "common_names": ["Quince"],
    ...                 "usda_hardiness": "4",
    ...             },
    ...             "Ficus_carica": {
    ...                 "latin": "Ficus carica",
    ...                 "common_names": ["Fig"],
    ...                 "usda_hardiness": "7",
    ...             },
    ...         },
    ...         "less_common_fruiting_trees": {
    ...             "Arbutus unedo": {
    ...                 "latin": "Arbutus unedo",
    ...                 "common_names": ["Strawberry Tree"],
    ...                 "usda_hardiness": "7",
    ...             },
    ...             "Armelancher_canadensis": {
    ...                 "latin": "Armelancher canadensis",
    ...                 "common_names": ["Juneberry", "Serviceberry"],
    ...                 "usda_hardiness": "4",
    ...             },
    ...             "Asimina_triloba": {
    ...                 "latin": "Asimina triloba",
    ...                 "common_names": ["PawPaw", "Pawpaw"],
    ...                 "USDA_hardiness": 5,
    ...             },
    ...         },
    ...     },
    ...     "test_jacke": {
    ...         "plant_matrix": {
    ...             "Cydonia_oblonga": {
    ...                 "latin": "Cydonia oblonga",
    ...                 "common_names": ["Quince"],
    ...                 "usda_hardiness": "4",
    ...             }
    ...         }
    ...     },
    ... }
    >>> import pprint
    >>> pprint.pprint(map_model_attributes(data_map))
    {'test_crawford': {'common_fruiting_trees': {('common_names', 'List'),
                                                 ('latin', 'Text'),
                                                 ('usda_hardiness', 'Text')},
                       'less_common_fruiting_trees': {('common_names', 'List'),
                                                      ('latin', 'Text'),
                                                      ('usda_hardiness', 'Integer'),
                                                      ('usda_hardiness', 'Text')}},
     'test_jacke': {'plant_matrix': {('common_names', 'List'),
                                     ('latin', 'Text'),
                                     ('usda_hardiness', 'Text')}}}
    """
    attributes = defaultdict(dict)
    for category in raw_data_map:
        for subcategory in raw_data_map[category]:
            attributes[category][subcategory] = set()
            for data_object in raw_data_map[category][subcategory]:
                for attribute, value in raw_data_map[category][subcategory][
                    data_object
                ].items():
                    attributes[category][subcategory].add(
                        (str(attribute).lower(), dtypes[type(value)])
                    )

    return dict(attributes)


# pylint: disable=too-many-locals
# function body is a tad verbose with all its local variables. But since it does
# some heavy lifting, I feel it is still reasonable with 22 local variables

# pylint: disable=too-many-arguments
# I think number of arguments is still acceptable
# especially, since the standard use case will be
# "hardcode_datamodel_from_raw(raw_data_map)"
def hardcode_datamodel_from_raw(
    raw_data_map,
    path="~/.fogdb.d/db_data_models/cassy/",
    primary_keys=("latin",),
    clustering_keys=None,
    config="~/.fogdb.d/conf.cfg",
    overwrite=False,
    backup=True,
):
    """Create a hardcoded cassandra data model from raw data map.

    Creates a python file inside a category folder at
    :paramref:`~create_model_from_raw.path`  for each subcategory.
    This python file represents the respective cassandra data model.

    The exact locations for each ``category.subcategory`` data model
    is stored inside :paramref:`~create_model_from_raw.config`.

    Parameters
    ----------
    raw_data_map: dict
        Raw data map as returned by :func:`fogdb.raw.to_dict`.

    path: str, default = "~/.fogdb.d/db_data_models/cassy/"
        String specifying the top level folder of the hardcoded data models.
        Will be populated with subfolders and python files according to
        the :paramref:`~create_model_from_raw.raw_data_map`.

    primary_keys: ~collections.abc.Container, default=("latin",)
        Container of strings specifying which of the attributes found by
        :func:`map_model_attributes` are to be used as primary keys.

    clustering_keys: ~collections.abc.Container, default=None
        Container of tuples specifying which of the attributes found by
        :func:`map_model_attributes` are to be used as clustering_keys
        in conjunction with their clustering order as in::

            clustering_keys = [
                ("english", "ASC"),
                ("german", "DESC"),
            ]

    config: str, default = "~/.fogdb.d/conf.cfg"
        String specifying the config file location as created during Initialization
        (:class:`fogdb.setup.Initializer`).

        The exact locations for each ``category.subcategory`` data model
        is stored inside the config file for ease of later extraction.

    overwrite: bool, default=False
        Boolean indicating whether the hardcoded model data file should be
        overwritten. If :paramref:`~create_model_from_raw.backup` is True,
        exsting file will be renamed to
        ``existing-name_backup_hash(timestamp).py``

    backup: bool, default=True
        Boolean indicating whether the hardcoded model data file should be
        kept as backup in case of overwriting. Exsting file will be renamed to
        ``existing-name_backup_hash(timestamp).py``

    Returns
    -------
    dict
        Dictionairy of categories subcategories and respective hardcoded data
        model locations as in::

            locations = {
                'crawford': {
                    'common_fruiting_trees': 'location_string',
                    'less_common_fruiting_trees': 'location_string',
                },
                'test_jacke': {
                    'plant_matrix': 'location_string',
                }
            }
    """
    # create the hardcoded data models home if not already present
    cassy_models_dir = Path(path).expanduser()
    cassy_models_dir.mkdir(parents=True, exist_ok=True)

    # make sure clustering keys are iterable for cleaner code
    if not clustering_keys:
        clustering_keys = ()

    # abbrevate key variable names for 1 liners
    pks = primary_keys
    cks = clustering_keys

    # get table attributes and mimick the result path dict
    table_attributes = map_model_attributes(raw_data_map)
    hardcoded_locations = table_attributes.copy()

    for category in table_attributes:
        for subcategory, attributes in table_attributes[category].items():
            prim_keys = [tpl for tpl in attributes if tpl[0] in pks]
            clust_keys = [tpl for tpl in attributes if tpl[0] in cks]
            columns = [tpl for tpl in attributes if tpl[0] not in [*pks, *cks]]

            # create the category dir
            cat_fldr = cassy_models_dir / Path(category)
            cat_fldr.mkdir(parents=True, exist_ok=True)

            subcategory_file = cat_fldr / Path("".join([subcategory, ".py"]))

            # parse tuples to dict and handle duplicate data types:
            prim_keys = _parse_column_tuples_to_dict(prim_keys)
            clust_keys = _parse_column_tuples_to_dict(clust_keys)
            columns = _parse_column_tuples_to_dict(columns)

            # create the meta model
            meta_model = MetaModel(
                name=subcategory,
                primary_keys=prim_keys,
                clustering_keys=clust_keys,
                columns=columns,
            )

            # hardcode the data model
            location = create_data_model(
                meta_model=meta_model,
                path=subcategory_file,
                overwrite=overwrite,
                backup=backup,
            )

            hardcoded_locations[category][subcategory] = str(location)

    # update the lcoations inside the config file
    _update_config_file_locations(config, hardcoded_locations)

    return hardcoded_locations


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals


def _parse_column_tuples_to_dict(col_tpls):
    parsed_dct = {}
    # iterate through all passed tuples
    for tpl in col_tpls:
        # unpack for better readability
        label, cassy_dtype = tpl[0], tpl[1]

        # if not already present just add entry
        if label not in parsed_dct:
            parsed_dct[label] = cassy_dtype

        # if present:
        else:
            # "Text" data type takes precedence
            if cassy_dtype == "Text":
                logger.warning(
                    "%s already present as type '%s'", label, parsed_dct[label]
                )
                logger.warning("Overwriting it with the more general 'Text'")
                logger.warning("Which is also present")
                parsed_dct[label] = cassy_dtype

            # and an accodring warning is loogged if necessary
            else:
                logger.warning("%s already present as type 'Text'", label)
                logger.warning("Which takes precedence over %s", cassy_dtype)
                logger.warning("Keeping only 'Text'")

    return parsed_dct


def _update_config_file_locations(config_file_path, locations):

    # init the config parsing
    config_path = str(Path(config_file_path).expanduser())
    config_object = ConfigParser()
    config_object.read(config_path)

    hcl = locations
    value_dict = {}
    for cat in hcl:
        for subcat in hcl[cat]:
            value_dict[f"{cat}.{subcat}"] = hcl[cat][subcat]

    config_object["cassy"] = value_dict
    with open(config_path, "w", encoding="utf8") as conf:
        config_object.write(conf)
