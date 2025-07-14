from unittest.mock import patch
import pytest
import os
from environment import Environment
from modules.singleton import Singleton


def teardown_function():
    # clear singleton instances after each test
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]


def test_environment_basic_initialization():
    with patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'}):
        env = Environment()
        assert env.telegram_token == 'test_token'
        assert env.allowed_user_ids == []  # no user restrictions
        assert env.summary_group_ids == [-1001467780714]  # default group


def test_environment_with_allowed_users():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123,456,789'
    }):
        env = Environment()
        assert env.telegram_token == 'test_token'
        assert env.allowed_user_ids == [123, 456, 789]
        assert env.summary_group_ids == [-1001467780714]  # default group


def test_environment_with_summary_groups():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-111,-222,-333'
    }):
        env = Environment()
        assert env.telegram_token == 'test_token'
        assert env.allowed_user_ids == []  # no user restrictions
        assert env.summary_group_ids == [-111, -222, -333]


def test_environment_with_whitespace():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '123, 456 , 789 ',
        'SUMMARY_GROUP_IDS': ' -111 , -222, -333 '
    }):
        env = Environment()
        assert env.allowed_user_ids == [123, 456, 789]
        assert env.summary_group_ids == [-111, -222, -333]


def test_environment_with_empty_lists():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': '',
        'SUMMARY_GROUP_IDS': ''
    }):
        env = Environment()
        assert env.allowed_user_ids == []
        assert env.summary_group_ids == []


def test_environment_with_invalid_user_ids():
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ALLOWED_USER_IDS': 'invalid,456,not_a_number'
    }):
        env = Environment()
        # invalid IDs should result in empty list due to error handling
        assert env.allowed_user_ids == []


def test_environment_missing_token():
    # test that missing TELEGRAM_TOKEN causes system exit
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(SystemExit):
            Environment()