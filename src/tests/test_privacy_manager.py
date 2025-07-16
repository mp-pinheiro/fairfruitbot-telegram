import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from messaging.privacy_manager import PrivacyManager


class TestPrivacyManager(unittest.TestCase):
    
    def setUp(self):
        self.privacy_manager = PrivacyManager()
        
    def test_anonymize_username(self):
        """Test username anonymization"""
        username = "testuser"
        hash_value = self.privacy_manager.anonymize_username(username)
        
        # Should return a hash starting with User_
        self.assertTrue(hash_value.startswith("User_"))
        self.assertNotEqual(hash_value, username)
        
        # Same username should get same hash
        hash_value2 = self.privacy_manager.anonymize_username(username)
        self.assertEqual(hash_value, hash_value2)
        
    def test_deanonymize_username(self):
        """Test username deanonymization"""
        username = "testuser"
        hash_value = self.privacy_manager.anonymize_username(username)
        original = self.privacy_manager.deanonymize_username(hash_value)
        
        self.assertEqual(original, username)
        
    def test_deanonymize_unknown_hash(self):
        """Test deanonymizing unknown hash returns None"""
        result = self.privacy_manager.deanonymize_username("unknown_hash")
        self.assertIsNone(result)
        
    def test_anonymize_empty_username(self):
        """Test anonymizing empty username"""
        result = self.privacy_manager.anonymize_username("")
        self.assertEqual(result, "User_anonymous")
        
        result = self.privacy_manager.anonymize_username(None)
        self.assertEqual(result, "User_anonymous")
        
    def test_anonymize_text(self):
        """Test text anonymization"""
        self.privacy_manager.anonymize_username("alice")
        self.privacy_manager.anonymize_username("bob")
        
        text = "alice said hello to bob"
        anonymized = self.privacy_manager.anonymize_text(text)
        
        # Should not contain original usernames
        self.assertNotIn("alice", anonymized)
        self.assertNotIn("bob", anonymized)
        
        # Should contain hash values
        alice_hash = self.privacy_manager.anonymize_username("alice")
        bob_hash = self.privacy_manager.anonymize_username("bob")
        self.assertIn(alice_hash, anonymized)
        self.assertIn(bob_hash, anonymized)
        
    def test_deanonymize_text(self):
        """Test text deanonymization"""
        alice_hash = self.privacy_manager.anonymize_username("alice")
        bob_hash = self.privacy_manager.anonymize_username("bob")
        
        anonymized_text = f"{alice_hash} said hello to {bob_hash}"
        deanonymized = self.privacy_manager.deanonymize_text(anonymized_text)
        
        # Should contain original usernames
        self.assertIn("alice", deanonymized)
        self.assertIn("bob", deanonymized)
        
        # Should not contain hash values
        self.assertNotIn(alice_hash, deanonymized)
        self.assertNotIn(bob_hash, deanonymized)
        
    def test_clear(self):
        """Test clearing all mappings"""
        self.privacy_manager.anonymize_username("testuser")
        self.assertEqual(self.privacy_manager.get_stats()["total_users"], 1)
        
        self.privacy_manager.clear()
        self.assertEqual(self.privacy_manager.get_stats()["total_users"], 0)
        
    def test_get_stats(self):
        """Test statistics"""
        stats = self.privacy_manager.get_stats()
        self.assertEqual(stats["total_users"], 0)
        
        self.privacy_manager.anonymize_username("user1")
        self.privacy_manager.anonymize_username("user2")
        
        stats = self.privacy_manager.get_stats()
        self.assertEqual(stats["total_users"], 2)
        
    def test_consistent_hashing(self):
        """Test that same username always gets same hash"""
        username = "consistent_user"
        
        pm1 = PrivacyManager()
        pm2 = PrivacyManager()
        
        hash1 = pm1.anonymize_username(username)
        hash2 = pm2.anonymize_username(username)
        
        # Different instances should produce the same hash for the same username
        self.assertEqual(hash1, hash2)


if __name__ == '__main__':
    unittest.main()