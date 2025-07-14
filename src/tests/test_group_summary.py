from unittest.mock import Mock, patch
import pytest
import os
from commands.group_summary import GroupSummary
from modules.singleton import Singleton


def teardown_function():
    """Clear singleton instances after each test."""
    if GroupSummary in Singleton._instances:
        del Singleton._instances[GroupSummary]
    # Also clear Environment singleton
    from environment import Environment
    if Environment in Singleton._instances:
        del Singleton._instances[Environment]


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_group_summary_initialization(mock_openai_client):
    """Test that GroupSummary initializes correctly."""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    assert -1001467780714 in summary._target_group_ids  # Default group should be included
    assert "6 falam" in summary._trigger_patterns
    assert "vcs falam" in summary._trigger_patterns
    assert "ces falam" in summary._trigger_patterns
    assert "6️⃣" in summary._trigger_patterns
    assert len(summary._message_buffer) == 0


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_should_trigger_correct_group(mock_openai_client):
    """Test trigger detection for correct group."""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    
    # Should trigger in correct group with trigger phrase
    assert summary._should_trigger("hey 6 falam", -1001467780714)
    assert summary._should_trigger("VCS FALAM mesmo", -1001467780714)
    assert summary._should_trigger("ces falam agora", -1001467780714)
    assert summary._should_trigger("6️⃣", -1001467780714)
    
    # Should not trigger in wrong group
    assert not summary._should_trigger("6 falam", -123456789)
    
    # Should not trigger without trigger phrase
    assert not summary._should_trigger("hello world", -1001467780714)


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_store_message(mock_openai_client):
    """Test message storage functionality."""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    
    # Clear any existing messages
    summary._message_buffer.clear()
    
    # Mock message from target group
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


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_get_recent_messages(mock_openai_client):
    """Test recent message retrieval."""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    
    # Clear any existing messages  
    summary._message_buffer.clear()
    
    # Test with empty buffer
    messages = summary._get_recent_messages()
    assert messages == ["[Nenhuma mensagem recente disponível]"]
    
    # Add some mock messages
    summary._message_buffer.append({
        "user": "user1",
        "text": "message 1",
        "timestamp": "2024-01-01"
    })
    summary._message_buffer.append({
        "user": "user2", 
        "text": "message 2",
        "timestamp": "2024-01-01"
    })
    
    messages = summary._get_recent_messages()
    assert len(messages) == 2
    assert "user1: message 1" in messages
    assert "user2: message 2" in messages


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_summarize_messages(mock_openai_client):
    """Test message summarization functionality."""
    mock_openai_instance = Mock()
    mock_openai_instance.make_request.return_value = "Este é um resumo dos tópicos discutidos."
    mock_openai_client.return_value = mock_openai_instance
    
    summary = GroupSummary()
    
    messages = [
        "user1: Olá pessoal!",
        "user2: Como vocês estão?", 
        "user3: Vamos conversar sobre futebol"
    ]
    
    result = summary._summarize_messages(messages)
    assert result == "Este é um resumo dos tópicos discutidos."
    
    # Verify OpenAI was called with correct parameters
    mock_openai_instance.make_request.assert_called_once()
    call_args = mock_openai_instance.make_request.call_args
    assert call_args[1]['max_tokens'] == 300
    
    # Check that the messages were formatted correctly
    messages_arg = call_args[1]['messages']
    assert len(messages_arg) == 2  # system + user message
    assert messages_arg[0]['role'] == 'system'
    assert 'português brasileiro' in messages_arg[0]['content']
    assert messages_arg[1]['role'] == 'user'
    assert 'user1: Olá pessoal!' in messages_arg[1]['content']


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')  
def test_process_trigger_message(mock_openai_client):
    """Test processing a message that triggers the summary."""
    mock_openai_instance = Mock()
    mock_openai_instance.make_request.return_value = "Resumo: conversa sobre diversos tópicos."
    mock_openai_client.return_value = mock_openai_instance
    
    summary = GroupSummary()
    summary._message_buffer.clear()
    
    # Add some messages to the buffer first
    for i in range(10):
        summary._message_buffer.append({
            "user": f"user{i}",
            "text": f"mensagem {i}",
            "timestamp": "2024-01-01"
        })
    
    # Create mock update and context
    update = Mock()
    update.message.chat_id = -1001467780714
    update.message.text = "6 falam mesmo!"
    update.message.from_user.id = 123
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.date = "2024-01-01"
    
    context = Mock()
    
    # Process the message
    summary._process(update, context)
    
    # Verify bot.send_message was called with correct response
    context.bot.send_message.assert_called_once()
    call_args = context.bot.send_message.call_args
    assert call_args[1]['chat_id'] == -1001467780714
    assert "6️⃣ falam eim! Foi falado:" in call_args[1]['text']
    assert "Resumo: conversa sobre diversos tópicos." in call_args[1]['text']


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_process_insufficient_messages(mock_openai_client):
    """Test processing when there aren't enough messages to summarize."""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    summary._message_buffer.clear()
    
    # Add only a couple messages (less than 5)
    for i in range(2):
        summary._message_buffer.append({
            "user": f"user{i}",
            "text": f"mensagem {i}",
            "timestamp": "2024-01-01"
        })
    
    # Create mock update and context
    update = Mock()
    update.message.chat_id = -1001467780714
    update.message.text = "6 falam"
    update.message.from_user.id = 123
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.date = "2024-01-01"
    
    context = Mock()
    
    # Process the message
    summary._process(update, context)
    
    # Verify appropriate message was sent
    context.bot.send_message.assert_called_once()
    call_args = context.bot.send_message.call_args
    assert "ainda não tenho mensagens suficientes" in call_args[1]['text']


