import hashlib
import logging
from typing import Dict, Optional


class PrivacyManager:
    """
    Manages username anonymization for LLM calls to protect user privacy.
    Replaces real usernames with hashes and maintains mapping for reconstruction.
    """
    
    def __init__(self):
        self._username_to_hash: Dict[str, str] = {}
        self._hash_to_username: Dict[str, str] = {}
        
    def _generate_hash(self, username: str) -> str:
        """Generate a consistent hash for a username"""
        # Use a prefix to make hashes more recognizable in logs/debugging
        hash_value = hashlib.md5(username.encode('utf-8')).hexdigest()[:8]
        return f"User_{hash_value}"
        
    def anonymize_username(self, username: str) -> str:
        """
        Convert a real username to an anonymous hash.
        
        Args:
            username: The real username to anonymize
            
        Returns:
            str: Anonymous hash representation
        """
        if not username:
            return "User_anonymous"
            
        if username not in self._username_to_hash:
            hash_value = self._generate_hash(username)
            self._username_to_hash[username] = hash_value
            self._hash_to_username[hash_value] = username
            
        return self._username_to_hash[username]
        
    def deanonymize_username(self, hash_value: str) -> Optional[str]:
        """
        Convert an anonymous hash back to the real username.
        
        Args:
            hash_value: The hash to convert back
            
        Returns:
            str or None: The real username, or None if not found
        """
        return self._hash_to_username.get(hash_value)
        
    def anonymize_text(self, text: str) -> str:
        """
        Replace any known usernames in text with their anonymous hashes.
        
        Args:
            text: Text that may contain usernames
            
        Returns:
            str: Text with usernames replaced by hashes
        """
        anonymized_text = text
        for username, hash_value in self._username_to_hash.items():
            anonymized_text = anonymized_text.replace(username, hash_value)
        return anonymized_text
        
    def deanonymize_text(self, text: str) -> str:
        """
        Replace any anonymous hashes in text with real usernames.
        
        Args:
            text: Text that may contain anonymous hashes
            
        Returns:
            str: Text with hashes replaced by real usernames
        """
        deanonymized_text = text
        for hash_value, username in self._hash_to_username.items():
            deanonymized_text = deanonymized_text.replace(hash_value, username)
        return deanonymized_text
        
    def clear(self):
        """Clear all stored mappings"""
        self._username_to_hash.clear()
        self._hash_to_username.clear()
        
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored mappings"""
        return {
            "total_users": len(self._username_to_hash)
        }