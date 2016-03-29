lizard-connector
================

Introduction
------------

Connector to Lizard api (e.g. https://demo.lizard.net/api/v2) for python.

Includes:
- Endpoints (Lizard api endoints, e.g. TimeseriesEndpoint)
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

    timeseries = lizard_connector.connector.Timeseries(
        username="example.username"
        password="example_password"
    )

    endpoint = 'timeseries'
    south_west = [48.0, -6.8]
    north_east = [56.2, 18.9]

    organisation_id = 'example_organisation_uuid'

    start = datetime.datetime(1970, 1, 1)
    end = datetime.datetime.now()

    relevant_queries = [
        lizard_connector.queries.in_bbox(south_west, north_east, endpoint),
        organisation(organisation_id, endpoint),
        datetime_limits(start, end)
    ]

    results = timeseries.download(relevant_queries)
