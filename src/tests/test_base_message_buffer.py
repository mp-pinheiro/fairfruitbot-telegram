import unittest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messaging.base_message_buffer import BaseMessageBuffer


class TestBaseMessageBuffer(unittest.TestCase):
    
    def setUp(self):
        self.buffer = BaseMessageBuffer(max_size=5)
        
    def test_initialization(self):
        buffer = BaseMessageBuffer(max_size=10, target_group_ids={123, 456})
        self.assertEqual(buffer._buffer.maxlen, 10)
        self.assertEqual(buffer._target_group_ids, {123, 456})
        self.assertEqual(buffer.size(), 0)
        
    def test_store_message_valid(self):
        message = Mock()
        message.text = "Hello world"
        message.chat_id = 123
        message.from_user.id = 456
        message.from_user.username = "testuser"
        message.from_user.full_name = "Test User"
        message.message_id = 789
        
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
        message = Mock()
        message.text = None
        
        result = self.buffer.store_message(message)
        self.assertFalse(result)
        self.assertEqual(self.buffer.size(), 0)
        
    def test_separate_instances_are_independent(self):
        buffer1 = BaseMessageBuffer(max_size=3)
        buffer2 = BaseMessageBuffer(max_size=5)
        
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
        
        self.assertEqual(buffer1.size(), 1)
        self.assertEqual(buffer2.size(), 0)


if __name__ == '__main__':
    unittest.main()