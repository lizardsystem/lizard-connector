import datetime
import urllib.parse

from lizard_connector import jsdatetime


class LizardApiImproperQueryError(Exception):
    pass


class QueryDictionary(dict):

    def update(self, E=None, *queries, **f):
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E is present and has a .keys() method, then does:  for k in E: D[k] = E[k]
        If E is present and lacks a .keys() method, then does:  for k, v in E: D[k] = v
        In either case, this is followed by: for k in F:  D[k] = F[k]
        """
        for k, v in f.items():
            self[k] = v
        queries = list(queries)
        if E and isinstance(E, str):
            for k, v in urllib.parse.parse_qsl(E.strip('?')):
                self[k] = v
        elif E:
            queries.append(E)
        for d in queries:
            try:
                for k, v in d.items():
                    self[k] = v
            except AttributeError:
                raise LizardApiImproperQueryError(
                    'Query {} is not a dictionary or a string'.format(E))


def commaify(*args):
    """
    :return: a comma-seperated string of the given arguments
    """
    return ','.join(str(x) for x in args)


def bbox(south_west, north_east):
    """
    Creates a bounding box in Well-known text (WKT).
    :param south_west: list or tuple with coordinates of the most south western
                       point of the bounding box of the form (lat, lon)
    :param north_east: list or tuple with coordinates of the most north eastern
                       point of the bounding box of the form (lat, lon)
    :return: bounding box polygon in Well-known text (WKT)
    """
    min_lat, min_lon = south_west
    max_lat, max_lon = north_east
    polygon_coordinates = [
            [min_lon, min_lat],
            [min_lon, max_lat],
            [max_lon, max_lat],
            [max_lon, min_lat],
            [min_lon, min_lat],
        ]
    points = [' '.join([str(x), str(y)]) for x, y in polygon_coordinates]
    return 'POLYGON ((' + ', '.join(points) + '))'


def in_bbox(south_west, north_east, endpoint=None):
    """
    Find all locations within a certain bounding box.
    returns records within bounding box using Bounding Box format (min Lon,
    min Lat, max Lon, max Lat). Also returns features with overlapping
    geometry.
    :param south_west: list or tuple with coordinates of the most south western
                       point of the bounding box of the form (lat, lon)
    :param north_east: list or tuple with coordinates of the most north eastern
                       point of the bounding box of the form (lat, lon)
    :return: a query dictionary.
    """
    query = "geom_within" if endpoint == 'timeseries' else "in_bbox"
    return QueryDictionary({query: bbox(south_west, north_east)})


def distance_to_point(distance, lat, lon):
    """
    Query for records with distance meters from a given point.
    Distance in meters is converted to WGS84 degrees and thus an approximation.
    :param distance: meters from point
    :param lon: longtitude of point
    :param lat: latitude of point
    :return: a query dictionary.
    """
    coords = commaify(lon, lat)
    return QueryDictionary(distance=distance, point=coords)


def datetime_limits(start=None, end=None):
    """
    Query for date time limits (start, end).
    :param start: start in python datetime.datetime format.
    :param end: end in python datetime.datetime format.
    :return: a query dictionary.
    """
    if not end:
        end = datetime.datetime.now()
    start = jsdatetime.datetime_to_js(start) if isinstance(
        start, datetime.datetime) else start
    end = jsdatetime.datetime_to_js(end) if isinstance(
        end, datetime.datetime) else end
    return QueryDictionary(start=start, end=end)


def organisation(organisation_id=None, endpoint=None):
    query_key = {
        None: "",
        "organisation": "",
        "location": "organisation__"
    }.get(endpoint, "location__organisation__") + "unique_id"

    org_query = QueryDictionary()
    if isinstance(organisation_id, str):
        org_query.update({query_key: organisation_id})
    elif organisation_id:
        org_query.update({query_key: ','.join(org for org in organisation_id)})
    return org_query


def statistics(*statistics):
    statistics = commaify(*[x if x != 'mean' else 'count,sum' for x in
                            statistics])
    return QueryDictionary(min_points=1, fields=statistics)


def feature_info(lat, lng, layername):
    return QueryDictionary(
        agg='curve',
        geom='POINT({lng}+{lat})'.format(lat=lat, lng=lng),
        srs='EPSG:4326',
        raster_names=layername,
        count=False
    )


def limits(layername, south_west, north_east):
    return QueryDictionary(
        request='getlimits',
        layers=layername,
        bbox=bbox(south_west, north_east),
        width=16,
        height=16,
        srs='epsg:4326'
    )


def search(q):
    return QueryDictionary(search=q)


groundwater = QueryDictionary(object_type__id= 107)

