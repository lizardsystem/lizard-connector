# coding=utf-8
"""
Connector to Lizard api (e.g. https://demo.lizard.net/api/v2) for python.

Includes:
- Datatypes (Rasters, Timeseries, Events, Assets), these are still a work in
  progress and experimental. In later versions these contain:
    - queryfunctions for special cases such as geographical queries and time
      related queries other queries can be input as a dictionary
    - parserfunctions to parse the json obtained from Endpoint queries
- Endpoints (Lizard api endoints)
- Connector (http handling)
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators

import json
import time
import sys
from threading import Thread, RLock

import lizard_connector.queries

if sys.version_info.major < 3:
    # py2
    from urllib import urlencode
    from urlparse import urljoin
    import urllib2 as urllib_request
    from urllib2 import urlopen
else:
    # py3
    from urllib.parse import urlencode
    from urllib.parse import urljoin
    import urllib.request as urllib_request
    from urllib.request import urlopen


ASYNC_POLL_TIME = 1
ASYNC_POLL_TIME_INCREASE = 1.5


class LizardApiTooManyResults(Exception):
    pass


class LizardApiAsyncTaskFailure(Exception):
    pass


class InvalidUrlError(Exception):
    pass


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


class Connector(object):

    def __init__(self, username=None, password=None):
        """
        Args:
            username (str): lizard-api user name to log in. Without one no
                            login is used.
            password (str): lizard-api password to log in. Without one no login
                            is used.
        """
        self.username = username
        self.password = password

    def get(self, url, raise_error_on_next_url=False):
        """
        GET a json from the api.

        Args:
            url (str): Lizard-api valid url.
            raise_error_on_next_url (bool): when provided an error is raised
                when a response contains a next_url field and the field is not
                null.
        Returns:
            A list of dictionaries of the 'results'-part of the api-response.
        """
        json_ = self.perform_request(url)
        if raise_error_on_next_url and bool(json_.get('next', False)):
            raise LizardApiTooManyResults(
                "\nThe Lizard API returns more than one result page. Please \n"
                "use `download_paginated` or `download_async` methods \n"
                "instead for large api responses. Or increase the page_size \n"
                "in the request parameters."
            )
        try:
            json_ = json_.get('results', json_)
        finally:
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
        return self.perform_request(url, data)

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
            a dictionary with the response.
        """
        if data:
            headers = self.header
            headers['content-type'] = "application/json"
            request_obj = urllib_request.Request(
                url,
                headers=headers,
                data=json.dumps(data).encode('utf-8'),
            )
        else:
            request_obj = urllib_request.Request(url, headers=self.header)
        resp = urlopen(request_obj)
        content = resp.read().decode('UTF-8')
        return json.loads(content)

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


class PaginatedRequest(object):

    def __init__(self, endpoint, url):
        """
        Args:
            endpoint (Endpoint): Endpoint object.
            url (str): First url to start the paginated request. This should
                be Lizard-api valid url.
        """
        self._endpoint = endpoint
        self.next_url = url
        self._count = None

    def _next_page(self):
        """
        GET a json from the api.

        Args:
            url (str): Lizard-api valid url.

        Returns:
            A list of dictionaries of the 'results'-part of the api-response.
        """
        json_ = self._endpoint.perform_request(self.next_url)
        self._count = json_.get('count')
        self.next_url = json_.get('next')
        json_ = json_.get('results', json_)
        return json_

    def next(self):
        """The next function for Python 2."""
        return self.__next__()

    @property
    def has_next_url(self):
        """
        Indicates whether other pages exist for this object.
        """
        return bool(self.next_url)

    def __len__(self):
        return self._count

    def __iter__(self):
        return self

    def __next__(self):
        """The next function for Python 3."""
        if self.has_next_url:
            return self._next_page()
        raise StopIteration


