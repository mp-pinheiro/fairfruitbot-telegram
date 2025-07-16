import logging
from collections import deque
from typing import Dict, List, Optional, Set, Callable
from utils import create_message_data


class MessageBuffer:
    """
    Shared message buffer for commands that need to read and store messages.
    Eliminates duplication between TypoDetector and GroupSummary.
    """
    
    def __init__(self, max_size: int = 100):
        self._buffer = deque(maxlen=max_size)
        
    def store_message(self, message, target_group_ids: Set[int]) -> bool:
        """
        Store a message if it's from one of the target groups.
        
        Args:
            message: Telegram message object
            target_group_ids: Set of group IDs to filter for
            
        Returns:
            bool: True if message was stored, False if filtered out
        """
        if not message or not message.text:
            return False
            
        if message.chat_id not in target_group_ids:
            return False
            
        try:
            message_data = create_message_data(message)
            self._buffer.append(message_data)
            return True
            
        except Exception as e:
            logging.error(f"Failed to store message: {e}")
            raise
            
    def get_recent_messages(self, limit: Optional[int] = None, 
                          filter_func: Optional[Callable] = None) -> List[Dict]:
        """
        Get recent messages, optionally filtered.
        
        Args:
            limit: Maximum number of messages to return (None for all)
            filter_func: Optional function to filter messages (takes message_data, returns bool)
            
        Returns:
            List of message data dictionaries
        """
        messages = list(self._buffer)
        
        if filter_func:
            messages = [msg for msg in messages if filter_func(msg)]
            
        if limit is not None:
            messages = messages[-limit:]
            
        return messages
        
    def find_messages_with_text(self, text: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Find messages containing specific text.
        
        Args:
            text: Text to search for (case insensitive)
            limit: Maximum number of messages to return
            
        Returns:
            List of matching message data dictionaries
        """
        matches = []
        for msg in self._buffer:
            if text.lower() in msg.get("text", "").lower():
                matches.append(msg)
                if limit and len(matches) >= limit:
                    break
        return matches
        
    def get_messages_by_users(self, user_ids: Set[int], limit: Optional[int] = None) -> List[Dict]:
        """
        Get messages from specific users.
        
        Args:
            user_ids: Set of user IDs to filter for
            limit: Maximum number of messages to return
            
        Returns:
            List of message data dictionaries
        """
        messages = [
            msg for msg in self._buffer 
            if msg.get("user_id") in user_ids
        ]
        
        if limit is not None:
            messages = messages[-limit:]
            
        return messages
        
    def clear(self):
        """Clear the message buffer"""
        self._buffer.clear()
        
    def size(self) -> int:
        """Get current number of messages in buffer"""
        return len(self._buffer)


# Create a shared instance that commands can use
# This eliminates the singleton confusion while still providing shared storage
_shared_message_buffer = MessageBuffer(max_size=100)


def get_shared_message_buffer() -> MessageBuffer:
    """Get the shared MessageBuffer instance"""
    return _shared_message_buffer