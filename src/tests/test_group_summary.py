from unittest.mock import Mock, patch
import pytest
import os
from commands.group_summary import GroupSummary
from modules.singleton import Singleton


def teardown_function():
    # clear singleton instances after each test
    if GroupSummary in Singleton._instances:
        del Singleton._instances[GroupSummary]
    # also clear Environment singleton
    from environment import Environment

    if Environment in Singleton._instances:
        del Singleton._instances[Environment]


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_group_summary_initialization(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    assert (
        -1001467780714 in summary._target_group_ids
    )  # default group should be included
    assert "6 falam" in summary._trigger_patterns
    assert "vcs falam" in summary._trigger_patterns
    assert "ces falam" in summary._trigger_patterns
    assert "6️⃣" in summary._trigger_patterns
    assert len(summary._message_buffer) == 0


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_should_trigger_correct_group(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # should trigger in correct group with trigger phrase
    assert summary._should_trigger("hey 6 falam", -1001467780714)
    assert summary._should_trigger("VCS FALAM mesmo", -1001467780714)
    assert summary._should_trigger("ces falam agora", -1001467780714)
    assert summary._should_trigger("6️⃣", -1001467780714)

    # should not trigger in wrong group
    assert not summary._should_trigger("6 falam", -123456789)

    # should not trigger without trigger phrase
    assert not summary._should_trigger("hello world", -1001467780714)


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_store_message(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # clear any existing messages
    summary._message_buffer.clear()

    # mock message from target group
    message = Mock()
    message.chat_id = -1001467780714
    message.text = "Test message"
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.date = "2024-01-01"

    summary._store_message(message)
    assert len(summary._message_buffer) == 1

    stored_msg = summary._message_buffer[0]
    assert stored_msg["user"] == "testuser"
    assert stored_msg["text"] == "Test message"


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_get_recent_messages(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # clear any existing messages
    summary._message_buffer.clear()

    # test with empty buffer
    messages = summary._get_recent_messages()
    assert messages == ["[Nenhuma mensagem recente disponível]"]

    # add some mock messages
    summary._message_buffer.append(
        {"user": "user1", "text": "message 1", "timestamp": "2024-01-01"}
    )
    summary._message_buffer.append(
        {"user": "user2", "text": "message 2", "timestamp": "2024-01-01"}
    )

    messages = summary._get_recent_messages()
    assert len(messages) == 2
    assert "user1: message 1" in messages
    assert "user2: message 2" in messages


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_summarize_messages(mock_openai_client):
    mock_openai_instance = Mock()
    mock_openai_instance.make_request.return_value = (
        "Este é um resumo dos tópicos discutidos."
    )
    mock_openai_client.return_value = mock_openai_instance

    summary = GroupSummary()

    messages = [
        "user1: Olá pessoal!",
        "user2: Como vocês estão?",
        "user3: Vamos conversar sobre futebol",
    ]

    result = summary._summarize_messages(messages)
    assert result == "Este é um resumo dos tópicos discutidos."

    # verify OpenAI was called with correct parameters
    mock_openai_instance.make_request.assert_called_once()
    call_args = mock_openai_instance.make_request.call_args
    assert call_args[1]["max_tokens"] == 300

    # check that the messages were formatted correctly
    messages_arg = call_args[1]["messages"]
    assert len(messages_arg) == 2  # system + user message
    assert messages_arg[0]["role"] == "system"
    assert "português brasileiro" in messages_arg[0]["content"]
    assert messages_arg[1]["role"] == "user"
    assert "user1: Olá pessoal!" in messages_arg[1]["content"]


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_process_trigger_message(mock_openai_client):
    mock_openai_instance = Mock()
    mock_openai_instance.make_request.return_value = (
        "Resumo: conversa sobre diversos tópicos."
    )
    mock_openai_client.return_value = mock_openai_instance

    summary = GroupSummary()
    summary._message_buffer.clear()

    # add some messages to the buffer first
    for i in range(10):
        summary._message_buffer.append(
            {"user": f"user{i}", "text": f"mensagem {i}", "timestamp": "2024-01-01"}
        )

    # create mock update and context
    update = Mock()
    update.message.chat_id = -1001467780714
    update.message.text = "6 falam mesmo!"
    update.message.from_user.id = 123
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.date = "2024-01-01"

    context = Mock()

    # process the message
    summary._process(update, context)

    # verify bot.send_message was called with correct response
    context.bot.send_message.assert_called_once()
    call_args = context.bot.send_message.call_args
    assert call_args[1]["chat_id"] == -1001467780714
    assert "6️⃣ falam eim!" in call_args[1]["text"]
    assert "Resumo: conversa sobre diversos tópicos." in call_args[1]["text"]
    assert "Resumo gerado por Bidu-GPT." in call_args[1]["text"]


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_process_insufficient_messages(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    summary._message_buffer.clear()

    # add only a couple messages (less than 5)
    for i in range(2):
        summary._message_buffer.append(
            {"user": f"user{i}", "text": f"mensagem {i}", "timestamp": "2024-01-01"}
        )

    # create mock update and context
    update = Mock()
    update.message.chat_id = -1001467780714
    update.message.text = "6 falam"
    update.message.from_user.id = 123
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.date = "2024-01-01"

    context = Mock()

    # process the message
    summary._process(update, context)

    # verify appropriate message was sent
    context.bot.send_message.assert_called_once()
    call_args = context.bot.send_message.call_args
    assert "ainda não tenho mensagens suficientes" in call_args[1]["text"]


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_process_wrong_group(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # create mock update from different group
    update = Mock()
    update.message.chat_id = -999999999  # different group
    update.message.text = "6 falam"
    update.message.from_user.id = 123
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.date = "2024-01-01"

    context = Mock()

    # process the message
    summary._process(update, context)

    # verify no response was sent
    context.bot.send_message.assert_not_called()


@patch("commands.group_summary.OpenAIClient")
def test_multiple_groups_configuration(mock_openai_client):
    with patch.dict(
        os.environ,
        {"TELEGRAM_TOKEN": "test_token", "SUMMARY_GROUP_IDS": "-111,-222,-333"},
    ):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()

        # should have all configured groups
        assert -111 in summary._target_group_ids
        assert -222 in summary._target_group_ids
        assert -333 in summary._target_group_ids
        assert len(summary._target_group_ids) == 3


@patch("commands.group_summary.OpenAIClient")
def test_trigger_in_multiple_groups(mock_openai_client):
    with patch.dict(
        os.environ,
        {"TELEGRAM_TOKEN": "test_token", "SUMMARY_GROUP_IDS": "-111,-222,-333"},
    ):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()

        # should trigger in all configured groups
        assert summary._should_trigger("6 falam", -111)
        assert summary._should_trigger("6 falam", -222)
        assert summary._should_trigger("6 falam", -333)

        # should not trigger in unconfigured groups
        assert not summary._should_trigger("6 falam", -444)
        assert not summary._should_trigger("6 falam", -999)


@patch("commands.group_summary.OpenAIClient")
def test_store_messages_from_multiple_groups(mock_openai_client):
    with patch.dict(
        os.environ,
        {"TELEGRAM_TOKEN": "test_token", "SUMMARY_GROUP_IDS": "-111,-222,-333"},
    ):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()
        summary._message_buffer.clear()

        # create messages from different groups
        for group_id in [-111, -222, -333]:
            message = Mock()
            message.chat_id = group_id
            message.text = f"Test message from group {group_id}"
            message.from_user.username = "testuser"
            message.from_user.first_name = "Test"
            message.date = "2024-01-01"

            summary._store_message(message)

        # should have stored messages from all groups
        assert len(summary._message_buffer) == 3

        # verify messages are from different groups
        stored_texts = [msg["text"] for msg in summary._message_buffer]
        assert "Test message from group -111" in stored_texts
        assert "Test message from group -222" in stored_texts
        assert "Test message from group -333" in stored_texts


@patch("commands.group_summary.OpenAIClient")
def test_ignore_messages_from_unconfigured_groups(mock_openai_client):
    with patch.dict(
        os.environ, {"TELEGRAM_TOKEN": "test_token", "SUMMARY_GROUP_IDS": "-111,-222"}
    ):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()
        summary._message_buffer.clear()

        # try to store message from unconfigured group
        message = Mock()
        message.chat_id = -999  # not in configured groups
        message.text = "Test message from unconfigured group"
        message.from_user.username = "testuser"
        message.from_user.first_name = "Test"
        message.date = "2024-01-01"

        summary._store_message(message)

        # should not store the message
        assert len(summary._message_buffer) == 0


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_get_recent_messages_filters_triggers(mock_openai_client):
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # clear any existing messages
    summary._message_buffer.clear()

    # add messages including trigger messages
    summary._message_buffer.append(
        {"user": "user1", "text": "message 1", "timestamp": "2024-01-01"}
    )
    summary._message_buffer.append(
        {
            "user": "user2",
            "text": "6 falam mesmo!",  # trigger message
            "timestamp": "2024-01-01",
        }
    )
    summary._message_buffer.append(
        {"user": "user3", "text": "message 3", "timestamp": "2024-01-01"}
    )
    summary._message_buffer.append(
        {
            "user": "user4",
            "text": "vcs falam agora",  # another trigger message
            "timestamp": "2024-01-01",
        }
    )

    messages = summary._get_recent_messages()
    assert len(messages) == 2  # only non-trigger messages
    assert "user1: message 1" in messages
    assert "user3: message 3" in messages
    assert "6 falam mesmo!" not in "\n".join(messages)
    assert "vcs falam agora" not in "\n".join(messages)


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_message_logging_is_robust(mock_openai_client):
    """Test that message logging happens even when other operations fail"""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # Mock logging to capture log calls
    with patch('commands.group_summary.logging') as mock_logging:
        # Create a message that would normally fail in _store_message
        message = Mock()
        message.chat_id = -1001467780714  # valid group
        message.text = "Test message"
        message.from_user = None  # This should cause issues in old implementation
        message.date = "2024-01-01"

        # Create update and context
        update = Mock()
        update.message = message
        context = Mock()

        # Process the message
        summary._process(update, context)

        # Verify that logging.info was called despite the potential error in user info extraction
        mock_logging.info.assert_called()
        
        # Check that the log message contains expected information
        log_call_args = mock_logging.info.call_args_list
        found_group_summary_log = False
        for call_args in log_call_args:
            if 'GroupSummary' in str(call_args[0][0]):
                found_group_summary_log = True
                assert '-1001467780714' in str(call_args[0][0])  # chat_id
                assert 'Test message' in str(call_args[0][0])  # message text
                break
        
        assert found_group_summary_log, "Expected GroupSummary log message not found"


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_logging_with_malformed_message(mock_openai_client):
    """Test that logging works even with completely malformed message objects"""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    with patch('commands.group_summary.logging') as mock_logging:
        # Create update with minimal message
        update = Mock()
        update.message = Mock()
        update.message.text = "Test message"
        update.message.chat_id = -1001467780714
        update.message.from_user = Mock()
        # Simulate exception when accessing user properties
        update.message.from_user.id = 123
        update.message.from_user.username = None
        update.message.from_user.full_name = None

        context = Mock()

        # Process the message
        summary._process(update, context)

        # Verify that some form of logging happened
        assert mock_logging.info.called or mock_logging.error.called
        
        # Should have logged the message despite user info issues
        log_calls = mock_logging.info.call_args_list + mock_logging.error.call_args_list
        found_message_log = any('Test message' in str(call) for call in log_calls)
        assert found_message_log, "Message text should be logged even with user info issues"


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})  
@patch("commands.group_summary.OpenAIClient")
def test_store_message_robustness(mock_openai_client):
    """Test that _store_message doesn't crash with malformed messages"""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    summary._message_buffer.clear()

    # Test with completely invalid message
    summary._store_message(None)
    assert len(summary._message_buffer) == 0

    # Test with message missing required attributes
    bad_message = Mock()
    # Don't set chat_id - should not crash
    summary._store_message(bad_message)
    assert len(summary._message_buffer) == 0

    # Test with message from non-target group
    bad_message.chat_id = -999999999  # wrong group
    bad_message.text = "test"
    summary._store_message(bad_message)
    assert len(summary._message_buffer) == 0

    # Test with valid message from target group but no user info
    good_message = Mock()
    good_message.chat_id = -1001467780714
    good_message.text = "Valid message"
    good_message.from_user = None  # No user info
    good_message.date = "2024-01-01"
    
    summary._store_message(good_message)
    # Should store the message even without user info
    assert len(summary._message_buffer) == 1
    assert summary._message_buffer[0]["text"] == "Valid message"
    assert summary._message_buffer[0]["user"] == "Unknown"


@patch.dict(os.environ, {"TELEGRAM_TOKEN": "test_token"})
@patch("commands.group_summary.OpenAIClient")
def test_should_trigger_robustness(mock_openai_client):
    """Test that _should_trigger doesn't crash with invalid inputs"""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()

    # Test with None message
    assert not summary._should_trigger(None, -1001467780714)
    
    # Test with empty message
    assert not summary._should_trigger("", -1001467780714)
    
    # Test with valid trigger in wrong group
    assert not summary._should_trigger("6 falam", -999999999)
    
    # Test with valid trigger in correct group
    assert summary._should_trigger("6 falam", -1001467780714)
