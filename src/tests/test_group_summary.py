from unittest.mock import Mock
import pytest
from commands.group_summary import GroupSummary


def test_group_summary_initialization():
    """Test that GroupSummary initializes correctly."""
    summary = GroupSummary()
    assert summary._target_group_id == -1001467780714
    assert "6 falam" in summary._trigger_patterns
    assert "vcs falam" in summary._trigger_patterns
    assert "ces falam" in summary._trigger_patterns
    assert "6️⃣" in summary._trigger_patterns
    assert len(summary._message_buffer) == 0


def test_should_trigger_correct_group():
    """Test trigger detection for correct group."""
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


def test_store_message():
    """Test message storage functionality."""
    summary = GroupSummary()
    
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


def test_get_recent_messages():
    """Test recent message retrieval."""
    summary = GroupSummary()
    
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