import json
import logging
import os
from typing import Dict, List, Tuple


class TypoTracker:
    def __init__(self, data_dir: str = "data"):
        """Initialize the typo tracker with a data directory."""
        self.data_dir = data_dir
        self.typo_file = os.path.join(data_dir, "typo_errors.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize file if it doesn't exist
        if not os.path.exists(self.typo_file):
            self._save_data({})

    def _load_data(self) -> Dict[str, Dict]:
        """Load typo data from JSON file."""
        try:
            with open(self.typo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Failed to load typo data: {e}, initializing empty data")
            return {}

    def _save_data(self, data: Dict[str, Dict]) -> None:
        """Save typo data to JSON file."""
        try:
            with open(self.typo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save typo data: {e}")

    def add_typo(self, user_id: int, username: str, typo_word: str) -> None:
        """Add a typo for a user."""
        data = self._load_data()
        user_key = str(user_id)
        
        if user_key not in data:
            data[user_key] = {
                "username": username,
                "total_errors": 0,
                "typos": []
            }
        
        # Update username in case it changed
        data[user_key]["username"] = username
        data[user_key]["total_errors"] += 1
        data[user_key]["typos"].append(typo_word)
        
        self._save_data(data)
        logging.info(f"Added typo '{typo_word}' for user {username} (ID: {user_id})")

    def get_top_users(self, limit: int = 3) -> List[Tuple[str, int]]:
        """Get top users by error count."""
        data = self._load_data()
        
        # Convert to list of (username, error_count)
        users = [(user_data["username"], user_data["total_errors"]) 
                 for user_data in data.values()]
        
        # Sort by error count (descending) and take top N
        users.sort(key=lambda x: x[1], reverse=True)
        return users[:limit]

    def get_user_stats(self, user_id: int) -> Dict:
        """Get stats for a specific user."""
        data = self._load_data()
        user_key = str(user_id)
        return data.get(user_key, {"username": "Unknown", "total_errors": 0, "typos": []})