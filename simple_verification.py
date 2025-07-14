#!/usr/bin/env python3
"""
Simple verification script that demonstrates the core functionality
without the complexity of singleton management in tests
"""
import os
import sys
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, 'src')

def test_basic_functionality():
    """Test the basic functionality by directly setting environment and importing fresh"""
    
    print("Setting up environment with user and group restrictions...")
    os.environ['TELEGRAM_TOKEN'] = 'test_token'
    os.environ['ALLOWED_USER_IDS'] = '123,456'
    os.environ['SUMMARY_GROUP_IDS'] = '-1001111,-1002222'
    
    # Import after setting environment
    from commands.command import Command
    
    command = Command()
    command._command = "test"
    
    print(f"Configured allowed users: {command._env.allowed_user_ids}")
    print(f"Configured summary groups: {command._env.summary_group_ids}")
    
    print("\n--- Testing Authorization Logic ---")
    
    # Test 1: Private chat - authorized user
    result1 = command._is_user_authorized(123, 'private', -999)
    print(f"1. Authorized user (123) in private chat: {'✓ ALLOWED' if result1 else '✗ BLOCKED'}")
    
    # Test 2: Private chat - unauthorized user  
    result2 = command._is_user_authorized(999, 'private', -999)
    print(f"2. Unauthorized user (999) in private chat: {'✗ BLOCKED' if not result2 else '✓ ALLOWED'}")
    
    # Test 3: Group chat - unauthorized user in allowed group
    result3 = command._is_user_authorized(999, 'group', -1001111)
    print(f"3. Unauthorized user (999) in allowed group: {'✓ ALLOWED' if result3 else '✗ BLOCKED'}")
    
    # Test 4: Group chat - unauthorized user in disallowed group
    result4 = command._is_user_authorized(999, 'group', -1003333)
    print(f"4. Unauthorized user (999) in disallowed group: {'✗ BLOCKED' if not result4 else '✓ ALLOWED'}")
    
    print("\n--- Testing Process Method ---")
    
    # Test process method with private chat unauthorized user
    update = Mock()
    update.message.from_user.id = 999
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.text = "/test"
    update.message.chat.id = -999
    update.message.chat.type = 'private'
    
    context = Mock()
    command._process(update, context)
    
    # Check what message was sent
    call_args = context.bot.send_message.call_args[1]
    if "🚫 Você não tem permissão" in call_args['text']:
        print("5. Process method correctly blocks unauthorized user in private: ✓ BLOCKED")
    else:
        print("5. Process method incorrectly allows unauthorized user in private: ✗ ALLOWED")
    
    # Test process method with group chat unauthorized user in allowed group
    context.bot.send_message.reset_mock()
    update.message.chat.id = -1001111
    update.message.chat.type = 'group'
    
    command._process(update, context)
    
    call_args = context.bot.send_message.call_args[1]
    if "Processando comando..." in call_args['text']:
        print("6. Process method correctly allows unauthorized user in allowed group: ✓ ALLOWED")
    else:
        print("6. Process method incorrectly blocks unauthorized user in allowed group: ✗ BLOCKED")
    
    print("\n--- Summary ---")
    expected_results = [result1, not result2, result3, not result4]
    if all(expected_results):
        print("✓ All authorization logic working as expected!")
        print("✓ Private messages are restricted to allowed users only")
        print("✓ Group messages allow any user in allowed groups")
        return True
    else:
        print("✗ Some authorization logic is not working correctly")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)