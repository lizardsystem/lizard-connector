import unittest
import unittest.mock
from collections import Iterable

from lizard_connector.connector import *


class MockHeaders:

    def __init__(self, calls):
        self.calls = calls

    def get_content_charset(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return 'utf-8'


class MockUrlopen:

    def __init__(self):
        self.calls = []
        self.headers = MockHeaders(self.calls)

    def read(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return json.dumps({
            'count': 10,
            'next': 'next_url',
            'results': [{
                    'uuid': 1
                }]
        }).encode('utf-8')

    def assert_called_with(self, *args, **kwargs):
        return any(
            all(arg in called_args for arg in args) and
            all(kwarg in called_kwargs.items() for kwarg in kwargs.items())
            for called_args, called_kwargs in self.calls
        )

    def __call__(self, *args, **kwargs):
        return self

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        return False


class ConnectorTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_urlopen = MockUrlopen()
        self.connector = Connector()
        self.full_connector = Connector(max_results=1,
                                        password='123456',
                                        username='test.user')

    def __connector_test(self, connector_method, *args, **kwargs):
        with unittest.mock.patch(
                'lizard_connector.connector.urlopen', self.mock_urlopen):
            return connector_method(*args, **kwargs)

    def test_get(self):
        json_ = self.__connector_test(self.connector.get, 'https://test.nl')
        self.assertDictEqual(json_[0], {'uuid': 1})
        self.mock_urlopen.assert_called_with('https://test.nl', {})

    def test_post(self):
        self.__connector_test(self.connector.post, 'https://test.nl', {'data': 1})
        self.mock_urlopen.assert_called_with('https://test.nl', {})

    def test_request(self):
        json_ = self.__connector_test(
            self.connector.perform_request, 'https://test.nl')
        self.assertDictEqual(
            json_, {'count': 10, 'next': 'next_url', 'results': [{
                'uuid': 1}]}
        )

    def test_use_header(self):
        self.assertFalse(self.connector.use_header)
        self.assertTrue(self.full_connector.use_header)

    def test_header(self):
        self.assertDictEqual({}, self.connector.header)
        self.assertDictEqual({"username": 'test.user', "password": '123456'},
                             self.full_connector.header)


class EndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.connector_get = unittest.mock.Mock(return_value=[{'uuid': 1}])
        self.connector_post = unittest.mock.Mock(return_value=None)
        self.endpoint = self.__connector_test(Endpoint, base='https://test.nl',
                                              endpoint='test')
        self.endpoint.next_url = 'test'

    def __connector_test(self, connector_method, *args, **kwargs):
        with unittest.mock.patch('lizard_connector.connector.Connector.get',
                                 self.connector_get), \
                unittest.mock.patch(
                    'lizard_connector.connector.Connector.post',
                    self.connector_post):
            return connector_method(*args, **kwargs)

    def test_download(self):
        self.__connector_test(self.endpoint.download, q1=2)
        try:
            self.connector_get.assert_called_with(
                'https://test.nl/api/v2/test/?q1=2&page_size=1000')
        except AssertionError:
            self.connector_get.assert_called_with(
                'https://test.nl/api/v2/test/?page_size=1000&q1=2')

    def test_paginated_download(self):
        result = self.endpoint.download_paginated('testendpoint')
        self.assertIsInstance(result, Iterable)

    def test_async_download(self):
        # This throws an error. That is ok.
        self.__connector_test(self.endpoint.download_async, q1=2)
        success = False
        for x in ['https://test.nl/api/v2/test/?async=true&q1=2&page_size=1000',
                  'https://test.nl/api/v2/test/?async=true&page_size=1000&q1=2',
                  'https://test.nl/api/v2/test/?q1=2&async=true&page_size=1000',
                  'https://test.nl/api/v2/test/?page_size=1000&async=true&q1=2',
                  'https://test.nl/api/v2/test/?q1=2&page_size=1000&async=true',
                  'https://test.nl/api/v2/test/?page_size=1000&q1=2&async=true'
                  ]:
            try:
                self.connector_get.assert_called_with(x)
                success = True
            except AssertionError:
                pass
        self.assertTrue(success)

    def test_post(self):
        self.__connector_test(self.endpoint.upload, uuid="1", data={"a": 1})
        self.connector_post.assert_called_with(
            'https://test.nl/api/v2/test/data', {"a": 1})
        self.__connector_test(self.endpoint.upload, data={"a": 1})
        self.connector_post.assert_called_with(
            'https://test.nl/api/v2/test/', {"a": 1})


class PaginatedRequestTestcase(unittest.TestCase):

    def test_count(self):
        pass
        # self.connector_test(self.connector.get, 'https://test.nl')
        # self.assertEqual(self.connector.count, 10)

    def test_next_page(self):
        pass
        # self.connector_test(self.connector.get, 'https://test.nl')
        # self.assertEqual(self.connector.next_url, 'next_url')


class DataTypeTestCase(unittest.TestCase):

    def setUp(self):
        self.datatype = Datatype()
        class TestDatatype(Datatype):
            queries = {
                "testendpoint": {
                    "test": self.dummy
                }
            }
        self.datatype2 = TestDatatype()
        self.mock_urlopen = MockUrlopen()

    def dummy(self):
        return "test"

    def test_not_implemented(self):
        def testerror():
            self.datatype.queries
        self.assertRaises(NotImplementedError, testerror)

    def test_list_endpoints(self):
        self.assertEqual(self.datatype2.endpoints(), ['testendpoint'])

    def test_endpoints(self):
        self.assertEqual(self.datatype2.endpoint_queries('testendpoint'),
                         ['test'])

    def test_queries(self):
        self.assertEqual(
            self.datatype2.queries['testendpoint']['test'](), 'test')

    def test_download(self):
        with unittest.mock.patch(
                'lizard_connector.connector.urlopen', self.mock_urlopen):
            self.assertDictEqual((self.datatype2.download('testendpoint'))[0],
                              {'uuid': 1})


# TODO: More tests are required, but since the datatypes are experimental /
# TODO: still a work in progress further testing has been postponed.


class TimeseriesTestCase(unittest.TestCase):

    def setUp(self):
        self.ts = lizard_connector.connector.Timeseries()

    def test_queries(self):
        test_result = self.ts.queries['timeseries']['organisation']('test')
        expected_result = {'location__organisation__unique_id': 'test'}
        self.assertDictEqual(test_result, expected_result)


if __name__ == '__main__':
    unittest.main()
