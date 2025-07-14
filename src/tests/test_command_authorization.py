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


def test_command_authorization_open_access():
    with patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'}):
        command = Command()
        
        # when no allowed_user_ids are configured, all users should be authorized
        assert command._is_user_authorized(123)
        assert command._is_user_authorized(456) 
        assert command._is_user_authorized(999)


def test_command_authorization_restricted_access():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456,789'
    }):
        command = Command()
        
        # only allowed users should be authorized
        assert command._is_user_authorized(123)
        assert command._is_user_authorized(456)
        assert command._is_user_authorized(789)
        
        # unauthorized users should be rejected
        assert not command._is_user_authorized(999)
        assert not command._is_user_authorized(111)


def test_command_process_authorized_user():
    with patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'}):
        command = Command()
        command._command = "test"
        
        # create mock update and context
        update = Mock()
        update.message.from_user.id = 123
        update.message.from_user.username = "testuser"
        update.message.from_user.full_name = "Test User"
        update.message.text = "/test"
        update.message.chat.id = 456
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send processing message
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == 456
        assert "Processando comando..." in call_args[1]['text']


def test_command_process_unauthorized_user():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456'
    }):
        command = Command()
        command._command = "test"
        
        # create mock update for unauthorized user
        update = Mock()
        update.message.from_user.id = 999  # not in allowed list
        update.message.from_user.username = "unauthorizeduser"
        update.message.from_user.full_name = "Unauthorized User"
        update.message.text = "/test"
        update.message.chat.id = 456
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send unauthorized message
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == 456
        assert "🚫 Você não tem permissão para usar este comando." in call_args[1]['text']


def test_command_process_authorized_user_with_restrictions():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456'
    }):
        command = Command()
        command._command = "test"
        
        # create mock update for authorized user
        update = Mock()
        update.message.from_user.id = 123  # in allowed list
        update.message.from_user.username = "authorizeduser"
        update.message.from_user.full_name = "Authorized User"
        update.message.text = "/test"
        update.message.chat.id = 456
        
        context = Mock()
        
        # process the command
        result = command._process(update, context)
        
        # should send processing message
        context.bot.send_message.assert_called_once()
        call_args = context.bot.send_message.call_args
        assert call_args[1]['chat_id'] == 456
        assert "Processando comando..." in call_args[1]['text']