# coding=utf-8
import collections

SCIENTIFIC_AVAILABLE = True

try:
    import pandas as pd
except ImportError:
    SCIENTIFIC_AVAILABLE = False

try:
    import numpy as np
except ImportError:
    SCIENTIFIC_AVAILABLE = False


DATA_TYPE_FIELDS = (
    'events',
    'data',
    'percentiles'
)


def list_on_key(results, key):
    """
    Get a list of a certain element from the root of the results attribute.

    Args:
        json (dict): json from the Lizard api parsed into a dictionary.
        key (str): the element you wish to get.

    Returns:
        A list of all elements in the root of the results attribute.
    """
    return [x[key] for x in results]


def uuids(results, endpoint=None):
    """
    Get a list of a certain element from the root of the results attribute.

    Args:
        json (dict): json from the Lizard api parsed into a dictionary.
        endpoint (str): endpoint you wish to query.

    Returns:
        A list of all uuid elements in the root of the results attribute.
    """
    uuid = 'unique_id' if endpoint == 'organisations' else 'uuid'
    return list_on_key(results, uuid)


def flatten_dict(results, parent_key='', sep='__'):
    """
    Flatten dictionary.

        {'a': 1,
         'c': {'a': 2,
               'b': {'x': 5,
                     'y' : 10}},
         'd': [1, 2, 3]}

    Is flattened to:

        {'a': 1,
         'c__a': 2,
         'c__b__x': 5,
         'c__b__y': 10,
         'd': [1, 2, 3]}

    Based on:
        https://stackoverflow.com/questions/6027558/
        flatten_dict-nested-python-dictionaries-compressing-keys#answer-6027615

    Args:
        results(dict): multilevel dictionary.
        parent_key(str): key to use
        sep(str): seperator between
    Returns:
        Flattened dictionary.
    """
    items = []
    for k, v in results.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def flatten_result(results, parent_key='', sep='__'):
    # First remove the results.
    events = {}
    for data_type in DATA_TYPE_FIELDS:
        try:
            events = results.pop(data_type) or {}
        except KeyError:
            continue
        if events:
            break
    return flatten_dict(results, sep=sep), events


def to_timestamps(dataframe):
    if dataframe is None or dataframe.empty:
        return
    for time_column in (c for c in dataframe.columns if
                        c.endswith('timestamp') or c in ('start', 'end')):
        dataframe[time_column] = pd.to_datetime(
            dataframe[time_column], unit='ms')
        return dataframe


def as_dataframes(results, sep='__', convert_timestamps=True):
    """
    Converts result dictionary to pandas DataFrame.

    Args:
        results:
        sep:
    Returns:

    """
    # TODO: clean up this function.
    if not results:
        # return empty.
        return pd.DataFrame(), []
    if isinstance(results, dict):
        # Result from a detail page, create a list of results.
        results = [results]

    flattened = [flatten_result(r, sep=sep) for r in results]

    try:
        # metadata is always found in dict form.
        metadata_dataframe = pd.DataFrame([x[0] for x in flattened])
    except NameError:
        raise ImportError(
            "Trying to convert to pandas Dataframe without pandas. Please "
            "install Pandas."
        )
    try:
        is_event_list = isinstance(flattened[0][1][0], list)
    except (IndexError, KeyError):
        is_event_list = False
    if is_event_list:
        try:
            return metadata_dataframe, [
                np.array(flat_data) for _, flat_data in flattened]
        except NameError:
            raise ImportError(
                "Trying to convert to numpy array without numpy. "
                "Please install Numpy."
            )
    else:
        event_dataframes = [
            pd.DataFrame(x[1]) if x[1] else [] for x in flattened]
    if convert_timestamps:
        to_timestamps(metadata_dataframe)
        event_dataframes = [
            to_timestamps(pd.DataFrame(x[1])) if x[1] else None for x in
            flattened
        ]

    return metadata_dataframe, event_dataframes


def scientific(results, sep='__', convert_timestamps=True):
    """
    Parses a result as a metadata dataframe and a list of data.
    The data is either a numpy array or pandas DataFrame for each metadata row.

    Args:
        results(list|dict): response in the form of a python object.
        sep(str): seperator used to name the denormalized metadata columns.
        convert_timestamps(bool): Wether or not to convert the timestamps
    Returns:
        metadata dataframe and a list of data:
            list[pandas.DataFrame]|list[numpy.array]
    """
    try:
        if isinstance(results[0], list):
            # our first result is a list internally, we return it as such:
            try:
                return pd.DataFrame(), [np.array(results)]
            except NameError:
                raise ImportError(
                    "Trying to convert to numpy array without numpy. "
                    "Please install Numpy."
                )
        return as_dataframes(results, sep, convert_timestamps)
    except IndexError:
        return [], []


def json(results, **kwargs):
    return results