@patch.dict(os.environ, {'TELEGRAM_TOKEN': 'test_token'})
@patch('commands.group_summary.OpenAIClient')
def test_process_wrong_group(mock_openai_client):
    """Test that messages from wrong group don't trigger summary."""
    mock_openai_client.return_value = Mock()
    summary = GroupSummary()
    
    # Create mock update from different group
    update = Mock()
    update.message.chat_id = -999999999  # Different group
    update.message.text = "6 falam"
    update.message.from_user.id = 123
    update.message.from_user.username = "testuser"
    update.message.from_user.full_name = "Test User"
    update.message.date = "2024-01-01"
    
    context = Mock()
    
    # Process the message
    summary._process(update, context)
    
    # Verify no response was sent
    context.bot.send_message.assert_not_called()


@patch('commands.group_summary.OpenAIClient')
def test_multiple_groups_configuration(mock_openai_client):
    """Test that GroupSummary supports multiple groups from environment."""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-111,-222,-333'
    }):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()
        
        # Should have all configured groups
        assert -111 in summary._target_group_ids
        assert -222 in summary._target_group_ids
        assert -333 in summary._target_group_ids
        assert len(summary._target_group_ids) == 3


@patch('commands.group_summary.OpenAIClient')
def test_trigger_in_multiple_groups(mock_openai_client):
    """Test trigger detection works in all configured groups."""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-111,-222,-333'
    }):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()
        
        # Should trigger in all configured groups
        assert summary._should_trigger("6 falam", -111)
        assert summary._should_trigger("6 falam", -222)
        assert summary._should_trigger("6 falam", -333)
        
        # Should not trigger in unconfigured groups
        assert not summary._should_trigger("6 falam", -444)
        assert not summary._should_trigger("6 falam", -999)


@patch('commands.group_summary.OpenAIClient')
def test_store_messages_from_multiple_groups(mock_openai_client):
    """Test message storage from multiple configured groups."""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-111,-222,-333'
    }):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()
        summary._message_buffer.clear()
        
        # Create messages from different groups
        for group_id in [-111, -222, -333]:
            message = Mock()
            message.chat_id = group_id
            message.text = f"Test message from group {group_id}"
            message.from_user.username = "testuser"
            message.from_user.first_name = "Test"
            message.date = "2024-01-01"
            
            summary._store_message(message)
        
        # Should have stored messages from all groups
        assert len(summary._message_buffer) == 3
        
        # Verify messages are from different groups
        stored_texts = [msg["text"] for msg in summary._message_buffer]
        assert "Test message from group -111" in stored_texts
        assert "Test message from group -222" in stored_texts
        assert "Test message from group -333" in stored_texts


@patch('commands.group_summary.OpenAIClient')
def test_ignore_messages_from_unconfigured_groups(mock_openai_client):
    """Test that messages from unconfigured groups are ignored."""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'SUMMARY_GROUP_IDS': '-111,-222'
    }):
        mock_openai_client.return_value = Mock()
        summary = GroupSummary()
        summary._message_buffer.clear()
        
        # Try to store message from unconfigured group
        message = Mock()
        message.chat_id = -999  # Not in configured groups
        message.text = "Test message from unconfigured group"
        message.from_user.username = "testuser"
        message.from_user.first_name = "Test"
        message.date = "2024-01-01"
        
        summary._store_message(message)
        
        # Should not store the message
        assert len(summary._message_buffer) == 0