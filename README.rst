lizard-connector
================

Introduction
------------

Connector to Lizard api (e.g. https://demo.lizard.net/api/v2) for python.

Includes:
- Datatypes (experimental / alpha)
- Endpoint (Easy access to Lizard api endpoints)
- Connector (http handling)
- queryfunctions for special cases such as geographical queries and time
related queries other queries can be input as a dictionary
- parserfunctions to parse the json obtained from Endpoint queries


Example usage
-------------

Use one endpoints https://demo.lizard.net/api/v2 in Python with the Endpoint
class::

    import lizard_connector
    import datetime

    # Fill in your username and password
    timeseries = lizard_connector.connector.Endpoint(
        username = "example.username",
        password = "example_password",
        endpoint = 'timeseries'
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

    results = timeseries.download(*relevant_queries)


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
            data = self._endpoint._synchronous_download_async(
                *self._querydicts, **self._queries)
            self.output.emit(data)
