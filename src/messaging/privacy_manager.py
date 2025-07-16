import hashlib
import logging
import secrets
import re
from typing import Dict, Optional, Set, List, ContextManager
from contextlib import contextmanager


class PrivacyManager:
    """
    Manages username anonymization for LLM calls to protect user privacy.
    Uses secure session-based hashing with in-place anonymization to prevent 
    user identification through hash reversibility or collision attacks.
    """
    
    def __init__(self):
        # No permanent storage - privacy mappings are session-based only
        pass
        
    def _generate_secure_hash(self, username: str, session_salt: str) -> str:
        """Generate a secure hash for a username using session salt"""
        # Use SHA-256 with session salt for security
        combined = f"{username}:{session_salt}"
        hash_value = hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]
        return f"User_{hash_value}"
    
    def _extract_usernames_from_text(self, text: str, known_usernames: Set[str]) -> Set[str]:
        """
        Extract potential usernames mentioned in message text.
        Looks for @mentions and known usernames in content.
        
        Args:
            text: Message text to scan
            known_usernames: Set of known usernames to look for
            
        Returns:
            Set of usernames found in text
        """
        found_usernames = set()
        
        # Look for @mentions (telegram format)
        mentions = re.findall(r'@(\w+)', text, re.IGNORECASE)
        found_usernames.update(mentions)
        
        # Look for known usernames mentioned in text (case insensitive)
        text_lower = text.lower()
        for username in known_usernames:
            if username.lower() in text_lower:
                found_usernames.add(username)
                
        return found_usernames
    
    @contextmanager
    def create_privacy_session(self, usernames: Set[str], message_texts: List[str] = None):
        """
        Create a privacy session for LLM calls with in-place anonymization.
        This ensures privacy mappings only exist during the LLM interaction.
        
        Args:
            usernames: Set of usernames to anonymize  
            message_texts: Optional list of message texts to scan for additional usernames
            
        Yields:
            PrivacySession: Session object with anonymize/deanonymize methods
        """
        # Generate a unique session salt for this privacy session
        session_salt = secrets.token_hex(16)
        
        # Find all usernames that need anonymization
        all_usernames = set(usernames)
        
        if message_texts:
            for text in message_texts:
                found_usernames = self._extract_usernames_from_text(text, usernames)
                all_usernames.update(found_usernames)
        
        # Create session mappings (only exist during this context)
        session_mappings = {}
        reverse_mappings = {}
        
        for username in all_usernames:
            if username:  # Skip empty usernames
                hash_value = self._generate_secure_hash(username, session_salt)
                session_mappings[username] = hash_value
                reverse_mappings[hash_value] = username
        
        class PrivacySession:
            def anonymize_text(self, text: str) -> str:
                """Anonymize text by replacing usernames with session hashes (case insensitive)"""
                anonymized_text = text
                # Sort by length (longest first) to avoid partial replacements
                for username in sorted(session_mappings.keys(), key=len, reverse=True):
                    if username:
                        # Case insensitive replacement using regex
                        pattern = re.escape(username)
                        anonymized_text = re.sub(pattern, session_mappings[username], anonymized_text, flags=re.IGNORECASE)
                return anonymized_text
                
            def deanonymize_text(self, text: str) -> str:
                """Restore original usernames from session hashes"""
                deanonymized_text = text
                for hash_value, username in reverse_mappings.items():
                    deanonymized_text = deanonymized_text.replace(hash_value, username)
                return deanonymized_text
                
            def get_anonymous_username(self, username: str) -> str:
                """Get the anonymous hash for a specific username"""
                return session_mappings.get(username, f"User_unknown_{secrets.token_hex(4)}")
        
        try:
            yield PrivacySession()
        finally:
            # Explicitly clear session data for security
            session_mappings.clear()
            reverse_mappings.clear()
            del session_mappings
            del reverse_mappings