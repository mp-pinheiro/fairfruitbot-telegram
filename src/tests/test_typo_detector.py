import os
from unittest.mock import Mock, patch
import pytest
from commands.typo_detector import TypoDetector
from modules.singleton import Singleton
from environment import Environment


def teardown_function():
    # Clear singleton instances after each test
    if TypoDetector in Singleton._instances:
        del Singleton._instances[TypoDetector]
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]


def create_mock_message(user_id, text, message_id=1, chat_id=-1001467780714):
    """Create a mock telegram message for testing"""
    message = Mock()
    message.from_user.id = user_id
    message.from_user.username = f"user{user_id}"
    message.from_user.full_name = f"User {user_id}"
    message.text = text
    message.message_id = message_id
    message.chat_id = chat_id
    message.date = Mock()
    return message


def create_mock_update(message):
    """Create a mock telegram update for testing"""
    update = Mock()
    update.message = message
    return update


def test_typo_detector_initialization():
    """Test that TypoDetector initializes correctly"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        detector = TypoDetector()
        assert detector._min_users == 3
        assert -1001467780714 in detector._target_group_ids
        assert len(detector._message_buffer) == 0


def test_typo_detector_fazedo_case():
    """Test the 'fazedo' case from the issue - should trigger with 3+ users and GPT validation"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            # Mock the OpenAI client to return that it's a typo
            mock_openai_instance = Mock()
            mock_openai_instance.make_request.return_value = "YES"
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            
            # Create mock context and bot
            context = Mock()
            context.bot.send_message = Mock()
            
            # Simulate the fazedo case from the issue
            # User1: "fazedo piadinha" 
            msg1 = create_mock_message(user_id=1, text="fazedo piadinha", message_id=1)
            update1 = create_mock_update(msg1)
            detector._process(update1, context)
            
            # User2: "Ala o outro"
            msg2 = create_mock_message(user_id=2, text="Ala o outro", message_id=2)
            update2 = create_mock_update(msg2)
            detector._process(update2, context)
            
            # User1: "kd"
            msg3 = create_mock_message(user_id=1, text="kd", message_id=3)
            update3 = create_mock_update(msg3)
            detector._process(update3, context)
            
            # User1: "onde"
            msg4 = create_mock_message(user_id=1, text="onde", message_id=4)
            update4 = create_mock_update(msg4)
            detector._process(update4, context)
            
            # User3: "fazedo" - this should trigger (3 users: 1, 3, and need one more)
            msg5 = create_mock_message(user_id=3, text="fazedo", message_id=5)
            update5 = create_mock_update(msg5)
            detector._process(update5, context)
            
            # Should not trigger yet - only 2 users
            assert context.bot.send_message.call_count == 0
            
            # User2: "Fazedo" - this should trigger (3 users: 1, 2, 3)
            msg6 = create_mock_message(user_id=2, text="Fazedo", message_id=6)
            update6 = create_mock_update(msg6)
            detector._process(update6, context)
            
            # Should trigger once with 3 users
            assert context.bot.send_message.call_count == 1
            
            # Check the call arguments
            call_args = context.bot.send_message.call_args
            assert call_args[1]['chat_id'] == -1001467780714
            assert "proibido errar" in call_args[1]['text']
            assert call_args[1]['reply_to_message_id'] == 1  # Reply to original message


def test_typo_detector_tendeyu_case():
    """Test the 'tendeyu' case from the issue - should trigger with 3 users and GPT validation"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            # Mock the OpenAI client to return that it's a typo
            mock_openai_instance = Mock()
            mock_openai_instance.make_request.return_value = "YES"
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            
            # Create mock context and bot
            context = Mock()
            context.bot.send_message = Mock()
            
            # Simulate the tendeyu case from the issue - need 3 users now
            # User2: "he was a limão siciliano boy she was a aroma sense girl tendeyu"
            msg1 = create_mock_message(user_id=2, text="he was a limão siciliano boy she was a aroma sense girl tendeyu", message_id=1)
            update1 = create_mock_update(msg1)
            detector._process(update1, context)
            
            # User2: "tendeyu"
            msg2 = create_mock_message(user_id=2, text="tendeyu", message_id=2)
            update2 = create_mock_update(msg2)
            detector._process(update2, context)
            
            # User1: "tendeyu" - should not trigger yet with only 2 users
            msg3 = create_mock_message(user_id=1, text="tendeyu", message_id=3)
            update3 = create_mock_update(msg3)
            detector._process(update3, context)
            
            # Should not trigger with only 2 users
            assert context.bot.send_message.call_count == 0
            
            # User3: "tendeyu" - should trigger with 3 users
            msg4 = create_mock_message(user_id=3, text="tendeyu", message_id=4)
            update4 = create_mock_update(msg4)
            detector._process(update4, context)
            
            # Should trigger with 3 users
            assert context.bot.send_message.call_count == 1
            
            # Check the call arguments
            call_args = context.bot.send_message.call_args
            assert call_args[1]['chat_id'] == -1001467780714
            assert "proibido errar" in call_args[1]['text']
            assert call_args[1]['reply_to_message_id'] == 1  # Reply to original message


def test_typo_detector_extract_potential_typos():
    """Test word extraction logic"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            mock_openai_instance = Mock()
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            
            # Test various cases - now using _extract_words instead of _extract_potential_typos
            assert "fazedo" in detector._extract_words("fazedo piadinha")
            assert "tendeyu" in detector._extract_words("tendeyu")
            assert "mudno" in detector._extract_words("ola mudno, isso é um exemplo")
            
            # Test that words longer than 3 characters are included
            assert "isso" in detector._extract_words("ola mudno, isso é um exemplo")
            assert "exemplo" in detector._extract_words("ola mudno, isso é um exemplo")
            
            # Test that short words are filtered out
            assert "é" not in detector._extract_words("ola mudno, isso é um exemplo")
            assert "um" not in detector._extract_words("ola mudno, isso é um exemplo")


