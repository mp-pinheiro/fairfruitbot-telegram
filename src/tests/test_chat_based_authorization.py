from unittest.mock import Mock, patch
import pytest
import os
from commands.command import Command
from modules.singleton import Singleton


def teardown_function():
    # clear singleton instances after each test
    if Command in Singleton._instances:
        del Singleton._instances[Command]
    from environment import Environment
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]


def test_private_chat_authorized_user():
    """Test that authorized users can use commands in private chat"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456'
    }):
        command = Command()
        
        # authorized user in private chat should be allowed
        assert command._is_user_authorized(123, 'private', 999)
        assert command._is_user_authorized(456, 'private', 999)


def test_private_chat_unauthorized_user():
    """Test that unauthorized users cannot use commands in private chat"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456'
    }):
        command = Command()
        
        # unauthorized user in private chat should be rejected
        assert not command._is_user_authorized(999, 'private', 888)


def test_group_chat_any_user_in_allowed_group():
    """Test that any user can use commands in allowed groups"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456',
        'SUMMARY_GROUP_IDS': '-1001111,-1002222'
    }):
        command = Command()
        
        # any user (including unauthorized) should be allowed in allowed groups
        assert command._is_user_authorized(123, 'group', -1001111)  # authorized user
        assert command._is_user_authorized(999, 'group', -1001111)  # unauthorized user
        assert command._is_user_authorized(777, 'supergroup', -1002222)  # unauthorized user in supergroup


def test_group_chat_user_in_disallowed_group():
    """Test that users cannot use commands in non-allowed groups"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456',
        'SUMMARY_GROUP_IDS': '-1001111,-1002222'
    }):
        command = Command()
        
        # users should not be allowed in groups not in summary list
        assert not command._is_user_authorized(123, 'group', -1003333)  # authorized user in disallowed group
        assert not command._is_user_authorized(999, 'group', -1003333)  # unauthorized user in disallowed group


def test_no_user_restrictions_no_group_restrictions():
    """Test that when no restrictions are configured, all users are allowed everywhere"""
    with patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'}):
        command = Command()
        
        # all users should be allowed everywhere when no restrictions
        assert command._is_user_authorized(123, 'private', 999)
        assert command._is_user_authorized(999, 'group', -1001111)
        assert command._is_user_authorized(777, 'supergroup', -1002222)


def test_user_restrictions_no_group_restrictions():
    """Test that when user restrictions exist but no group restrictions, all groups are allowed"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456'
    }):
        command = Command()
        
        # private chat should still use user restrictions
        assert command._is_user_authorized(123, 'private', 999)
        assert not command._is_user_authorized(999, 'private', 888)
        
        # but groups should allow any user when no group restrictions
        assert command._is_user_authorized(123, 'group', -1001111)
        assert command._is_user_authorized(999, 'group', -1001111)


def test_process_private_chat_authorized():
    """Test _process method with authorized user in private chat"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123'
    }):
        command = Command()
        command._command = "test"
        
        # create mock update for private chat with authorized user
        update = Mock()
        update.message.from_user.id = 123
        update.message.from_user.username = "testuser"
        update.message.from_user.full_name = "Test User"
        update.message.text = "/test"
        update.message.chat.id = 456
        update.message.chat.type = 'private'
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send processing message
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == 456
        assert "Processando comando..." in call_args[1]['text']


def test_process_private_chat_unauthorized():
    """Test _process method with unauthorized user in private chat"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123'
    }):
        command = Command()
        command._command = "test"
        
        # create mock update for private chat with unauthorized user
        update = Mock()
        update.message.from_user.id = 999
        update.message.from_user.username = "unauthorized"
        update.message.from_user.full_name = "Unauthorized User"
        update.message.text = "/test"
        update.message.chat.id = 456
        update.message.chat.type = 'private'
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send unauthorized message
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == 456
        assert "🚫 Você não tem permissão para usar este comando." in call_args[1]['text']


def test_process_group_chat_unauthorized_user_allowed_group():
    """Test _process method with unauthorized user in allowed group"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123',
        'SUMMARY_GROUP_IDS': '-1001111'
    }):
        command = Command()
        command._command = "test"
        
        # create mock update for group chat with unauthorized user in allowed group
        update = Mock()
        update.message.from_user.id = 999  # not in allowed users
        update.message.from_user.username = "unauthorized"
        update.message.from_user.full_name = "Unauthorized User"
        update.message.text = "/test"
        update.message.chat.id = -1001111  # allowed group
        update.message.chat.type = 'group'
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send processing message (allowed because group is allowed)
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == -1001111
        assert "Processando comando..." in call_args[1]['text']


def test_process_group_chat_unauthorized_user_disallowed_group():
    """Test _process method with unauthorized user in disallowed group"""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123',
        'SUMMARY_GROUP_IDS': '-1001111'
    }):
        command = Command()
        command._command = "test"
        
        # create mock update for group chat with unauthorized user in disallowed group
        update = Mock()
        update.message.from_user.id = 999  # not in allowed users
        update.message.from_user.username = "unauthorized"
        update.message.from_user.full_name = "Unauthorized User"
        update.message.text = "/test"
        update.message.chat.id = -1002222  # not in allowed groups
        update.message.chat.type = 'group'
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send unauthorized message
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == -1002222
        assert "🚫 Você não tem permissão para usar este comando." in call_args[1]['text']