import unittest
import unittest.mock
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
                    'uuid':1
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


class FetcherTestCase(unittest.TestCase):

    def setUp(self):
        self.mock_urlopen = MockUrlopen()
        self.fetcher = Fetcher(endpoint='test')
        self.full_fetcher = Fetcher(endpoint='test',
                                    max_results=1,
                                    password='123456',
                                    username='test.user')

    def fetcher_test(self, fetcher_method, *args, **kwargs):
        with unittest.mock.patch('urllib.request.urlopen', self.mock_urlopen) \
                as mock_response:
            return fetcher_method(*args, **kwargs)

    def test_get(self):
        json_ = self.fetcher_test(self.fetcher.get, 'http://test.nl')
        self.assertDictEqual(json_[0], {'uuid': 1})
        self.mock_urlopen.assert_called_with('http://test.nl', {})

    def test_post(self):
        self.fetcher_test(self.fetcher.post, 'http://test.nl', '1',
                          {'data': 1})
        self.mock_urlopen.assert_called_with('http://test.nl', {})

    def test_request(self):
        json_ = self.fetcher_test(self.fetcher.request, 'http://test.nl')
        self.assertDictEqual(
            json_, {'count': 10, 'next': 'next_url', 'results': [{'uuid': 1}]}
        )

    def test_count(self):
        self.fetcher_test(self.fetcher.get, 'http://test.nl')
        self.assertEqual(self.fetcher.count, 10)

    def test_next_page(self):
        self.fetcher_test(self.fetcher.get, 'http://test.nl')
        self.assertEqual(self.fetcher.next_url, 'next_url')

    def test_use_header(self):
        self.assertFalse(self.fetcher.use_header)
        self.assertTrue(self.full_fetcher.use_header)

    def test_header(self):
        self.assertDictEqual({}, self.fetcher.header)
        self.assertDictEqual({"username": 'test.user', "password": '123456'},
                             self.full_fetcher.header)


class ParseTestCase(unittest.TestCase):

    def test_parse_element(self):
        self.assertEqual(parse_element([{'uuid': 1}], 'uuid'), [1])

    def test_parse_uuid(self):
        self.assertEqual(parse_uuid([{'uuid': 1}]), [1])


class EndpointTestCase(unittest.TestCase):

    def setUp(self):
        self.fetcher_get = unittest.mock.Mock(return_value=[{'uuid': 1}])
        self.fetcher_post = unittest.mock.Mock(return_value=None)
        self.endpoint = self.fetcher_test(Endpoint,
                                          base='http://test.nl')
        self.endpoint.fetcher.count = 3
        self.endpoint.fetcher.next_url = 'test'

    def fetcher_test(self, fetcher_method, *args, **kwargs):
        with unittest.mock.patch('lizard_connector.connector.Fetcher.get',
                                 self.fetcher_get) as fg, \
                unittest.mock.patch('lizard_connector.connector.Fetcher.post',
                                    self.fetcher_post) as fp:
            return fetcher_method(*args, **kwargs)

    def test_get(self):
        self.fetcher_test(self.endpoint.get, q1=2)
        try:
            self.fetcher_get.assert_called_with(
                'http://test.nl/api/v2/?q1=2&page_size=1000')
        except AssertionError:
            self.fetcher_get.assert_called_with(
                'http://test.nl/api/v2/?page_size=1000&q1=2')

    def test_post(self):
        self.fetcher_test(self.endpoint.post, uuid=1, data={"a": 1})
        self.fetcher_post.assert_called_with('http://test.nl/api/v2/', 1,
                                             {"a": 1})

    def test_paginated(self):
        self.assertEqual(self.endpoint.paginated, True)

    def test_count(self):
        self.assertEqual(self.endpoint.count, 3)


if __name__ == '__main__':
    unittest.main()