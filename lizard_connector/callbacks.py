# coding=utf-8
import json
import time
import pickle

FILE_BASE = "api_result"
H5_DATASET_NAME_DATA = "data"
H5_DATASET_NAME_METADATA = "metadata"
H5_DATASET_NAMES = (
    H5_DATASET_NAME_METADATA,
    H5_DATASET_NAME_DATA,
)


def no_op(*args, **kwargs):
    pass


def save_to_json(result):
    """
    Saves a result to json with a timestamp in milliseconds.

    Use with json parser.

    Args:
        result (list|dict): a json dumpable object to save to file.
        file_base (str): filename base. Can contain a relative or absolute
                         path.
    """
    filename = "{}_{}.json".format(FILE_BASE, str(int(time.time() * 1000)))
    with open(filename, 'w') as json_filehandler:
        json.dump(result, json_filehandler)


def save_to_pickle(result):
    """
    Pickle a result to file with a timestamp in milliseconds.

    Use with json parser.

    Args:
        result (list|dict): a python serializable object to save to file.
        file_base (str): filename base. Can contain a relative or absolute
                         path.
    """
    filename = "{}_{}.p".format(FILE_BASE, str(int(time.time() * 1000)))
    with open(filename, 'w') as pickle_filehandler:
        pickle.dump(result, pickle_filehandler)


def save_to_hdf5(result):
    """
    Saves a result to hdf5 file with a timestamp in milliseconds.

    Use with scientific parser. HDF5 library should be installed.

    Args:
        result ([pandas.DataFrame|numpy.array]): a json dumpable object to save to file.
        file_base (str): filename base. Can contain a relative or absolute
                         path.
    """
    filename = "{}_{}.h5".format(FILE_BASE, str(int(time.time() * 1000)))

    # h5py is only required when using this callback. So we import here.
    import h5py
    with h5py.File(filename, "w", libver='latest') as h5_file:
        for i, dataset_data in enumerate(result):
            dataset = h5_file.create_dataset(
                H5_DATASET_NAMES[i],
                dataset_data.shape,
                dtype=dataset_data.dtype)
            dataset[...] = dataset_data
