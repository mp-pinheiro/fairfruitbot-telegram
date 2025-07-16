import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock environment before importing any commands
@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'mock_token'})
def mock_environment():
    with patch('environment.Environment') as MockEnv:
        mock_env_instance = Mock()
        mock_env_instance.summary_group_ids = [-1001467780714]
        mock_env_instance.allowed_user_ids = []
        MockEnv.return_value = mock_env_instance
        return MockEnv


class TestIndependentBuffers(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton instances
        import modules
        modules.Singleton._instances = {}
        
    @patch('clients.OpenAIClient')  # Mock OpenAI client for GroupSummary
    def test_independent_buffer_behavior(self, mock_openai_client):
        """Test that TypoDetector and GroupSummary have independent buffers."""
        
        with mock_environment():
            from commands.typo_detector import TypoDetector
            from commands.group_summary import GroupSummary
            from messaging import BaseMessageBuffer
            
            # Create instances
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Verify they inherit from BaseMessageBuffer
            self.assertIsInstance(typo_detector, BaseMessageBuffer)
            self.assertIsInstance(group_summary, BaseMessageBuffer)
            
            # Verify they are different instances
            self.assertIsNot(typo_detector, group_summary)
            
            # Verify different buffer sizes
            self.assertEqual(typo_detector._buffer.maxlen, 50)  # TypoDetector optimized size
            self.assertEqual(group_summary._buffer.maxlen, 100)  # GroupSummary optimized size
            
            # Initially both should be empty
            self.assertEqual(typo_detector.size(), 0)
            self.assertEqual(group_summary.size(), 0)
            
    @patch('clients.OpenAIClient')
    def test_independent_message_storage(self, mock_openai_client):
        """Test that messages stored in one buffer don't affect the other."""
        
        with mock_environment():
            from commands.typo_detector import TypoDetector
            from commands.group_summary import GroupSummary
            
            # Reset singleton instances again to ensure clean state
            import modules
            modules.Singleton._instances = {}
            
            # Create instances
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Mock a message from the target group
            message = Mock()
            message.text = "Hello world test message"
            message.chat_id = -1001467780714  # Target group ID
            message.from_user.id = 123
            message.from_user.username = "testuser"
            message.from_user.full_name = "Test User"
            message.message_id = 456
            
            # Mock create_message_data
            with patch('utils.create_message_data') as mock_create:
                mock_create.return_value = {
                    "text": "Hello world test message",
                    "user_id": 123,
                    "user": "testuser",
                    "message_id": 456,
                    "chat_id": -1001467780714
                }
                
                # Store message in typo_detector
                result1 = typo_detector.store_message(message)
                self.assertTrue(result1)
                
                # typo_detector should have 1 message, group_summary should have 0
                self.assertEqual(typo_detector.size(), 1)
                self.assertEqual(group_summary.size(), 0)
                
                # Store message in group_summary
                result2 = group_summary.store_message(message)
                self.assertTrue(result2)
                
                # Now both should have 1 message, but they're independent
                self.assertEqual(typo_detector.size(), 1)
                self.assertEqual(group_summary.size(), 1)
                
                # Verify the messages are stored independently
                typo_messages = typo_detector.get_recent_messages()
                summary_messages = group_summary.get_recent_messages()
                
                self.assertEqual(len(typo_messages), 1)
                self.assertEqual(len(summary_messages), 1)
                self.assertEqual(typo_messages[0]["text"], "Hello world test message")
                self.assertEqual(summary_messages[0]["text"], "Hello world test message")
                
    @patch('clients.OpenAIClient')
    def test_different_buffer_capacities(self, mock_openai_client):
        """Test that different buffer capacities work as expected."""
        
        with mock_environment():
            from commands.typo_detector import TypoDetector
            from commands.group_summary import GroupSummary
            
            # Reset singleton instances
            import modules
            modules.Singleton._instances = {}
            
            # Create instances
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Fill typo_detector buffer beyond its capacity (50)
            with patch('utils.create_message_data') as mock_create:
                for i in range(55):  # More than typo_detector capacity
                    message = Mock()
                    message.text = f"Message {i}"
                    message.chat_id = -1001467780714
                    message.from_user.id = 123 + i
                    message.from_user.username = f"user{i}"
                    message.from_user.full_name = f"User {i}"
                    message.message_id = 456 + i
                    
                    mock_create.return_value = {
                        "text": f"Message {i}",
                        "user_id": 123 + i,
                        "user": f"user{i}",
                        "message_id": 456 + i,
                        "chat_id": -1001467780714
                    }
                    
                    typo_detector.store_message(message)
                
                # TypoDetector should only have 50 messages (its max capacity)
                self.assertEqual(typo_detector.size(), 50)
                
                # GroupSummary should still be empty
                self.assertEqual(group_summary.size(), 0)
                
                # The messages in typo_detector should be the latest ones (5-54)
                typo_messages = typo_detector.get_recent_messages()
                self.assertEqual(typo_messages[0]["text"], "Message 5")
                self.assertEqual(typo_messages[-1]["text"], "Message 54")
                
    @patch('clients.OpenAIClient')  
    def test_no_shared_state_performance_improvement(self, mock_openai_client):
        """Test that each command only processes its own messages, improving performance."""
        
        with mock_environment():
            from commands.typo_detector import TypoDetector
            from commands.group_summary import GroupSummary
            
            # Reset singleton instances
            import modules
            modules.Singleton._instances = {}
            
            # Create instances
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Add different numbers of messages to each
            with patch('utils.create_message_data') as mock_create:
                # Add 30 messages to typo_detector
                for i in range(30):
                    message = Mock()
                    message.text = f"Typo message {i}"
                    message.chat_id = -1001467780714
                    message.from_user.id = 100 + i
                    message.from_user.username = f"typouser{i}"
                    message.from_user.full_name = f"Typo User {i}"
                    message.message_id = 100 + i
                    
                    mock_create.return_value = {
                        "text": f"Typo message {i}",
                        "user_id": 100 + i,
                        "user": f"typouser{i}",
                        "message_id": 100 + i,
                        "chat_id": -1001467780714
                    }
                    
                    typo_detector.store_message(message)
                
                # Add 70 messages to group_summary
                for i in range(70):
                    message = Mock()
                    message.text = f"Summary message {i}"
                    message.chat_id = -1001467780714
                    message.from_user.id = 200 + i
                    message.from_user.username = f"summaryuser{i}"
                    message.from_user.full_name = f"Summary User {i}"
                    message.message_id = 200 + i
                    
                    mock_create.return_value = {
                        "text": f"Summary message {i}",
                        "user_id": 200 + i,
                        "user": f"summaryuser{i}",
                        "message_id": 200 + i,
                        "chat_id": -1001467780714
                    }
                    
                    group_summary.store_message(message)
                
                # Verify each has only its own messages
                self.assertEqual(typo_detector.size(), 30)
                self.assertEqual(group_summary.size(), 70)
                
                # Verify message content separation
                typo_messages = typo_detector.get_recent_messages()
                summary_messages = group_summary.get_recent_messages()
                
                # All typo messages should contain "Typo message"
                for msg in typo_messages:
                    self.assertIn("Typo message", msg["text"])
                    
                # All summary messages should contain "Summary message"
                for msg in summary_messages:
                    self.assertIn("Summary message", msg["text"])
                    
                # No cross-contamination
                for msg in typo_messages:
                    self.assertNotIn("Summary message", msg["text"])
                    
                for msg in summary_messages:
                    self.assertNotIn("Typo message", msg["text"])


if __name__ == '__main__':
    unittest.main()