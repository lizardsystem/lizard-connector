import unittest

from lizard_connector.queries import *


class QueryDictionaryTestCase(unittest.TestCase):

    def test_update(self):
        q = QueryDictionary()
        self.assertIsInstance(q, dict)
        q.update(a=2, b=3)
        self.assertDictEqual({"a": 2, "b": 3}, q)
        q.update('?a=1&b=2', {"c": 3}, d=4)
        self.assertDictEqual({"a": "1", "b": "2", "c": 3, "d": 4}, q)


class QueriesTestCase(unittest.TestCase):

    def test_commaify(self):
        self.assertEqual(commaify(1, '2,3', 4), '1,2,3,4')

    def test_bbox(self):
        self.assertEqual(bbox([0,1], [2,3]),
                         'POLYGON ((1 0, 1 2, 3 2, 3 0, 1 0))')

    def test_wkt_polygon(self):
        bbox = wkt_polygon([[1, 0], [1, 2]])
        self.assertEqual(bbox, 'POLYGON ((1 0, 1 2))')

    def test_wkt_point(self):
        bbox = wkt_point(0, 1)
        self.assertEqual(bbox, 'POINT (0 1)')


    def test_in_bbox(self):
        bbox = in_bbox([0,1], [2,3])
        self.assertDictEqual(bbox,
            {'in_bbox': 'POLYGON ((1 0, 1 2, 3 2, 3 0, 1 0))'})

    def test_distance_to_point(self):
        q = distance_to_point(3, 2, 1)
        self.assertDictEqual(q, {'distance': 3, 'point': '1,2'})

    def test_datetime_limits(self):
        q = datetime_limits(start=datetime.datetime(2004, 1, 2),
                            end=datetime.datetime(2014, 1, 3))
        self.assertDictEqual(q, {'start': 1073001600000, 'end': 1388707200000})

    def test_organisation(self):
        self.assertDictEqual(organisation('1', 'test'),
                             {'location__organisation__unique_id': '1'})
        self.assertDictEqual(organisation('1', 'organisation'),
                             {'unique_id': '1'})
        self.assertDictEqual(organisation('1', 'location'),
                             {'organisation__unique_id': '1'})

    def test_statistics(self):
        self.assertDictEqual(statistics('min', 'max'),
                             {'min_points': 1, 'fields': 'min,max'})
        self.assertDictEqual(statistics('min', 'mean'),
                             {'min_points': 1, 'fields': 'min,count,sum'})

    def test_feature_info(self):
        self.assertDictEqual(
            feature_info(0, 1, 'test'), {
                'srs': 'EPSG:4326',
                'geom': 'POINT(1+0)',
                'count': False,
                'raster_names': 'test',
                'agg': 'curve'
            })

    def test_limits(self):
        self.assertDictEqual(
            limits('test', [0,1], [2,3]), {
                'srs': 'epsg:4326',
                'height': 16,
                'bbox': 'POLYGON ((1 0, 1 2, 3 2, 3 0, 1 0))',
                'request': 'getlimits',
                'layers': 'test',
                'width': 16
            })

if __name__ == '__main__':
    unittest.main()
