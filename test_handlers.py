import sys
import os
sys.path.append('src')

# Set minimal required environment variables
os.environ['TELEGRAM_TOKEN'] = 'dummy_token'
os.environ['SUMMARY_GROUP_IDS'] = '-100146,-100147'
os.environ['OPENAI_API_KEY'] = 'dummy_key'

from commands.typo_detector import TypoDetector
from commands.group_summary import GroupSummary
from telegram.ext import MessageHandler, Filters

print('Testing handler creation...')

try:
    typo = TypoDetector()
    # Test creating the handler manually
    typo_handler = MessageHandler(Filters.text & Filters.group, typo._process)
    print(f'✓ TypoDetector handler created: {typo_handler.filters}')
except Exception as e:
    print(f'✗ TypoDetector handler failed: {e}')

try:
    summary = GroupSummary()
    # Test creating the handler manually
    summary_handler = MessageHandler(Filters.text & Filters.group, summary._process)
    print(f'✓ GroupSummary handler created: {summary_handler.filters}')
except Exception as e:
    print(f'✗ GroupSummary handler failed: {e}')

# Both handlers should have identical filters
if typo_handler.filters == summary_handler.filters:
    print('✓ Both handlers use identical filters')
else:
    print(f'✗ Handlers have different filters')

# Test mock message processing
print('\nCreating mock message for testing...')

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

class MockUpdate:
    def __init__(self, message):
        self.message = message

class MockContext:
    def __init__(self):
        self.bot = MockBot()

class MockBot:
    def send_message(self, chat_id, text, **kwargs):
        print(f'MOCK BOT: Sending to {chat_id}: {text}')

# Test with a message from the target group
target_group = -100146
test_user = MockUser(12345, 'testuser', 'Test User')
test_message = MockMessage(target_group, 'hello', test_user)
test_update = MockUpdate(test_message)
test_context = MockContext()

print(f'\nTesting message processing with chat_id={target_group}...')

print('Testing TypoDetector._process...')
try:
    typo._process(test_update, test_context)
    print('✓ TypoDetector._process executed without errors')
except Exception as e:
    print(f'✗ TypoDetector._process failed: {e}')
    import traceback
    traceback.print_exc()

print('Testing GroupSummary._process...')
try:
    summary._process(test_update, test_context)
    print('✓ GroupSummary._process executed without errors')
except Exception as e:
    print(f'✗ GroupSummary._process failed: {e}')
    import traceback
    traceback.print_exc()
