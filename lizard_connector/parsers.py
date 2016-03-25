# coding=utf-8


def parse_element(json_, element):
    """
    Get a list of a certain element from the root of the results attribute.

    Args:
        json (dict): json from the Lizard api parsed into a dictionary.
        element (str): the element you wish to get.

    Returns:
        A list of all elements in the root of the results attribute.
    """
    return [x[element] for x in json_]


def parse_uuid(json_, endpoint=None):
    """
    Get a list of a certain element from the root of the results attribute.

    Args:
        json (dict): json from the Lizard api parsed into a dictionary.
        endpoint (str): endpoint you wish to query.

    Returns:
        A list of all uuid elements in the root of the results attribute.
    """
    uuid = 'unique_id' if endpoint == 'organisations' else 'uuid'
    return parse_element(json_, uuid)
