import sys
import os
from datetime import datetime
sys.path.append('src')

# Set minimal required environment variables
os.environ['TELEGRAM_TOKEN'] = 'dummy_token'
os.environ['SUMMARY_GROUP_IDS'] = '-100146,-100147'
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

# Test TypoDetector with realistic scenarios
print('Testing TypoDetector with realistic typo scenarios...')

typo = TypoDetector()
target_group = -100146

# Create mock users
users = [
    MockUser(1001, 'user1', 'User One'),
    MockUser(1002, 'user2', 'User Two'), 
    MockUser(1003, 'user3', 'User Three'),
    MockUser(1004, 'user4', 'User Four'),
]

def send_message(user, text, msg_id=None):
    message = MockMessage(target_group, text, user, msg_id or len(typo._message_buffer) + 1)
    update = MockUpdate(message)
    context = MockContext()
    
    print(f'📨 {user.username}: "{text}"')
    typo._process(update, context)
    
send_message(users[0], "Eu estava pensando numa reclamaaaacao que fiz ontem")
send_message(users[1], "reclamaaaacao")  
send_message(users[2], "reclamaaaacao")

print(f'\nMessage buffer size: {len(typo._message_buffer)}')
print(f'Recent messages:')
for i, msg in enumerate(typo._message_buffer):
    print(f'  {i+1}. {msg["user"]}: "{msg["text"]}"')

print('\n' + '='*50)
print('Testing different scenarios...')

# Clear buffer and test another scenario
typo._message_buffer.clear()

# Scenario where someone makes a typo in context, then others repeat it
send_message(users[0], "Nossa, que chatoooo hoje")
send_message(users[1], "chatoooo")
send_message(users[2], "chatoooo")

print('\n' + '='*50) 
print('Testing with longer buffer...')

# Add more messages to build up buffer
typo._message_buffer.clear()
send_message(users[0], "Tava vendo aquele filme erronnnnn ontem")
send_message(users[1], "Legal, qual filme?")
send_message(users[2], "Não conheço")
send_message(users[0], "É sobre um cara que...")
send_message(users[1], "erronnnnn") # just the typo
send_message(users[3], "erronnnnn") # third person repeats

print(f'\nFinal buffer size: {len(typo._message_buffer)}')
