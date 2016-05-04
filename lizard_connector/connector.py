# coding=utf-8
"""
Connector to Lizard api (e.g. https://demo.lizard.net/api/v2) for python.

Includes:
- Endpoints (Lizard api endoints, e.g. TimeseriesEndpoint)
- Connector (http handling)
- queryfunctions for special cases such as geographical queries and time
related queries other queries can be input as a dictionary
- parserfunctions to parse the json obtained from Endpoint queries
"""

import json
import urllib.request
import urllib.parse
import functools

import lizard_connector.queries


class LizardApiTooManyResults(Exception):
    pass


class Connector(object):

    def __init__(self, max_results=1000, username=None, password=None,
                 all_pages=True):
        """
        Args:
            max_results (int): maximum number of results allowed from one get.
            username (str): lizard-api user name to log in. Without one no
                            login is used.
            password (str): lizard-api password to log in. Without one no login
                            is used.
            all_pages (bool): when set to True, on get all pages are obtained.
                              When set to False only the first page is obtained
                              on get.
        """
        self.all_pages = all_pages
        self.max_results = max_results
        self.next_url = None
        self.count = None
        self.username = username
        self.password = password

    def get(self, url):
        """
        GET a json from the api.

        Args:
            url (str): Lizard-api valid url.

        Returns:
            A dictionary of the 'results'-part of the api-response.
        """
        json_ = json.loads(self.perform_request(url))
        self.count = json_.get('count')
        self.next_url = json_.get('next')
        json_ = json_.get('results', json_)
        count = self.count if self.count else 0

        if count > self.max_results:
            raise LizardApiTooManyResults(
                'Too many results: {} found, while max {} are accepted'.format(
                    count, self.max_results)
            )
        if self.all_pages:
            for extra_json in self:
                json_.update(extra_json.get('results', extra_json))
        return json_

    def post(self, url, data):
        """
        POST data to the api.

        Args:
            url (str): Lizard-api valid endpoint url.
            uuid (str): UUID of the object in the database you wish to store
                        data to.
            data (dict): Dictionary with the data to post to the api
        """
        return self.perform_request(url, data=json.dumps(data).encode('utf-8'))

    def perform_request(self, url, data=None):
        """
        GETs parameters from the Lizard api or POSTs data to the Lizard api.

        Defaults to GET request. Turns into a POST request if data is provided.

        Args:
            url (str): full query url: should be of the form:
                       [base_url]/api/v2/[endpoint]/?[query_key]=[query_value]&
                           ...
            data (dict): data in a list or dictionary format.

        Returns:
            the JSON from the response when no data is sent, else None.
        """
        if data:
            request_obj = urllib.request.Request(url, headers=self.header,
                                                 data=data, method="POST")
        else:
            request_obj = urllib.request.Request(url, headers=self.header)
        with urllib.request.urlopen(request_obj) as resp:
            encoding = resp.headers.get_content_charset()
            encoding = encoding if encoding else 'UTF-8'
            content = resp.read().decode(encoding)
            return content

    def next_page(self):
        """
        Returns next page if available else raises StopIteration.
        """
        return next(self)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.perform_request(self.next_url)
        except ValueError:
            raise StopIteration

    @property
    def use_header(self):
        """
        Indicates if header with login is used.
        """
        if self.username is None or self.password is None:
            return False
        return True

    @property
    def header(self):
        """
        The header with credentials for the api.
        """
        if self.use_header:
            return {
                "username": self.username,
                "password": self.password
            }
        return {}


class Endpoint(Connector):
    max_results = 1000

    def __init__(self, endpoint, base="https://demo.lizard.net", **kwargs):
        """
        Args:
            base (str): lizard-nxt url.
            max_results (int): maximum number of results allowed from one get.
            username (str): lizard-api user name to log in. Without one no
                            login is used.
            password (str): lizard-api password to log in. Without one no login
                            is used.
            all_pages (bool): when set to True, on download all pages are
                              obtained. When set to False only the first
                              page is obtained on get.
        """
        super().__init__(**kwargs)
        self.endpoint = endpoint
        base = base.strip(r'/')
        if not base.startswith('http'):
            base = 'https://' + base
        base = urllib.parse.urljoin(base, 'api/v2') + "/"
        self.base_url = urllib.parse.urljoin(base, self.endpoint) + "/"

    def download(self, *querydicts, **queries):
        """
        Query the api at this endpoint and download its data.

        For possible queries see: https://nxt.staging.lizard.net/doc/api.html
        Stores the api-response as a dict in the results attribute.

        Args:
            querydicts (iterable): all key valuepairs from dictionaries are
                                   used as queries.
            queries (dict): all keyword arguments are used as queries.
        """
        q = lizard_connector.queries.QueryDictionary(page_size=self.max_results
                                                     )
        q.update(*querydicts, **queries)
        query = "?" + urllib.parse.urlencode(q)
        url = urllib.parse.urljoin(self.base_url, query)
        return self.get(url)

    def upload(self, data, uuid=None):
        """
        Upload data to the api at this endpoint.

        Args:
            uuid (str): UUID of the object in the database you wish to store
                        data to.
            data (dict): Dictionary with the data to post to the api
        """
        if uuid:
            post_url = urllib.parse.urljoin(
                urllib.parse.urljoin(self.base_url, uuid),
                'data')
        else:
            post_url = self.base_url
        return self.post(post_url, data)

    @property
    def paginated(self):
        """
        Indicates whether this object is paginated (i.e. other pages exist).
        """
        return bool(self.next_url)


class Datatype(object):
    """
    Experimental class that forms the building block for data types.

    Each data type contains a list of queries for each relevant lizard-api
    endpoint. These are the only viable queries for each endpoint.
    """

    @property
    def queries(self):
        """
        This property needs to be implemented for the class to function.
        """
        raise NotImplementedError

    def list_endpoints(self):
        """Lists all available endpoints for this datatype."""
        return list(self.queries.keys())

    def download(self, endpoint, *querydicts, **queries):
        """Downloads a json as a dict from an endpoint."""
        endpoint_ = Endpoint(endpoint)
        return endpoint_.download(*querydicts, **queries)


class Timeseries(Datatype):
    queries = {
        "timeseries": {
            "in_bbox": functools.partial(
                lizard_connector.queries.in_bbox, endpoint="timeseries"),
            "distance_to_point":
                lizard_connector.lizard_connector.queries.distance_to_point,
            "datetime_limits": lizard_connector.queries.datetime_limits,
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="timeseries"),
            "statistics": lizard_connector.queries.statistics
        },
        "locations": {
            "in_bbox": functools.partial(
                lizard_connector.queries.in_bbox, endpoint="timeseries"),
            "distance_to_point": lizard_connector.queries.distance_to_point,
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="locations")
        }
    }


class Rasters(Datatype):
    queries = {
        "rasters": {
            "feature_info": lizard_connector.queries.feature_info,
            "limits": lizard_connector.queries.limits,
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="rasters")
        }
    }


class Events(Datatype):
    queries = {
        "events": {
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="events")
        }
    }


class Assets(Datatype):
    queries = {
        "leveerings": {
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="leveerings")
        },
        "levees": {
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="levees")
        },
        "leveesections": {
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="leveesections"
            )
        },
        "leveezones": {
            "organisation": functools.partial(
                lizard_connector.queries.organisation, endpoint="leveezones")
        }
    }
