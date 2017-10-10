from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators

import unittest

from lizard_connector.parsers import *


class ParseTestCase(unittest.TestCase):

    def test_parse_element(self):
        self.assertEqual(parse_element([{'uuid': 1}], 'uuid'), [1])

    def test_parse_uuid(self):
        self.assertEqual(parse_uuid([{'uuid': 1}]), [1])
