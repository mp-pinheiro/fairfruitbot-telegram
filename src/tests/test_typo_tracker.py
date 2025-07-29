import unittest
import tempfile
import shutil
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.typo_tracker import TypoTracker


class TestTypoTracker(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.tracker = TypoTracker(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_typo_and_get_stats(self):
        self.tracker.add_typo(123, "testuser", "traveção")
        
        stats = self.tracker.get_user_stats(123)
        self.assertEqual(stats["username"], "testuser")
        self.assertEqual(stats["total_errors"], 1)
        self.assertEqual(stats["typos"], ["traveção"])

    def test_get_top_users(self):
        self.tracker.add_typo(1, "user1", "erro1")
        self.tracker.add_typo(1, "user1", "erro2")
        self.tracker.add_typo(2, "user2", "erro1")
        
        top_users = self.tracker.get_top_users(2)
        
        self.assertEqual(len(top_users), 2)
        self.assertEqual(top_users[0], ("user1", 2))
        self.assertEqual(top_users[1], ("user2", 1))


if __name__ == "__main__":
    unittest.main()