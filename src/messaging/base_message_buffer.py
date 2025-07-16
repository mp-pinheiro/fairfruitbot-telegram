import logging
from collections import deque
from typing import Dict, List, Optional, Set
from utils import create_message_data


class BaseMessageBuffer:
    """
    Base class for message buffer functionality.
    Provides common operations for storing and retrieving messages.
    Each command can have its own buffer with optimal size for its needs.
    """
    
    def __init__(self, max_size: int = 100, target_group_ids: Optional[Set[int]] = None):
        """
        Initialize the message buffer.
        
        Args:
            max_size: Maximum number of messages to store
            target_group_ids: Set of group IDs to filter for (optional)
        """
        self._buffer = deque(maxlen=max_size)
        self._target_group_ids = target_group_ids or set()
        
    def store_message(self, message) -> bool:
        """
        Store a message if it meets the criteria.
        
        Args:
            message: Telegram message object
            
        Returns:
            bool: True if message was stored, False if filtered out
        """
        if not message or not message.text:
            return False
            
        # Only filter by group IDs if they are set
        if self._target_group_ids and message.chat_id not in self._target_group_ids:
            return False
            
        try:
            message_data = create_message_data(message)
            self._buffer.append(message_data)
            return True
            
        except Exception as e:
            logging.error(f"Failed to store message: {e}")
            raise
            
    def get_recent_messages(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent messages.
        
        Args:
            limit: Maximum number of messages to return (None for all)
            
        Returns:
            List of message data dictionaries
        """
        messages = list(self._buffer)
        
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