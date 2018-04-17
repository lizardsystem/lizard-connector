# coding=utf-8
"""
Callbacks to be used with lizard_connector.connector.Endpoint().get_async
"""
import json
import time
import pickle

FILE_BASE = "api_result"


def no_op(*args, **kwargs):
    pass


def save_to_json(result):
    """
    Saves a result to json with a timestamp in milliseconds.

    Use with Endpoints initialized with the lizard_connector.json parser.

    Args:
        result (list|dict): a json dumpable object to save to file.
    """
    filename = "{}_{}.json".format(FILE_BASE, str(int(time.time() * 1000)))
    with open(filename, 'w') as json_filehandler:
        json.dump(result, json_filehandler)


def save_to_pickle(result):
    """
    Pickle a result to file with a timestamp in milliseconds.

    Use with Endpoints initialized with the lizard_connector.json parser.

    Args:
        result (list|dict): a python serializable object to save to file.
    """
    filename = "{}_{}.p".format(FILE_BASE, str(int(time.time() * 1000)))
    with open(filename, 'w') as pickle_filehandler:
        pickle.dump(result, pickle_filehandler)


def save_to_hdf5(result):
    """
    Saves a result to hdf5 file with a timestamp in milliseconds.

    Use with Endpoints initialized with the lizard_connector.scientific parser.

    Requires the h5py library for HDF5.

    Args:
        result (tuple[pandas.DataFrame|numpy.array]): a tuple with two elements
            which are either a pandas DataFrame or a numpy array.
    """
    filename = "{}_{}.h5".format(FILE_BASE, str(int(time.time() * 1000)))

    # h5py is only required when using this callback. So we import here.
    try:
        import h5py
        import pandas as pd
    except ImportError:
        raise ImportError("When the save_to_hdf5 callback is used, make sure"
                          "h5py, pandas and numpy are installed.")
    result.metadata.to_hdf(filename, 'metadata')

    for i, ds in enumerate(result.data):
        if ds:
            dataset_name = 'data_{}'.format(i)
            if isinstance(ds, pd.DataFrame):
                ds.to_hdf(filename, dataset_name)

            with h5py.File(filename, "w", libver='latest') as h5_file:
                if ds.dtype.kind == "O":
                    print(ds)
                    dtype = str
                    ds = ds.astype(dtype)
                else:
                    dtype = ds.dtype
                dataset = h5_file.create_dataset(
                    dataset_name,
                    ds.shape,
                    dtype=dtype)
                dataset[...] = ds
