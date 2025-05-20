import unittest

from dict_helper import get_first_non_none_value


class TestDictHelper(unittest.TestCase):

    def test_get_first_non_none_value_1(self):
        data = {
            "id": "natsuki",
            "displayName": "ナツキ",
        }
        result = get_first_non_none_value(data, ["displayName", "id"])
        self.assertEqual("ナツキ", result)

    def test_get_first_non_none_value_2(self):
        data = {
            "id": "natsuki",
            "displayName": None,
        }
        result = get_first_non_none_value(data, ["displayName", "id"])
        self.assertEqual("natsuki", result)
