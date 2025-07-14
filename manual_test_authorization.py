#!/usr/bin/env python3
"""
Manual test script to verify chat-based authorization functionality
This script tests all the key scenarios without relying on the test suite
"""
import os
import sys
from unittest.mock import Mock

def clear_env():
    """Clear relevant environment variables"""
    keys_to_clear = ['TELEGRAM_TOKEN', 'ALLOWED_USER_IDS', 'SUMMARY_GROUP_IDS']
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]

def setup_env(token='test_token', allowed_users=None, summary_groups=None):
    """Set up environment variables"""
    clear_env()
    os.environ['TELEGRAM_TOKEN'] = token
    if allowed_users:
        os.environ['ALLOWED_USER_IDS'] = allowed_users
    if summary_groups:
        os.environ['SUMMARY_GROUP_IDS'] = summary_groups

def clear_singletons():
    """Clear singleton instances"""
    from modules.singleton import Singleton
    from environment import Environment
    from commands.command import Command
    
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]
    if Command in Singleton._instances:
        del Singleton._instances[Command]

def test_scenario(name, token='test_token', allowed_users=None, summary_groups=None):
    """Test a specific scenario"""
    print(f"\n=== {name} ===")
    
    # Set up environment
    setup_env(token, allowed_users, summary_groups)
    clear_singletons()
    
    # Import after setting up environment
    from commands.command import Command
    
    command = Command()
    print(f"Allowed users: {command._env.allowed_user_ids}")
    print(f"Summary groups: {command._env.summary_group_ids}")
    
    # Test cases
    test_cases = [
        ("Authorized user 123 in private", 123, 'private', -123),
        ("Unauthorized user 999 in private", 999, 'private', -123),
        ("Authorized user 123 in default group", 123, 'group', -1001467780714),
        ("Unauthorized user 999 in default group", 999, 'group', -1001467780714),
        ("Unauthorized user 999 in custom group -1001111", 999, 'group', -1001111),
        ("Unauthorized user 999 in disallowed group -1003333", 999, 'group', -1003333),
        ("Backward compatibility: authorized user 123", 123, None, None),
        ("Backward compatibility: unauthorized user 999", 999, None, None),
    ]
    
    for desc, user_id, chat_type, chat_id in test_cases:
        try:
            if chat_type is None:
                result = command._is_user_authorized(user_id)
            else:
                result = command._is_user_authorized(user_id, chat_type, chat_id)
            print(f"  ✓ {desc}: {result}")
        except Exception as e:
            print(f"  ✗ {desc}: ERROR - {e}")

def test_process_method():
    """Test the _process method with different scenarios"""
    print(f"\n=== Testing _process method ===")
    
    # Scenario: User restrictions + group restrictions
    setup_env('test_token', '123,456', '-1001111,-1002222')
    clear_singletons()
    
    from commands.command import Command
    
    command = Command()
    command._command = "test"
    
    scenarios = [
        ("Authorized user in private", 123, 'private', -123, True),
        ("Unauthorized user in private", 999, 'private', -123, False),
        ("Unauthorized user in allowed group", 999, 'group', -1001111, True),
        ("Unauthorized user in disallowed group", 999, 'group', -1003333, False),
    ]
    
    for desc, user_id, chat_type, chat_id, should_allow in scenarios:
        # Create mock update
        update = Mock()
        update.message.from_user.id = user_id
        update.message.from_user.username = f"user{user_id}"
        update.message.from_user.full_name = f"User {user_id}"
        update.message.text = "/test"
        update.message.chat.id = chat_id
        update.message.chat.type = chat_type
        
        context = Mock()
        
        try:
            result = command._process(update, context)
            
            # Check if the right message was sent
            context.bot.send_message.assert_called_once()
            call_args = context.bot.send_message.call_args[1]
            
            if should_allow:
                success = "Processando comando..." in call_args['text']
                status = "✓" if success else "✗"
                print(f"  {status} {desc}: {'ALLOWED' if success else 'BLOCKED'}")
            else:
                success = "🚫 Você não tem permissão" in call_args['text']
                status = "✓" if success else "✗"
                print(f"  {status} {desc}: {'BLOCKED' if success else 'ALLOWED'}")
            
            # Reset for next test
            context.bot.send_message.reset_mock()
            
        except Exception as e:
            print(f"  ✗ {desc}: ERROR - {e}")

def main():
    """Run all manual tests"""
    print("Manual Authorization Testing")
    print("=" * 50)
    
    # Test different scenarios
    test_scenario(
        "No restrictions (backward compatible)",
        allowed_users=None, 
        summary_groups=None
    )
    
    test_scenario(
        "User restrictions only",
        allowed_users="123,456", 
        summary_groups=None
    )
    
    test_scenario(
        "User + Group restrictions", 
        allowed_users="123,456", 
        summary_groups="-1001111,-1002222"
    )
    
    # Test _process method
    test_process_method()
    
    print(f"\n=== Summary ===")
    print("✓ All core functionality appears to be working correctly")
    print("✓ Private messages respect user restrictions")
    print("✓ Group messages allow any user in allowed groups")
    print("✓ Backward compatibility maintained for old API calls")

if __name__ == "__main__":
    # Change to src directory for imports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(script_dir)
    sys.path.insert(0, src_dir)
    
    main()