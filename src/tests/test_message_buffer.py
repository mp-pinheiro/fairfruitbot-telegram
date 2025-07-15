import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from messaging.message_buffer import MessageBuffer


class TestMessageBuffer(unittest.TestCase):
    
    def setUp(self):
        # Clear the singleton instance before each test
        MessageBuffer._instances = {}
        self.buffer = MessageBuffer(max_size=5)
        
    def tearDown(self):
        # Clean up after each test
        MessageBuffer._instances = {}
        
    def test_singleton_behavior(self):
        """Test that MessageBuffer follows singleton pattern"""
        buffer1 = MessageBuffer()
        buffer2 = MessageBuffer()
        self.assertIs(buffer1, buffer2)
        
    def test_store_message_valid(self):
        """Test storing a valid message"""
        mock_message = Mock()
        mock_message.text = "Test message"
        mock_message.chat_id = 123
        mock_message.from_user.id = 456
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = "Test"
        mock_message.message_id = 789
        mock_message.date = Mock()
        
        target_groups = {123, 456}
        
        with patch('messaging.message_buffer.create_message_data') as mock_create:
            mock_create.return_value = {
                "user": "testuser",
                "user_id": 456,
                "text": "Test message",
                "timestamp": Mock(),
                "message_id": 789,
                "chat_id": 123,
            }
            
            result = self.buffer.store_message(mock_message, target_groups)
            
        self.assertTrue(result)
        self.assertEqual(self.buffer.size(), 1)
        
    def test_store_message_filtered_out(self):
        """Test that messages from non-target groups are filtered out"""
        mock_message = Mock()
        mock_message.text = "Test message"
        mock_message.chat_id = 999  # Not in target groups
        
        target_groups = {123, 456}
        
        result = self.buffer.store_message(mock_message, target_groups)
        
        self.assertFalse(result)
        self.assertEqual(self.buffer.size(), 0)
        
    def test_store_message_no_text(self):
        """Test that messages without text are filtered out"""
        mock_message = Mock()
        mock_message.text = None
        mock_message.chat_id = 123
        
        target_groups = {123}
        
        result = self.buffer.store_message(mock_message, target_groups)
        
        self.assertFalse(result)
        self.assertEqual(self.buffer.size(), 0)
        
    def test_get_recent_messages_with_limit(self):
        """Test getting recent messages with limit"""
        # Store multiple messages
        target_groups = {123}
        
        for i in range(3):
            mock_message = Mock()
            mock_message.text = f"Message {i}"
            mock_message.chat_id = 123
            mock_message.from_user.id = 456
            mock_message.from_user.username = "testuser"
            mock_message.from_user.first_name = "Test"
            mock_message.message_id = i
            mock_message.date = Mock()
            
            with patch('messaging.message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "user": "testuser",
                    "user_id": 456,
                    "text": f"Message {i}",
                    "timestamp": Mock(),
                    "message_id": i,
                    "chat_id": 123,
                }
                self.buffer.store_message(mock_message, target_groups)
        
        # Get only last 2 messages
        recent = self.buffer.get_recent_messages(limit=2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["text"], "Message 1")
        self.assertEqual(recent[1]["text"], "Message 2")
        
    def test_get_recent_messages_with_filter(self):
        """Test getting recent messages with filter function"""
        target_groups = {123}
        
        messages_data = [
            {"text": "Hello world", "user_id": 1},
            {"text": "Test message", "user_id": 2},
            {"text": "Hello again", "user_id": 1},
        ]
        
        for i, msg_data in enumerate(messages_data):
            mock_message = Mock()
            mock_message.text = msg_data["text"]
            mock_message.chat_id = 123
            mock_message.from_user.id = msg_data["user_id"]
            mock_message.from_user.username = "testuser"
            mock_message.from_user.first_name = "Test"
            mock_message.message_id = i
            mock_message.date = Mock()
            
            with patch('messaging.message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "user": "testuser",
                    "user_id": msg_data["user_id"],
                    "text": msg_data["text"],
                    "timestamp": Mock(),
                    "message_id": i,
                    "chat_id": 123,
                }
                self.buffer.store_message(mock_message, target_groups)
        
        # Filter messages containing "Hello"
        def filter_hello(msg_data):
            return "Hello" in msg_data["text"]
            
        filtered = self.buffer.get_recent_messages(filter_func=filter_hello)
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all("Hello" in msg["text"] for msg in filtered))
        
    def test_find_messages_with_text(self):
        """Test finding messages with specific text"""
        target_groups = {123}
        
        messages = ["Hello world", "Test message", "Hello again"]
        
        for i, text in enumerate(messages):
            mock_message = Mock()
            mock_message.text = text
            mock_message.chat_id = 123
            mock_message.from_user.id = 456
            mock_message.from_user.username = "testuser"
            mock_message.from_user.first_name = "Test"
            mock_message.message_id = i
            mock_message.date = Mock()
            
            with patch('messaging.message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "user": "testuser",
                    "user_id": 456,
                    "text": text,
                    "timestamp": Mock(),
                    "message_id": i,
                    "chat_id": 123,
                }
                self.buffer.store_message(mock_message, target_groups)
        
        # Find messages containing "hello" (case insensitive)
        matches = self.buffer.find_messages_with_text("hello")
        self.assertEqual(len(matches), 2)
        
    def test_subscriber_notification(self):
        """Test that subscribers are notified when messages are stored"""
        callback_called = []
        
        def test_callback(message_data, buffer):
            callback_called.append((message_data, buffer))
            
        self.buffer.add_subscriber("test_subscriber", test_callback)
        
        mock_message = Mock()
        mock_message.text = "Test message"
        mock_message.chat_id = 123
        mock_message.from_user.id = 456
        mock_message.from_user.username = "testuser"
        mock_message.from_user.first_name = "Test"
        mock_message.message_id = 789
        mock_message.date = Mock()
        
        target_groups = {123}
        
        with patch('messaging.message_buffer.create_message_data') as mock_create:
            mock_create.return_value = {
                "user": "testuser",
                "user_id": 456,
                "text": "Test message",
                "timestamp": Mock(),
                "message_id": 789,
                "chat_id": 123,
            }
            
            self.buffer.store_message(mock_message, target_groups)
            
        # Verify callback was called
        self.assertEqual(len(callback_called), 1)
        message_data, buffer = callback_called[0]
        self.assertEqual(message_data["text"], "Test message")
        self.assertIs(buffer, self.buffer)
        
    def test_max_size_limit(self):
        """Test that buffer respects max_size limit"""
        target_groups = {123}
        
        # Store more messages than max_size (5)
        for i in range(7):
            mock_message = Mock()
            mock_message.text = f"Message {i}"
            mock_message.chat_id = 123
            mock_message.from_user.id = 456
            mock_message.from_user.username = "testuser"
            mock_message.from_user.first_name = "Test"
            mock_message.message_id = i
            mock_message.date = Mock()
            
            with patch('messaging.message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "user": "testuser",
                    "user_id": 456,
                    "text": f"Message {i}",
                    "timestamp": Mock(),
                    "message_id": i,
                    "chat_id": 123,
                }
                self.buffer.store_message(mock_message, target_groups)
        
        # Should only have 5 messages (max_size)
        self.assertEqual(self.buffer.size(), 5)
        
        # Should have the last 5 messages (2, 3, 4, 5, 6)
        messages = self.buffer.get_recent_messages()
        self.assertEqual(len(messages), 5)
        self.assertEqual(messages[0]["text"], "Message 2")
        self.assertEqual(messages[4]["text"], "Message 6")


if __name__ == '__main__':
    unittest.main()