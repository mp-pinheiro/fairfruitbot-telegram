import sys
import os
from datetime import datetime
sys.path.append('src')

# Set minimal required environment variables
os.environ['TELEGRAM_TOKEN'] = 'dummy_token'
os.environ['SUMMARY_GROUP_IDS'] = '-100146,-100147'  # Target groups
os.environ['OPENAI_API_KEY'] = 'dummy_key'

from commands.typo_detector import TypoDetector

class MockUser:
    def __init__(self, id, username, full_name):
        self.id = id
        self.username = username
        self.full_name = full_name

class MockMessage:
    def __init__(self, chat_id, text, from_user, message_id=1):
        self.chat_id = chat_id
        self.text = text
        self.from_user = from_user
        self.message_id = message_id
        self.date = datetime.now()

class MockUpdate:
    def __init__(self, message):
        self.message = message

class MockContext:
    def __init__(self):
        self.bot = MockBot()

class MockBot:
    def send_message(self, chat_id, text, **kwargs):
        print(f'🤖 BOT RESPONSE: {text}')
        return True

print('Testing TypoDetector with wrong group ID...')

typo = TypoDetector()
print(f'Target groups: {typo._target_group_ids}')

# Test with a message from a DIFFERENT group (not in target groups)
wrong_group = -999999  # This group is not in the target groups
test_user = MockUser(12345, 'testuser', 'Test User')
test_message = MockMessage(wrong_group, 'hello', test_user)
test_update = MockUpdate(test_message)
test_context = MockContext()

print(f'\nSending message from chat_id={wrong_group} (not in target groups)...')
typo._process(test_update, test_context)

print(f'\nSending message from chat_id={typo._target_group_ids[0]} (in target groups)...')
correct_message = MockMessage(typo._target_group_ids[0], 'hello', test_user)
correct_update = MockUpdate(correct_message)
typo._process(correct_update, test_context)
