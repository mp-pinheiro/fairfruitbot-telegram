import hashlib
import re
import secrets
import uuid
from typing import Dict, Tuple


class PrivacyManager:
    def __init__(self):
        # generate a random salt per session for extra privacy
        self._salt = secrets.token_hex(16)
        self._user_map = {}  # hash -> original username
        self._reverse_map = {}  # original -> hash
    
    def _hash_username(self, username: str) -> str:
        """create a unique user identifier"""
        if not username:
            return "User0"
            
        # check if we already hashed this username
        if username in self._reverse_map:
            return self._reverse_map[username]
            
        # create deterministic UUID from salted username
        salted = f"{self._salt}:{username}"
        hash_bytes = hashlib.sha256(salted.encode()).digest()
        # use first 16 bytes to create UUID
        fake_uuid = str(uuid.UUID(bytes=hash_bytes[:16]))
        fake_name = f"User_{fake_uuid}"
        
        # store mappings
        self._user_map[fake_name] = username
        self._reverse_map[username] = fake_name
        
        return fake_name
    
    def anonymize_messages(self, messages: list) -> Tuple[list, Dict[str, str]]:
        """anonymize usernames in messages for GPT"""
        anonymized_messages = []
        
        for msg in messages:
            # get username from different possible fields
            username = None
            if isinstance(msg, dict):
                username = msg.get('user') or msg.get('username') or f"id_{msg.get('user_id', 'unknown')}"
                text = msg.get('text', '')
            else:
                # handle other message formats
                continue
                
            # hash the username
            hashed_username = self._hash_username(username)
            
            # replace @mentions in text
            anonymized_text = self._anonymize_text(text)
            
            # create anonymized message
            anon_msg = msg.copy() if isinstance(msg, dict) else {}
            anon_msg['user'] = hashed_username
            anon_msg['text'] = anonymized_text
            
            anonymized_messages.append(anon_msg)
        
        return anonymized_messages, self._user_map
    
    def _anonymize_text(self, text: str) -> str:
        """replace @mentions with hashed versions"""
        if not text:
            return text
            
        # find all @mentions
        mention_pattern = r'@(\w+)'
        
        def replace_mention(match):
            username = match.group(1)
            hashed = self._hash_username(username)
            return f"@{hashed}"
        
        return re.sub(mention_pattern, replace_mention, text)
    
    def restore_username(self, hashed_username: str) -> str:
        """restore original username from hash"""
        return self._user_map.get(hashed_username, hashed_username)