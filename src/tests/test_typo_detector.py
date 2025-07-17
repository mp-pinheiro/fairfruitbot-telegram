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
        'SUMMARY_GROUP_IDS': '-1001467780714'
    }):
        detector = TypoDetector()
        assert detector._min_users == 3
        assert -1001467780714 in detector._target_group_ids
        assert len(detector._message_buffer) == 0


def test_typo_detector_fazedo_case():
    """Test the 'fazedo' case from the issue - should trigger with 3 users"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714'
    }):
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
        
        # User3: "fazedo" - this should trigger
        msg5 = create_mock_message(user_id=3, text="fazedo", message_id=5)
        update5 = create_mock_update(msg5)
        detector._process(update5, context)
        
        # Should trigger here - we have 3 users (1, 3) with "fazedo"
        # User1 used it in longer message, User3 used it as full message
        assert context.bot.send_message.call_count == 1
        
        # Check the call arguments
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == -1001467780714
        assert "proibido errar" in call_args[1]['text']
        assert call_args[1]['reply_to_message_id'] == 1  # Reply to original message


def test_typo_detector_tendeyu_case():
    """Test the 'tendeyu' case from the issue - should not trigger with only 2 users"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714'
    }):
        detector = TypoDetector()
        
        # Create mock context and bot
        context = Mock()
        context.bot.send_message = Mock()
        
        # Simulate the tendeyu case from the issue
        # User2: "he was a limão siciliano boy she was a aroma sense girl tendeyu"
        msg1 = create_mock_message(user_id=2, text="he was a limão siciliano boy she was a aroma sense girl tendeyu", message_id=1)
        update1 = create_mock_update(msg1)
        detector._process(update1, context)
        
        # User2: "tendeyu"
        msg2 = create_mock_message(user_id=2, text="tendeyu", message_id=2)
        update2 = create_mock_update(msg2)
        detector._process(update2, context)
        
        # User1: "tendeyu"
        msg3 = create_mock_message(user_id=1, text="tendeyu", message_id=3)
        update3 = create_mock_update(msg3)
        detector._process(update3, context)
        
        # Should not trigger - only 2 users (1, 2) but needs 3
        assert context.bot.send_message.call_count == 0


def test_typo_detector_extract_potential_typos():
    """Test typo extraction logic"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714'
    }):
        detector = TypoDetector()
        
        # Test various cases
        assert "fazedo" in detector._extract_potential_typos("fazedo piadinha")
        assert "tendeyu" in detector._extract_potential_typos("tendeyu")
        assert "mudno" in detector._extract_potential_typos("ola mudno, isso é um exemplo")
        
        # Test that common words are filtered out
        assert "isso" not in detector._extract_potential_typos("ola mudno, isso é um exemplo")
        assert "exemplo" not in detector._extract_potential_typos("ola mudno, isso é um exemplo")


def test_typo_detector_different_chat():
    """Test that detector ignores messages from non-target chats"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-1001467780714'
    }):
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
        'SUMMARY_GROUP_IDS': '-1001467780714'
    }):
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