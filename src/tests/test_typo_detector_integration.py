import unittest
import tempfile
import shutil
import os
import sys
from unittest.mock import MagicMock, patch, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from commands.typo_detector import TypoDetector
from modules.typo_tracker import TypoTracker


class TestTypoDetectorIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test with temporary directory and mock environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Set required environment variables
        os.environ['TELEGRAM_TOKEN'] = 'test_token'
        os.environ['OPENAI_API_KEY'] = 'test_key'
        os.environ['OPENAI_API_BASE'] = 'test_base'
        
        # Mock OpenAI client to return YES for typo detection
        self.openai_patch = patch('commands.typo_detector.OpenAIClient')
        self.mock_openai = self.openai_patch.start()
        self.mock_openai.return_value.make_request.return_value = "YES"
        
        # Mock PrivacyManager
        self.privacy_patch = patch('commands.typo_detector.PrivacyManager')
        self.mock_privacy = self.privacy_patch.start()
        self.mock_privacy.return_value.anonymize_messages.return_value = ([], {})
        
        # Create detector with patched typo tracker using test directory
        with patch('commands.typo_detector.TypoTracker') as mock_tracker_class:
            mock_tracker_class.return_value = TypoTracker(self.test_dir)
            self.detector = TypoDetector()

    def tearDown(self):
        """Clean up test directory and stop patches."""
        shutil.rmtree(self.test_dir)
        
        # Clean up environment variables
        for key in ['TELEGRAM_TOKEN', 'OPENAI_API_KEY', 'OPENAI_API_BASE']:
            if key in os.environ:
                del os.environ[key]
        
        self.openai_patch.stop()
        self.privacy_patch.stop()
        
        # Reset Environment singleton
        from environment import Environment
        Environment._instances = {}

    def _create_mock_message(self, user_id, username, text, message_id=1, chat_id=123):
        """Create a mock Telegram message."""
        message = Mock()
        message.from_user.id = user_id
        message.text = text
        message.caption = None
        message.message_id = message_id
        message.chat_id = chat_id
        message.chat.type = "group"
        
        # Mock user
        user = Mock()
        user.id = user_id
        user.first_name = username
        message.from_user = user
        
        return message

    def _create_mock_update_context(self, message):
        """Create mock update and context for message processing."""
        update = Mock()
        update.message = message
        
        context = Mock()
        context.bot.send_chat_action = Mock()
        context.bot.send_message = Mock()
        
        return update, context

    def test_typo_detection_and_ranking(self):
        """Test complete typo detection workflow with ranking system."""
        chat_id = 123
        
        # Mock the authorization to return True
        with patch.object(self.detector, '_is_user_authorized', return_value=True):
            # Simulate multiple users making the same typo
            messages = [
                self._create_mock_message(1, "user1", "isso é traveção", 1, chat_id),
                self._create_mock_message(2, "user2", "concordo com traveção", 2, chat_id),
                self._create_mock_message(3, "user3", "sim traveção mesmo", 3, chat_id),
            ]
            
            # Process the messages to build up the buffer
            for i, message in enumerate(messages):
                update, context = self._create_mock_update_context(message)
                self.detector._process(update, context)
                
                # Only the third message should trigger (3 different users)
                if i == 2:
                    # Verify the response was sent
                    context.bot.send_message.assert_called_once()
                    call_args = context.bot.send_message.call_args[1]
                    
                    # Check that the response contains the expected elements
                    response_text = call_args['text']
                    
                    # Should contain the suspect (first user)
                    self.assertIn("user1", response_text)
                    self.assertIn("traveção", response_text)
                    
                    # Should contain the ranking header
                    self.assertIn("🏆 HERÓIS NACIONAIS", response_text)
                    
                    # Should show error count
                    self.assertIn("1 erro", response_text)
                    
                    # Should contain comedy achievement
                    self.assertIn("🤡 PARABÉNS GUYZ, COMEDY ACHIEVED! 🤡", response_text)

    def test_multiple_typos_ranking(self):
        """Test that ranking works correctly with multiple typos from different users."""
        chat_id = 123
        
        # Create typo tracker directly for this test
        tracker = TypoTracker(self.test_dir)
        
        # Add different numbers of typos for different users
        tracker.add_typo(1, "user1", "erro1")
        tracker.add_typo(1, "user1", "erro2")
        tracker.add_typo(1, "user1", "erro3")  # 3 errors
        
        tracker.add_typo(2, "user2", "erro1")
        tracker.add_typo(2, "user2", "erro2")  # 2 errors
        
        tracker.add_typo(3, "user3", "erro1")  # 1 error
        
        # Get top users
        top_users = tracker.get_top_users(3)
        
        # Verify ranking order
        self.assertEqual(len(top_users), 3)
        self.assertEqual(top_users[0], ("user1", 3))  # Most errors first
        self.assertEqual(top_users[1], ("user2", 2))
        self.assertEqual(top_users[2], ("user3", 1))


if __name__ == "__main__":
    unittest.main()