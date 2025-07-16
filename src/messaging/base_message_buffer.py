import logging
from collections import deque
from typing import Dict, List, Optional, Set
from utils import create_message_data


class BaseMessageBuffer:
    def __init__(self, max_size: int = 100, target_group_ids: Optional[Set[int]] = None):
        self._buffer = deque(maxlen=max_size)
        self._target_group_ids = target_group_ids or set()
        
    def store_message(self, message) -> bool:
        if not message or not message.text:
            return False
            
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
        messages = list(self._buffer)
        if limit is not None:
            messages = messages[-limit:]
        return messages
        
    def find_messages_with_text(self, text: str, limit: Optional[int] = None) -> List[Dict]:
        matches = []
        for msg in self._buffer:
            if text.lower() in msg.get("text", "").lower():
                matches.append(msg)
                if limit and len(matches) >= limit:
                    break
        return matches
        
    def get_messages_by_users(self, user_ids: Set[int], limit: Optional[int] = None) -> List[Dict]:
        messages = [msg for msg in self._buffer if msg.get("user_id") in user_ids]
        if limit is not None:
            messages = messages[-limit:]
        return messages
        
    def clear(self):
        self._buffer.clear()
        
    def size(self) -> int:
        return len(self._buffer)