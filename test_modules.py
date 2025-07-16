import sys
import os
sys.path.append('src')

# Set minimal required environment variables
os.environ['TELEGRAM_TOKEN'] = 'dummy_token'
os.environ['SUMMARY_GROUP_IDS'] = '-100146,-100147'
os.environ['OPENAI_API_KEY'] = 'dummy_key'

from commands.typo_detector import TypoDetector
from commands.group_summary import GroupSummary

print('Testing module imports and instantiation...')

try:
    typo = TypoDetector()
    print(f'✓ TypoDetector instantiated successfully')
    print(f'  Target groups: {typo._target_group_ids}')
    print(f'  Min users: {typo._min_users}')
except Exception as e:
    print(f'✗ TypoDetector failed: {e}')

try:
    summary = GroupSummary()
    print(f'✓ GroupSummary instantiated successfully')
    print(f'  Target groups: {summary._target_group_ids}')
    print(f'  Trigger patterns: {summary._trigger_patterns}')
except Exception as e:
    print(f'✗ GroupSummary failed: {e}')

# Test if both use the same target groups
try:
    if typo._target_group_ids == summary._target_group_ids:
        print('✓ Both modules use the same target groups')
    else:
        print(f'✗ Target groups differ: typo={typo._target_group_ids}, summary={summary._target_group_ids}')
except:
    print('Could not compare target groups')

# Test handler setup
print('\nTesting handler setup...')
from telegram.ext import Updater
updater = Updater(token='dummy_token', use_context=True)
dispatcher = updater.dispatcher

try:
    typo.setup(dispatcher)
    print('✓ TypoDetector setup completed')
except Exception as e:
    print(f'✗ TypoDetector setup failed: {e}')

try:
    summary.setup(dispatcher)
    print('✓ GroupSummary setup completed')
except Exception as e:
    print(f'✗ GroupSummary setup failed: {e}')

print(f'\nTotal handlers registered: {len(dispatcher.handlers[0])}')
for i, handler in enumerate(dispatcher.handlers[0]):
    print(f'  Handler {i}: {type(handler).__name__} - {handler.filters}')
