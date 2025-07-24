import unittest
import tempfile
import shutil
import os
import sys
from unittest.mock import MagicMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.typo_tracker import TypoTracker


class TestTypoTracker(unittest.TestCase):
    def setUp(self):
        """Set up test with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.tracker = TypoTracker(self.test_dir)

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_add_typo_new_user(self):
        """Test adding typo for a new user."""
        self.tracker.add_typo(123, "testuser", "traveção")
        
        stats = self.tracker.get_user_stats(123)
        self.assertEqual(stats["username"], "testuser")
        self.assertEqual(stats["total_errors"], 1)
        self.assertEqual(stats["typos"], ["traveção"])

    def test_add_multiple_typos(self):
        """Test adding multiple typos for same user."""
        self.tracker.add_typo(123, "testuser", "traveção")
        self.tracker.add_typo(123, "testuser", "mudno")
        
        stats = self.tracker.get_user_stats(123)
        self.assertEqual(stats["total_errors"], 2)
        self.assertEqual(len(stats["typos"]), 2)

    def test_get_top_users(self):
        """Test ranking functionality."""
        # Add users with different error counts
        self.tracker.add_typo(1, "user1", "erro1")
        self.tracker.add_typo(1, "user1", "erro2")
        self.tracker.add_typo(1, "user1", "erro3")  # 3 errors
        
        self.tracker.add_typo(2, "user2", "erro1")
        self.tracker.add_typo(2, "user2", "erro2")  # 2 errors
        
        self.tracker.add_typo(3, "user3", "erro1")  # 1 error
        
        top_users = self.tracker.get_top_users(3)
        
        # Should be sorted by error count (descending)
        self.assertEqual(len(top_users), 3)
        self.assertEqual(top_users[0], ("user1", 3))
        self.assertEqual(top_users[1], ("user2", 2))
        self.assertEqual(top_users[2], ("user3", 1))

    def test_get_top_users_limit(self):
        """Test limiting top users results."""
        for i in range(5):
            self.tracker.add_typo(i, f"user{i}", "erro")
        
        top_users = self.tracker.get_top_users(2)
        self.assertEqual(len(top_users), 2)


if __name__ == "__main__":
    unittest.main()