def test_typo_detector_different_chat():
    """Test that detector ignores messages from non-target chats"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            mock_openai_instance = Mock()
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            
            # Create mock context and bot
            context = Mock()
            context.bot.send_message = Mock()
            
            # Message from different chat (not in target groups)
            msg1 = create_mock_message(user_id=1, text="fazedo", message_id=1, chat_id=-999999)
            update1 = create_mock_update(msg1)
            detector._process(update1, context)
            
            # Should not trigger or store anything
            assert context.bot.send_message.call_count == 0
            assert len(detector._message_buffer) == 0


def test_typo_detector_min_users_configurable():
    """Test that we can change minimum users requirement"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            # Mock the OpenAI client to return that it's a typo
            mock_openai_instance = Mock()
            mock_openai_instance.make_request.return_value = "YES"
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            
            # Change min users to 2 for testing
            detector._min_users = 2
            
            # Create mock context and bot
            context = Mock()
            context.bot.send_message = Mock()
            
            # Simulate the tendeyu case with min_users=2
            # User2: "he was a limão siciliano boy she was a aroma sense girl tendeyu"
            msg1 = create_mock_message(user_id=2, text="he was a limão siciliano boy she was a aroma sense girl tendeyu", message_id=1)
            update1 = create_mock_update(msg1)
            detector._process(update1, context)
            
            # User2: "tendeyu"
            msg2 = create_mock_message(user_id=2, text="tendeyu", message_id=2)
            update2 = create_mock_update(msg2)
            detector._process(update2, context)
            
            # User1: "tendeyu" - should trigger now with min_users=2
            msg3 = create_mock_message(user_id=1, text="tendeyu", message_id=3)
            update3 = create_mock_update(msg3)
            detector._process(update3, context)
            
            # Should trigger with 2 users
            assert context.bot.send_message.call_count == 1


def test_typo_detector_photo_caption():
    """Test that detector processes photo captions"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            # Mock the OpenAI client to return that it's a typo
            mock_openai_instance = Mock()
            mock_openai_instance.make_request.return_value = "YES"
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            detector._min_users = 2  # Lower threshold for testing
            
            # Create mock context and bot
            context = Mock()
            context.bot.send_message = Mock()
            
            # Create a mock photo message with caption
            msg1 = create_mock_message(user_id=1, text=None, message_id=1)
            msg1.caption = "aquela de casa sexta né"
            msg1.text = None
            update1 = create_mock_update(msg1)
            detector._process(update1, context)
            
            # User2: "casa"
            msg2 = create_mock_message(user_id=2, text="casa", message_id=2)
            update2 = create_mock_update(msg2)
            detector._process(update2, context)
            
            # Should trigger with 2 users using "casa" from photo caption
            assert context.bot.send_message.call_count == 1
            
            # Check the call arguments
            call_args = context.bot.send_message.call_args
            assert call_args[1]['chat_id'] == -1001467780714
            assert "proibido errar" in call_args[1]['text']
            assert call_args[1]['reply_to_message_id'] == 1  # Reply to original photo message


def test_typo_detector_gpt_says_no():
    """Test that detector doesn't trigger when GPT says it's not a typo"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        with patch('commands.typo_detector.OpenAIClient') as mock_openai_class:
            # Mock the OpenAI client to return that it's NOT a typo
            mock_openai_instance = Mock()
            mock_openai_instance.make_request.return_value = "NO"
            mock_openai_class.return_value = mock_openai_instance
            
            detector = TypoDetector()
            
            # Create mock context and bot
            context = Mock()
            context.bot.send_message = Mock()
            
            # Simulate 3 users saying the same word
            msg1 = create_mock_message(user_id=1, text="hello world", message_id=1)
            update1 = create_mock_update(msg1)
            detector._process(update1, context)
            
            msg2 = create_mock_message(user_id=2, text="hello", message_id=2)
            update2 = create_mock_update(msg2)
            detector._process(update2, context)
            
            msg3 = create_mock_message(user_id=3, text="hello", message_id=3)
            update3 = create_mock_update(msg3)
            detector._process(update3, context)
            
            # Should not trigger because GPT said NO
            assert context.bot.send_message.call_count == 0