class Endpoint(Connector):

    def __init__(self, endpoint, base="https://demo.lizard.net", **kwargs):
        """
        Args:
            base (str): lizard-nxt url.
            username (str): lizard-api user name to log in. Without one no
                            login is used.
            password (str): lizard-api password to log in. Without one no login
                            is used.
        """
        super(Endpoint, self).__init__(**kwargs)
        self.endpoint = endpoint
        base = base.strip(r'/')
        if not base.startswith('https') and 'localhost' not in base:
            raise InvalidUrlError('base should start with https')
        base = urljoin(base, 'api/v2') + "/"
        self.base_url = urljoin(base, self.endpoint) + "/"

    def _build_url(self, page_size=1000, *querydicts, **queries):
        q = lizard_connector.queries.QueryDictionary(
            page_size=page_size)
        q.update(*querydicts, **queries)
        query = "?" + urlencode(q)
        return urljoin(self.base_url, query)

    def download(self, page_size=1000, *querydicts, **queries):
        """
        Query the api at this endpoint and download its data.

        For possible queries see: https://nxt.staging.lizard.net/doc/api.html
        Stores the api-response as a dict in the results attribute.

        Args:
            page_size (int): the page_size parameter when more results are
                returned than the page size allows an error is returned.
            querydicts (iterable): all key valuepairs from dictionaries are
                                   used as queries.
            queries (dict): all keyword arguments are used as queries.
        """
        url = self._build_url(page_size=page_size, *querydicts, **queries)
        return self.get(url, raise_error_on_next_url=True)

    def download_paginated(self, page_size=100, *querydicts, **queries):
        """
        Instantiates an iterable paginated request.

        The iterable returned has a length after first use. Example::

            end_point = Endpoint("sluices")
            paginated_request = end_point.download_paginated()
            len(paginated_request)  # this is None
            first_page = next(paginated_request)
            # this results in a number (the amount of available sluices):
            len(paginated_request)

        Args:
            querydicts (iterable): all key valuepairs from dictionaries are
                                   used as queries.
            page_size (int): number of results per iteration.
            queries (dict): all keyword arguments are used as queries.
        Returns:
            an iterable that returns the results of each page.
        """
        url = self._build_url(page_size=page_size, *querydicts, **queries)
        return PaginatedRequest(self, url)

    def download_async(self, call_back=None, lock=None, *querydicts,
                       **queries):
        """
        Downloads async via a Thread. A call_back function handles the results.

        By default download_async does make a call, but doesn't do anything. We
        provide a default method to save to file: save_to_json.

        Args:
            querydicts (iterable): all key valuepairs from dictionaries are
                                   used as queries.
            call_back (function): call back function that is called with the
                                  downloaded result
            lock (Lock): a threading lock. This lock is used when executing the
                         call back function.
            queries (dict): all keyword arguments are used as queries.
        """
        if call_back is None:
            call_back = no_op
        if lock is None:
            lock = RLock()
        args = (call_back, lock) + querydicts
        thread = Thread(
            target=self._async_worker,
            args=args,
            kwargs=queries
        )
        thread.start()

    def _poll_task(self, task_url):
        poll_result = self.get(task_url)
        task_status = poll_result.get("task_status")
        sleep_time = ASYNC_POLL_TIME
        if task_status == "PENDING":
            time.sleep(sleep_time)
            sleep_time *= ASYNC_POLL_TIME_INCREASE
            return None, True
        elif task_status == "SUCCESS":
            url = poll_result.get('result_url')
            return self.get(url), False
        raise LizardApiAsyncTaskFailure(task_status, task_url)

    def _async_worker(self, call_back, lock=None, *querydicts, **queries):
        """
        Starts a download as an api async task, but handles it synchronously.
        A call_back function handles the results.

        This function does not use threading and is provided to use in other
        threads or processes other than the Thread from the python standard
        library like QThread.

        By default async_worker does make a call, but doesn't do anything. We
        provide a default method to save to file: save_to_json.

        Args:
            querydicts (iterable): all key valuepairs from dictionaries are
                                   used as queries.
            call_back (function): call back function that is called with the
                                  downloaded result
            lock (Lock): a threading lock. This lock is used when executing the
                         call back function.
            queries (dict): all keyword arguments are used as queries.
        """
        result = self._synchronous_download_async(*querydicts, **queries)
        if lock:
            with lock:
                call_back(result)
        else:
            call_back(result)

    def _synchronous_download_async(self, *querydicts, **queries):
        queries.update({"async": "true"})
        page_size = queries.pop('page_size', 0)
        task_url = self.download(
            page_size=page_size, *querydicts, **queries).get('url')
        keep_polling = True
        result = None
        while keep_polling:
            result, keep_polling = self._poll_task(task_url)
        return result

    def upload(self, data, uuid=None):
        """
        Upload data to the api at this endpoint.

        Args:
            uuid (str): UUID of the object in the database you wish to store
                        data to.
            data (dict): Dictionary with the data to post to the api
        """
        if uuid:
            post_url = urljoin(urljoin(self.base_url, uuid), 'data')
        else:
            post_url = self.base_url
        return self.post(post_url, data)
