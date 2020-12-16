lizard-connector
================

:warning: **Lizard API version 2 will deprecate on January 31th 2021, please switch to the default API version 3**

This can be done by either omitting the version parameter when creating a Client instance, or creating a Client instance with version 3 specified:

..
    from lizard_connector import Client
    cli = Client(version=3)


Introduction
------------

Connector to Lizard api (e.g. https://demo.lizard.net/api/v3) for python.

Includes:
- Client (experimental / alpha)
- Endpoint (Easy access to Lizard api endpoints)
- Connector (http handling)
- parsers to parse the json obtained from Endpoint queries
- queryfunctions for special cases such as geographical queries and time related queries other queries can be input as a dictionary
- callbacks for async data handling.

When pandas, numpy are installed the Client returns `pandas.DataFrame`s and/or
`numpy.array`s in a `ScientifResult` object.

Example usage
-------------

An example jupyter notebook can be found `Example_EN.ipynb` or in Dutch:
`Voorbeeld_NL.ipynb`.

Use one endpoints https://demo.lizard.net/api/v3 in Python with the Endpoint
class::

    from lizard_connector import Client
    import lizard_connector.queries
    import datetime

    # Fill in your username and password (your password will be prompted)
    client = lizard_connector.Client(
        username = "example.username"
    )

    endpoint = 'timeseries'
    south_west = [48.0, -6.8]
    north_east = [56.2, 18.9]

    organisation_id = 'example_organisation_uuid'

    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime.now()

    relevant_queries = [
        lizard_connector.queries.in_bbox(south_west, north_east, endpoint),
        lizard_connector.queries.organisation(organisation_id, endpoint),
        lizard_connector.queries.datetime_limits(start, end)
    ]

    results = client.timeseries.get(*relevant_queries)


Usage with PyQT (for Qgis plugins)
----------------------------------
You can create a QThread worker like so::

    from PyQt4.QtCore import QThread
    from PyQt4.QtCore import pyqtSignal


    class Worker(QThread):
        """This class creates a worker thread for getting the data."""
        output = pyqtSignal(object)

        def __init__(self, parent=None, endpoint=None, *querydicts, **queries):
            """Initiate the Worker."""
            super(Worker, self).__init__(parent)
            self._endpoint = endpoint
            self._querydicts = querydicts
            self._queries = queries

        def run(self):
            """Called indirectly by PyQt if you call start().
            This method retrieves the data from Lizard and emits it via the
            output signal as dictionary.
            """
            data = self._endpoint._synchronous_get_async(
                *self._querydicts, **self._queries)
            self.output.emit(data)
