# coding=utf-8
import json
import time


def no_op(*args, **kwargs):
    pass


def save_to_json(result, file_base="api_result"):
    """
    Saves a result to json with a timestamp in milliseconds.

    Args:
        result (list|dict): a json dumpable object to save to file.
        file_base (str): filename base. Can contain a relative or absolute
                         path.
    """
    filename = "{}_{}.json".format(file_base, str(int(time.time() * 1000)))
    with open(filename, 'w') as json_filehandler:
        json.dump(result, json_filehandler)
