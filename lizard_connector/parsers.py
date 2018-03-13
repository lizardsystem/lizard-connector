# coding=utf-8
import collections

try:
    import pandas as pd
except ImportError:
    pd = None


try:
    import numpy as np
except ImportError:
    pd = None


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
    try:
        events = results.pop('events') or {}
    except KeyError:
        events = {}
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
    Converts result dictionary to pandas.

    :param results:
    :param sep:
    :return:
    """
    flattened = [flatten_result(r, sep=sep) for r in results]
    metadata_dataframe = pd.DataFrame([x[0] for x in flattened])
    if convert_timestamps:
        to_timestamps(metadata_dataframe)
        event_dataframes = [
            to_timestamps(pd.DataFrame(x[1])) if x[1] else None for x in
            flattened
        ]
    else:
        event_dataframes = [
            pd.DataFrame(x[1]) if x[1] else [] for x in flattened]
    try:
        return metadata_dataframe, event_dataframes
    except NameError:
        raise ImportError(
            "Trying to convert to pandas dataframe without pandas. Please "
            "install Pandas."
        )


def scientific(results, sep='__', convert_timestamps=True):
    try:
        if isinstance(results, dict):
            print(dict)
            results = [results]
        if isinstance(results[0], list):
            try:
                return np.array(results)
            except NameError:
                raise ImportError(
                    "Trying to convert to numpy array without numpy. "
                    "Please install Numpy."
                )
        else:
            return as_dataframes(results, sep, convert_timestamps)
    except IndexError:
        return


def json(results, **kwargs):
    return results
