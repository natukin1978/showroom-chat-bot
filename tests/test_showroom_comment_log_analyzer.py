import unittest

from config_helper import read_config
from showroom_comment_log_analyzer import ShowroomCommentLogAnalyzer


class TestShowroomCommentLogAnalyzer(unittest.TestCase):
    COMMENT_LOG_JSON = read_config("test_data/comment_log.json")

    def test_get_new_comments(self):
        scla = ShowroomCommentLogAnalyzer()
        scla.merge(self.COMMENT_LOG_JSON)

        comments = scla.get_new_comments()
        self.assertEqual(5, len(comments))
        comments = scla.get_new_comments()
        self.assertEqual(0, len(comments))
        scla.latest_created_at = 1740935077
        comments = scla.get_new_comments()
        self.assertEqual(3, len(comments))
