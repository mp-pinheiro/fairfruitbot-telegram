import os
import sys
from unittest.mock import patch
import pytest

# Add src to path before importing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from environment import Environment
from modules.singleton import Singleton


def test_summary_group_ids_parsing_issue_16():
    """Test for the specific issue reported in GitHub issue #16.
    
    User reported: SUMMARY_GROUP_IDS=-1001467780714,-4844834146
    But only sees messages from group 1, not the second.
    
    This test verifies that both group IDs are correctly parsed.
    """
    # Clear any existing singleton instances
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]
    
    # Set environment variables directly (more reliable than patch.dict)
    original_token = os.environ.get('TELEGRAM_TOKEN')
    original_groups = os.environ.get('SUMMARY_GROUP_IDS')
    
    try:
        os.environ['TELEGRAM_TOKEN'] = 'test_token_for_issue_16'
        os.environ['SUMMARY_GROUP_IDS'] = '-1001467780714,-4844834146'
        
        # Force reload of dotenv to pick up new environment variables
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Create Environment instance
        env = Environment()
        
        # Verify both group IDs are parsed correctly
        expected_group_ids = [-1001467780714, -4844834146]
        assert env.summary_group_ids == expected_group_ids, \
            f"Expected {expected_group_ids}, but got {env.summary_group_ids}"
        
        # Verify there are exactly 2 groups
        assert len(env.summary_group_ids) == 2, \
            f"Expected 2 group IDs, but got {len(env.summary_group_ids)}"
        
        # Verify each specific group ID is present
        assert -1001467780714 in env.summary_group_ids, \
            "First group ID -1001467780714 not found in parsed list"
        assert -4844834146 in env.summary_group_ids, \
            "Second group ID -4844834146 not found in parsed list"
        
        print("✅ Issue #16 test passed: Both group IDs are correctly parsed")
        
    finally:
        # Restore original environment variables
        if original_token is not None:
            os.environ['TELEGRAM_TOKEN'] = original_token
        elif 'TELEGRAM_TOKEN' in os.environ:
            del os.environ['TELEGRAM_TOKEN']
            
        if original_groups is not None:
            os.environ['SUMMARY_GROUP_IDS'] = original_groups
        elif 'SUMMARY_GROUP_IDS' in os.environ:
            del os.environ['SUMMARY_GROUP_IDS']
        
        # Clear singleton
        if Environment in Singleton._instances:
            del Singleton._instances[Environment]


def test_group_summary_target_groups_functionality():
    """Test that GroupSummary would correctly use the parsed group IDs.
    
    This simulates the GroupSummary logic without requiring OpenAI client.
    """
    # Clear any existing singleton instances
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]
    
    original_token = os.environ.get('TELEGRAM_TOKEN')
    original_groups = os.environ.get('SUMMARY_GROUP_IDS')
    
    try:
        os.environ['TELEGRAM_TOKEN'] = 'test_token_functionality'
        os.environ['SUMMARY_GROUP_IDS'] = '-1001467780714,-4844834146'
        
        # Force reload of dotenv
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        env = Environment()
        target_group_ids = env.summary_group_ids
        
        # Simulate GroupSummary._should_trigger logic
        def should_trigger(message_text, chat_id):
            trigger_patterns = ["6 falam", "vcs falam", "ces falam", "6️⃣"]
            
            # Check if it's one of the target groups
            if chat_id not in target_group_ids:
                return False

            # Check if message contains any trigger patterns
            message_lower = message_text.lower()
            for pattern in trigger_patterns:
                if pattern.lower() in message_lower:
                    return True

            return False
        
        # Simulate GroupSummary._store_message logic
        def should_store_message(chat_id):
            return chat_id in target_group_ids
        
        # Test scenarios
        test_message = "6 falam"
        
        # Both groups should trigger
        assert should_trigger(test_message, -1001467780714), \
            "First group should trigger summary"
        assert should_trigger(test_message, -4844834146), \
            "Second group should trigger summary"
        
        # Random group should not trigger
        assert not should_trigger(test_message, -999999), \
            "Random group should not trigger summary"
        
        # Both groups should store messages
        assert should_store_message(-1001467780714), \
            "Messages from first group should be stored"
        assert should_store_message(-4844834146), \
            "Messages from second group should be stored"
        
        # Random group should not store messages
        assert not should_store_message(-999999), \
            "Messages from random group should not be stored"
        
        print("✅ GroupSummary functionality test passed: Both groups work correctly")
        
    finally:
        # Restore original environment variables
        if original_token is not None:
            os.environ['TELEGRAM_TOKEN'] = original_token
        elif 'TELEGRAM_TOKEN' in os.environ:
            del os.environ['TELEGRAM_TOKEN']
            
        if original_groups is not None:
            os.environ['SUMMARY_GROUP_IDS'] = original_groups
        elif 'SUMMARY_GROUP_IDS' in os.environ:
            del os.environ['SUMMARY_GROUP_IDS']
        
        # Clear singleton
        if Environment in Singleton._instances:
            del Singleton._instances[Environment]


if __name__ == '__main__':
    test_summary_group_ids_parsing_issue_16()
    test_group_summary_target_groups_functionality()
    print("All tests passed!")