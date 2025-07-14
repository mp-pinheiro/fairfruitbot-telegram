"""
Simple manual test to validate authorization logic without environment patching
"""
import os
import sys

def test_authorization_logic():
    # Set up environment manually
    os.environ['TELEGRAM_TOKEN'] = 'test_token'
    os.environ['ALLOWED_USER_IDS'] = '123,456'
    os.environ['SUMMARY_GROUP_IDS'] = '-1001111,-1002222'
    
    # Clear singleton instances
    from modules.singleton import Singleton
    from environment import Environment
    from commands.command import Command
    
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]
    if Command in Singleton._instances:
        del Singleton._instances[Command]
    
    # Test the authorization
    command = Command()
    
    # Test 1: authorized user in private chat
    result1 = command._is_user_authorized(123, 'private', 999)
    print(f"Test 1 - authorized user in private: {result1} (expected: True)")
    
    # Test 2: unauthorized user in private chat
    result2 = command._is_user_authorized(999, 'private', 888)
    print(f"Test 2 - unauthorized user in private: {result2} (expected: False)")
    
    # Test 3: any user in allowed group
    result3 = command._is_user_authorized(999, 'group', -1001111)
    print(f"Test 3 - any user in allowed group: {result3} (expected: True)")
    
    # Test 4: any user in disallowed group
    result4 = command._is_user_authorized(999, 'group', -1003333)
    print(f"Test 4 - any user in disallowed group: {result4} (expected: False)")
    
    # Verify all tests pass
    all_passed = result1 and not result2 and result3 and not result4
    print(f"All tests passed: {all_passed}")
    
    # Clean up
    del os.environ['TELEGRAM_TOKEN']
    del os.environ['ALLOWED_USER_IDS']
    del os.environ['SUMMARY_GROUP_IDS']
    
    return all_passed

if __name__ == '__main__':
    success = test_authorization_logic()
    sys.exit(0 if success else 1)