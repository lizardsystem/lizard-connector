# coding=utf-8
"""
Connector to Lizard api (e.g. https://demo.lizard.net/api/v2) for python.

Includes:
- Endpoints (Lizard api endoints, e.g. TimeseriesEndpoint)
- Fetcher (http handling)
- queryfunctions for special cases such as geographical queries and time
related queries other queries can be input as a dictionary
- parserfunctions to parse the json obtained from Endpoint queries
"""

import json
import urllib.request
import urllib.parse

from lizard_connector.query import QueryDictionary


class LizardApiTooManyResults(Exception):
    pass


class Fetcher(object):

    def __init__(self, endpoint, base="https://demo.lizard.net",
                 max_results=1000, username=None, password=None,
                 all_pages=True):
        """
        :param max_results: maximum number of results allowed from one get.
        :param username: lizard-api user name to log in. Without one no login
            is used.
        :param password: lizard-api password to log in. Without one no login
            is used.
        :param all_pages: when set to True, on get all pages are obtained.
            When set to False only the first page is obtained on get.
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
        :param url: Lizard-api valid url.
        :return: a dictionary of the 'results'-part of the api-response.
        """
        json_ = self.request(url)
        self.count = json_.get('count')
        self.next_url = json_.get('next')
        json_ = json_.get('results', json_)
        count = self.count if self.count else 0

        if count > self.max_results:
            raise LizardApiTooManyResults(
                'Too many results: {} found, while max {} are accepted'.format(
                json_.get('count', '?'), self.max_results)
            )
        if self.all_pages:
            for extra_json in self:
                json_.update(extra_json.get('results', extra_json))
        return json_

    def post(self, url, uuid, data):
        """
        POST data to the api.
        :param url: Lizard-api valid endpoint url.
        :param uuid: UUID of the object in the database you wish to store
                     data to.
        :param data: Dictionary with the data to post to the api
        """
        post_url = urllib.parse.urljoin(urllib.parse.urljoin(url, str(uuid)),
                                        'data')
        self.request(post_url, data=json.dumps(data))

    def request(self, url, data=None):
        """
        GETs parameters from the Lizard api or POSTs data to the Lizard api.
        Defaults to GET request. Turns into a POST request if data is provided.

        :param url: full query url: should be of the form:
                    [base_url]/api/v2/[endpoint]/?[query_key]=[query_value]&...
        :param data: data in a list or dictionary format.
        :return: the JSON from the response when no data is sent, else None.
        """
        if data:
            request_obj = urllib.request.Request(url, headers=self.header,
                                                 data=data)
        else:
            request_obj = urllib.request.Request(url, headers=self.header)
        with urllib.request.urlopen(request_obj) as resp:
            if not data:
                encoding = resp.headers.get_content_charset()
                encoding = encoding if encoding else 'UTF-8'
                content = resp.read().decode(encoding)
                return json.loads(content)

    def next_page(self):
        """
        Returns next page if available else raises StopIteration.
        """
        return next(self)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.request(self.next_url)
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


def parse_element(json_, element):
    """
    Get a list of a certain element from the root of the results attribute.

    :param json: json from the Lizard api parsed into a dictionary.
    :param element: the element you wish to get.
    :return: A list of all elements in the root of the results attribute.
    """
    return [x[element] for x in json_]


def parse_uuid(json_, endpoint=None):
    """
    Get a list of a certain element from the root of the results attribute.

    :param json: json from the Lizard api parsed into a dictionary.
    :param endpoint: endpoint you wish to query.
    :return: A list of all uuid elements in the root of the results attribute.
    """
    uuid = 'unique_id' if endpoint == 'organisations' else 'uuid'
    return parse_element(json_, uuid)


class Endpoint(object):
    max_results = 1000
    endpoint = ""

    def __init__(self, base, **kwargs):
        """
        :param base: lizard-nxt url.
        """
        self.fetcher = Fetcher(
            endpoint=self.endpoint,
            max_results=self.max_results,
            **kwargs
        )
        base = base.strip(r'/')
        if not base.startswith('http'):
            base = 'https://' + base
        base = urllib.parse.urljoin(base, 'api/v2')
        self.base_url = urllib.parse.urljoin(base, self.endpoint) + "/"

    def get(self, *querydicts, **queries):
        """
        Query the api at this endpoint.
        For possible queries see: https://nxt.staging.lizard.net/doc/api.html
        Stores the api-response as a dict in the results attribute.

        :param querydicts: all key valuepairs from dictionaries are used as
            queries.
        :param queries: all keyword arguments are used as queries.
        :return:
        """
        q = QueryDictionary(page_size=self.max_results)
        q.update(*querydicts, **queries)
        query = "?" + urllib.parse.urlencode(q)
        url = urllib.parse.urljoin(self.base_url, query)
        return self.fetcher.get(url)

    def post(self, uuid, data):
        """
        POST data to the api at this endpoint.
        :param uuid: UUID of the object in the database you wish to store
                     data to.
        :param data: Dictionary with the data to post to the api
        """
        self.fetcher.post(self.base_url, uuid, data)

    @property
    def paginated(self):
        """
        Indicates whether this object is paginated (i.e. other pages exist).
        """
        return bool(self.fetcher.next_url)

    @property
    def count(self):
        """
        Number of results.
        """
        return self.fetcher.count


class Annotations(Endpoint):
    endpoint = 'annotations'


class CollageItems(Endpoint):
    endpoint = 'collageitems'


class Collages(Endpoint):
    endpoint = 'collages'


class Dashboards(Endpoint):
    endpoint = 'dashboards'


class Domains(Endpoint):
    endpoint = 'domains'


class Events(Endpoint):
    endpoint = 'events'


class EventSeries(Endpoint):
    endpoint = 'eventseries'


class Favourites(Endpoint):
    endpoint = 'favourites'


class FixedDrainageLevelAreas(Endpoint):
    endpoint = 'fixeddrainagelevelareas'


class Geocode(Endpoint):
    endpoint = 'geocode'


class Inbox(Endpoint):
    endpoint = 'inbox'


class Layers(Endpoint):
    endpoint = 'layers'


class LeveeReferencePoints(Endpoint):
    endpoint = 'leveereferencepoints'


class LeveeRings(Endpoint):
    endpoint = 'leveerings'


class Levees(Endpoint):
    endpoint = 'levees'


class LeveeSections(Endpoint):
    endpoint = 'leveesections'


class LeveeZones(Endpoint):
    endpoint = 'leveezones'


class Locations(Endpoint):
    endpoint = 'locations'


class OpticalFibers(Endpoint):
    endpoint = 'opticalfibers'


class Organisations(Endpoint):
    endpoint = 'organisations'


class ParameterReferencedUnits(Endpoint):
    endpoint = 'parameterreferencedunits'


class Polders(Endpoint):
    endpoint = 'polders'


class Rasters(Endpoint):
    endpoint = 'rasters'


class Regions(Endpoint):
    endpoint = 'regions'


class Scenario(Endpoint):
    endpoint = 'scenario'


class Scenarios(Endpoint):
    endpoint = 'scenarios'


class Search(Endpoint):
    endpoint = 'search'


class Timeseries(Endpoint):
    endpoint = 'timeseries'


class Users(Endpoint):
    endpoint = 'users'


class Workspaces(Endpoint):
    endpoint = 'workspaces'


class Wms(Endpoint):
    endpoint = 'wms'
