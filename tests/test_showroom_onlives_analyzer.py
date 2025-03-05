import unittest

from config_helper import read_config
from showroom_onlives_analyzer import ShowroomOnlivesAnalyzer


class TestShowroomOnlivesAnalyzer(unittest.TestCase):
    ONLIVES_JSON = read_config("test_data/onlives.json")

    def test_get_live(self):
        soa = ShowroomOnlivesAnalyzer()
        soa.merge(self.ONLIVES_JSON)

        live = soa.get_live("ナツキソのゲームメメント")
        self.assertEqual(544593, live["room_id"])
