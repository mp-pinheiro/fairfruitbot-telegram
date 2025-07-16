import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messaging.base_message_buffer import BaseMessageBuffer


class TestBaseMessageBuffer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.buffer = BaseMessageBuffer(max_size=5)
        
    def test_initialization(self):
        """Test that BaseMessageBuffer initializes correctly."""
        buffer = BaseMessageBuffer(max_size=10, target_group_ids={123, 456})
        self.assertEqual(buffer._buffer.maxlen, 10)
        self.assertEqual(buffer._target_group_ids, {123, 456})
        self.assertEqual(buffer.size(), 0)
        
    def test_initialization_without_group_ids(self):
        """Test initialization without target group IDs."""
        buffer = BaseMessageBuffer(max_size=5)
        self.assertEqual(buffer._target_group_ids, set())
        
    def test_store_message_valid(self):
        """Test storing a valid message."""
        # Mock message
        message = Mock()
        message.text = "Hello world"
        message.chat_id = 123
        message.from_user.id = 456
        message.from_user.username = "testuser"
        message.from_user.full_name = "Test User"
        message.message_id = 789
        
        # Mock create_message_data to return a simple dict
        with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
            mock_create.return_value = {
                "text": "Hello world",
                "user_id": 456,
                "user": "testuser",
                "message_id": 789,
                "chat_id": 123
            }
            
            result = self.buffer.store_message(message)
            self.assertTrue(result)
            self.assertEqual(self.buffer.size(), 1)
            
    def test_store_message_no_text(self):
        """Test storing a message without text."""
        message = Mock()
        message.text = None
        
        result = self.buffer.store_message(message)
        self.assertFalse(result)
        self.assertEqual(self.buffer.size(), 0)
        
    def test_store_message_group_filter(self):
        """Test that messages are filtered by target group IDs."""
        buffer = BaseMessageBuffer(max_size=5, target_group_ids={123})
        
        # Mock message from allowed group
        message1 = Mock()
        message1.text = "Hello from allowed group"
        message1.chat_id = 123
        message1.from_user.id = 456
        message1.from_user.username = "testuser"
        message1.from_user.full_name = "Test User"
        message1.message_id = 789
        
        # Mock message from disallowed group
        message2 = Mock()
        message2.text = "Hello from disallowed group"
        message2.chat_id = 999
        
        with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
            mock_create.return_value = {
                "text": "Hello from allowed group",
                "user_id": 456,
                "user": "testuser",
                "message_id": 789,
                "chat_id": 123
            }
            
            result1 = buffer.store_message(message1)
            result2 = buffer.store_message(message2)
            
            self.assertTrue(result1)
            self.assertFalse(result2)
            self.assertEqual(buffer.size(), 1)
            
    def test_get_recent_messages(self):
        """Test retrieving recent messages."""
        # Add some messages
        for i in range(3):
            message = Mock()
            message.text = f"Message {i}"
            message.chat_id = 123
            message.from_user.id = 456 + i
            message.from_user.username = f"user{i}"
            message.from_user.full_name = f"User {i}"
            message.message_id = 789 + i
            
            with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "text": f"Message {i}",
                    "user_id": 456 + i,
                    "user": f"user{i}",
                    "message_id": 789 + i,
                    "chat_id": 123
                }
                self.buffer.store_message(message)
        
        # Get all messages
        all_messages = self.buffer.get_recent_messages()
        self.assertEqual(len(all_messages), 3)
        
        # Get limited messages
        limited_messages = self.buffer.get_recent_messages(limit=2)
        self.assertEqual(len(limited_messages), 2)
        
    def test_max_size_limit(self):
        """Test that buffer respects max size limit."""
        # Add more messages than max size
        for i in range(7):  # buffer max size is 5
            message = Mock()
            message.text = f"Message {i}"
            message.chat_id = 123
            message.from_user.id = 456 + i
            message.from_user.username = f"user{i}"
            message.from_user.full_name = f"User {i}"
            message.message_id = 789 + i
            
            with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "text": f"Message {i}",
                    "user_id": 456 + i,
                    "user": f"user{i}",
                    "message_id": 789 + i,
                    "chat_id": 123
                }
                self.buffer.store_message(message)
        
        # Should only have 5 messages (max size)
        self.assertEqual(self.buffer.size(), 5)
        
        # Should have the latest messages (2, 3, 4, 5, 6)
        messages = self.buffer.get_recent_messages()
        self.assertEqual(messages[0]["text"], "Message 2")
        self.assertEqual(messages[-1]["text"], "Message 6")
        
    def test_find_messages_with_text(self):
        """Test finding messages containing specific text."""
        # Add messages with different text
        texts = ["Hello world", "Hello there", "Goodbye world"]
        for i, text in enumerate(texts):
            message = Mock()
            message.text = text
            message.chat_id = 123
            message.from_user.id = 456 + i
            message.from_user.username = f"user{i}"
            message.from_user.full_name = f"User {i}"
            message.message_id = 789 + i
            
            with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "text": text,
                    "user_id": 456 + i,
                    "user": f"user{i}",
                    "message_id": 789 + i,
                    "chat_id": 123
                }
                self.buffer.store_message(message)
        
        # Find messages containing "Hello"
        hello_messages = self.buffer.find_messages_with_text("Hello")
        self.assertEqual(len(hello_messages), 2)
        
        # Find messages containing "world"
        world_messages = self.buffer.find_messages_with_text("world")
        self.assertEqual(len(world_messages), 2)
        
        # Find with limit
        limited_hello = self.buffer.find_messages_with_text("Hello", limit=1)
        self.assertEqual(len(limited_hello), 1)
        
    def test_get_messages_by_users(self):
        """Test getting messages from specific users."""
        # Add messages from different users
        for i in range(3):
            message = Mock()
            message.text = f"Message from user {i}"
            message.chat_id = 123
            message.from_user.id = 456 + i
            message.from_user.username = f"user{i}"
            message.from_user.full_name = f"User {i}"
            message.message_id = 789 + i
            
            with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
                mock_create.return_value = {
                    "text": f"Message from user {i}",
                    "user_id": 456 + i,
                    "user": f"user{i}",
                    "message_id": 789 + i,
                    "chat_id": 123
                }
                self.buffer.store_message(message)
        
        # Get messages from specific users
        user_messages = self.buffer.get_messages_by_users({456, 458})
        self.assertEqual(len(user_messages), 2)
        
        # Get with limit
        limited_user_messages = self.buffer.get_messages_by_users({456, 457, 458}, limit=1)
        self.assertEqual(len(limited_user_messages), 1)
        
    def test_clear(self):
        """Test clearing the buffer."""
        # Add a message first
        message = Mock()
        message.text = "Test message"
        message.chat_id = 123
        message.from_user.id = 456
        message.from_user.username = "testuser"
        message.from_user.full_name = "Test User"
        message.message_id = 789
        
        with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
            mock_create.return_value = {
                "text": "Test message",
                "user_id": 456,
                "user": "testuser",
                "message_id": 789,
                "chat_id": 123
            }
            self.buffer.store_message(message)
        
        self.assertEqual(self.buffer.size(), 1)
        
        # Clear the buffer
        self.buffer.clear()
        self.assertEqual(self.buffer.size(), 0)
        
    def test_separate_instances_are_independent(self):
        """Test that separate BaseMessageBuffer instances are independent."""
        buffer1 = BaseMessageBuffer(max_size=3)
        buffer2 = BaseMessageBuffer(max_size=5)
        
        # Add message to buffer1
        message = Mock()
        message.text = "Test message"
        message.chat_id = 123
        message.from_user.id = 456
        message.from_user.username = "testuser"
        message.from_user.full_name = "Test User"
        message.message_id = 789
        
        with unittest.mock.patch('messaging.base_message_buffer.create_message_data') as mock_create:
            mock_create.return_value = {
                "text": "Test message",
                "user_id": 456,
                "user": "testuser",
                "message_id": 789,
                "chat_id": 123
            }
            buffer1.store_message(message)
        
        # buffer1 should have 1 message, buffer2 should have 0
        self.assertEqual(buffer1.size(), 1)
        self.assertEqual(buffer2.size(), 0)
        
        # Different max sizes
        self.assertEqual(buffer1._buffer.maxlen, 3)
        self.assertEqual(buffer2._buffer.maxlen, 5)


if __name__ == '__main__':
    unittest.main()