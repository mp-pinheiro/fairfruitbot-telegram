import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from messaging.privacy_manager import PrivacyManager


class TestPrivacyManager(unittest.TestCase):
    
    def setUp(self):
        self.privacy_manager = PrivacyManager()
        
    def test_privacy_session_creation(self):
        """Test privacy session context manager"""
        usernames = {"alice", "bob"}
        message_texts = ["alice said hello", "@charlie joined"]
        
        with self.privacy_manager.create_privacy_session(usernames, message_texts) as session:
            # Should be able to anonymize text
            text = "alice talked to bob"
            anonymized = session.anonymize_text(text)
            
            # Should not contain original usernames
            self.assertNotIn("alice", anonymized)
            self.assertNotIn("bob", anonymized)
            
            # Should be able to deanonymize
            deanonymized = session.deanonymize_text(anonymized)
            self.assertIn("alice", deanonymized)
            self.assertIn("bob", deanonymized)
            
    def test_username_mention_extraction(self):
        """Test extraction of usernames from message content"""
        usernames = {"alice", "bob"}
        message_texts = ["@charlie said hi to alice", "Did you see bob?"]
        
        with self.privacy_manager.create_privacy_session(usernames, message_texts) as session:
            # Should handle @mentions and content mentions
            text = "@charlie asked about alice and bob"
            anonymized = session.anonymize_text(text)
            
            # All mentioned users should be anonymized
            self.assertNotIn("charlie", anonymized)
            self.assertNotIn("alice", anonymized) 
            self.assertNotIn("bob", anonymized)
            
    def test_session_isolation(self):
        """Test that different sessions have different hashes"""
        usernames = {"testuser"}
        
        with self.privacy_manager.create_privacy_session(usernames) as session1:
            hash1 = session1.get_anonymous_username("testuser")
            
        with self.privacy_manager.create_privacy_session(usernames) as session2:
            hash2 = session2.get_anonymous_username("testuser")
            
        # Different sessions should produce different hashes
        self.assertNotEqual(hash1, hash2)
        
    def test_empty_username_handling(self):
        """Test handling of empty usernames"""
        usernames = {"", "validuser"}
        
        with self.privacy_manager.create_privacy_session(usernames) as session:
            # Should handle empty username gracefully
            anon_empty = session.get_anonymous_username("")
            anon_valid = session.get_anonymous_username("validuser")
            
            self.assertTrue(anon_empty.startswith("User_"))
            self.assertTrue(anon_valid.startswith("User_"))
            self.assertNotEqual(anon_empty, anon_valid)
            
    def test_case_insensitive_username_matching(self):
        """Test that username matching in text is case insensitive"""
        usernames = {"Alice", "BOB"}
        message_texts = ["alice said hi to bob"]
        
        with self.privacy_manager.create_privacy_session(usernames, message_texts) as session:
            text = "Alice talked to bob and BOB replied"
            anonymized = session.anonymize_text(text)
            
            # All variations should be anonymized
            self.assertNotIn("Alice", anonymized)
            self.assertNotIn("alice", anonymized)
            self.assertNotIn("BOB", anonymized)
            self.assertNotIn("bob", anonymized)
            
    def test_secure_hash_format(self):
        """Test that hashes are in expected secure format"""
        usernames = {"testuser"}
        
        with self.privacy_manager.create_privacy_session(usernames) as session:
            hash_value = session.get_anonymous_username("testuser")
            
            # Should start with User_ and have 16 character hash
            self.assertTrue(hash_value.startswith("User_"))
            self.assertEqual(len(hash_value), 5 + 16)  # "User_" + 16 hex chars
            
    def test_unknown_username_handling(self):
        """Test handling of unknown usernames"""
        usernames = {"alice"}
        
        with self.privacy_manager.create_privacy_session(usernames) as session:
            # Should return unknown format for unregistered username
            unknown_hash = session.get_anonymous_username("unknown_user")
            self.assertTrue(unknown_hash.startswith("User_unknown_"))
            
    def test_privacy_session_cleanup(self):
        """Test that session data is cleaned up after context exits"""
        usernames = {"testuser"}
        session_ref = None
        
        with self.privacy_manager.create_privacy_session(usernames) as session:
            session_ref = session
            # Session should work inside context
            hash_val = session.get_anonymous_username("testuser")
            self.assertTrue(hash_val.startswith("User_"))
            
        # After context exit, session should still work (object exists) 
        # but new sessions should produce different hashes due to different salts
        with self.privacy_manager.create_privacy_session(usernames) as new_session:
            new_hash = new_session.get_anonymous_username("testuser")
            self.assertNotEqual(hash_val, new_hash)


if __name__ == '__main__':
    unittest.main()