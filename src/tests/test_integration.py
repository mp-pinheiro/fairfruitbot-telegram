import unittest
import os
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from commands.typo_detector import TypoDetector
from commands.group_summary import GroupSummary
from messaging import get_shared_message_buffer


class TestMessageIntegration(unittest.TestCase):
    """Test that TypoDetector and GroupSummary properly share the MessageBuffer"""
    
    def setUp(self):
        # Clear the shared buffer before each test
        get_shared_message_buffer().clear()
        
    def tearDown(self):
        # Clean up after each test
        get_shared_message_buffer().clear()
        
    def test_shared_message_buffer(self):
        """Test that both components use the same MessageBuffer instance"""
        with patch.dict(os.environ, {
            'TELEGRAM_TOKEN': 'test_token',
            'SUMMARY_GROUP_IDS': '-1001467780714',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            # Create instances
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # They should share the same MessageBuffer instance
            self.assertIs(typo_detector._message_buffer, group_summary._message_buffer)
            
    def test_both_commands_store_to_same_buffer(self):
        """Test that messages stored by either command appear in the shared buffer"""
        with patch.dict(os.environ, {
            'TELEGRAM_TOKEN': 'test_token',
            'SUMMARY_GROUP_IDS': '-1001467780714',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Create a mock message
            mock_message = Mock()
            mock_message.text = "Test message from integration"
            mock_message.chat_id = -1001467780714
            mock_message.from_user.id = 123
            mock_message.from_user.username = "testuser"
            mock_message.from_user.first_name = "Test"
            mock_message.message_id = 456
            mock_message.date = Mock()
            
            # Store message through TypoDetector
            typo_detector._store_message(mock_message)
            
            # Both should see the same message count
            self.assertEqual(typo_detector._message_buffer.size(), 1)
            self.assertEqual(group_summary._message_buffer.size(), 1)
            
            # Both should see the same message content
            typo_messages = typo_detector._message_buffer.get_recent_messages()
            summary_messages = group_summary._message_buffer.get_recent_messages()
            
            self.assertEqual(len(typo_messages), 1)
            self.assertEqual(len(summary_messages), 1)
            self.assertEqual(typo_messages[0]["text"], "Test message from integration")
            self.assertEqual(summary_messages[0]["text"], "Test message from integration")
            
    def test_group_filtering_works_correctly(self):
        """Test that group filtering still works correctly with shared buffer"""
        with patch.dict(os.environ, {
            'TELEGRAM_TOKEN': 'test_token',
            'SUMMARY_GROUP_IDS': '-1001467780714',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Create messages from different groups
            target_message = Mock()
            target_message.text = "Message from target group"
            target_message.chat_id = -1001467780714  # Target group
            target_message.from_user.id = 123
            target_message.from_user.username = "testuser"
            target_message.from_user.first_name = "Test"
            target_message.message_id = 456
            target_message.date = Mock()
            
            other_message = Mock()
            other_message.text = "Message from other group"
            other_message.chat_id = -9999999  # Different group
            other_message.from_user.id = 124
            other_message.from_user.username = "otheruser"
            other_message.from_user.first_name = "Other"
            other_message.message_id = 457
            other_message.date = Mock()
            
            # Store both messages
            typo_detector._store_message(target_message)
            typo_detector._store_message(other_message)
            
            # Only the target group message should be stored
            self.assertEqual(typo_detector._message_buffer.size(), 1)
            messages = typo_detector._message_buffer.get_recent_messages()
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["text"], "Message from target group")
            
    def test_memory_efficiency_improvement(self):
        """Test that we're using less memory than before by sharing the buffer"""
        with patch.dict(os.environ, {
            'TELEGRAM_TOKEN': 'test_token',
            'SUMMARY_GROUP_IDS': '-1001467780714',
            'OPENAI_API_KEY': 'test_openai_key'
        }):
            typo_detector = TypoDetector()
            group_summary = GroupSummary()
            
            # Create multiple messages
            for i in range(10):
                mock_message = Mock()
                mock_message.text = f"Test message {i}"
                mock_message.chat_id = -1001467780714
                mock_message.from_user.id = 123 + i
                mock_message.from_user.username = f"user{i}"
                mock_message.from_user.first_name = f"User{i}"
                mock_message.message_id = 456 + i
                mock_message.date = Mock()
                
                # Store through TypoDetector - should be visible to GroupSummary too
                typo_detector._store_message(mock_message)
                
            # Both should see all 10 messages (not 20 as would be the case with separate buffers)
            self.assertEqual(typo_detector._message_buffer.size(), 10)
            self.assertEqual(group_summary._message_buffer.size(), 10)
            
            # Verify they're actually the same buffer (reference equality)
            self.assertIs(typo_detector._message_buffer, group_summary._message_buffer)


if __name__ == '__main__':
    unittest.main()