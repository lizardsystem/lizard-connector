__author__ = 'roel.vandenberg@nelen-schuurmans.nl'

import unittest
from lizard_connector.jsdatetime import *
import datetime
import re


class JavascriptDatetimeConverterTestCase(unittest.TestCase):

    datestring_regex = r"(0[1-9]|[12]\d|3[01])([- /.])(0{0,1}[1-9]|1[012])\2(" \
                r"19|20)\d\d"

    def test_todaystr(self):
        t = todaystr()
        self.assertIsInstance(t, str, "todaystr() doesn't return a string "
                                      "format.")
        self.assertRegexpMatches(t, self.datestring_regex,
                                 "not a valid date format")
        today_dt = datetime.datetime.strptime(t, '%d-%m-%Y').date()
        self.assertEqual(today_dt, datetime.datetime.now().date(),
                         "todaystr doesn't return today")

    def test_now_iso(self):
        t_iso = now_iso()
        rx = (r"(19|20)\d\d-(1[012]|0?[1-9])-(3[01]|2\d|0?[1-9])"   # date
              r"T(2[0-4]|[0-1]\d):([0-5]\d):([0-5]\d)Z")            # time
        self.assertRegexpMatches(t_iso, rx)

    def test_round_js_to_date(self):
        self.assertTrue(round_js_to_date(86400000))
        self.assertFalse(round_js_to_date(86399999), "")

    def test_js_epoch(self):
        self.assertEqual(JS_EPOCH, datetime.datetime(1970, 1, 1),
                         "JS_EPOCH is changed.")

    def test_datetime_to_js(self):
        self.assertFalse(datetime_to_js(JS_EPOCH))

    def test_js_to_datetime(self):
        self.assertEqual(js_to_datetime(0), JS_EPOCH)

    def test_datetime_to_datestring(self):
        date = datetime.datetime(1993, 12, 31)
        datestring = datetime_to_datestring(date)
        self.assertRegexpMatches(datestring, self.datestring_regex,
                        "datetime_to_datestring() does not return a valid "
                        "date string")
        self.assertEqual(datestring, "31-12-1993", "datetime_to_datestring() "
                                                   "conversion is corrupt")

    def test_datestring_to_js(self):
        self.assertFalse(datestring_to_js('01-01-1970'))


if __name__ == '__main__':
    unittest.main()
