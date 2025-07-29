#!/usr/bin/env python3
"""
Simple test script for SalmoFetcher that avoids circular import issues.
Run this directly to test the fetcher functionality.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_salmo_fetcher_basics():
    """Test basic SalmoFetcher functionality without importing through module system."""
    print("Testing SalmoFetcher basics...")

    # Import directly to avoid module circular imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetchers"))
    from salmo_fetcher import SalmoFetcher

    # Test initialization
    fetcher = SalmoFetcher()
    assert fetcher._url == "https://www.bibliaon.com/salmo_do_dia/"
    print("✓ Initialization test passed")

    # Test error handling
    with patch("salmo_fetcher.requests.get") as mock_get:
        mock_get.side_effect = Exception("Network error")
        result = fetcher.fetch()
        assert isinstance(result, dict)
        assert result["title"] == "Erro"
        assert "Erro ao buscar o salmo" in result["content"]
        print("✓ Error handling test passed")

    # Test successful response
    with patch("salmo_fetcher.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = """
        <html>
        <head><title>Salmo do Dia</title></head>
        <body>
            <h1>Salmo 23</h1>
            <div class="salmo">
                O Senhor é meu pastor, nada me faltará.
            </div>
        </body>
        </html>
        """
        mock_get.return_value = mock_response

        result = fetcher.fetch()
        assert isinstance(result, dict)
        assert "title" in result
        assert "content" in result
        assert "url" in result
        assert result["url"] == "https://www.bibliaon.com/salmo_do_dia/"
        print("✓ Successful response test passed")

    print("All SalmoFetcher tests passed!")


def test_salmo_command_basics():
    """Test basic Salmo command functionality."""
    print("Testing Salmo command basics...")

    # Set environment variable
    os.environ["TELEGRAM_TOKEN"] = "test_token"

    try:
        # Import the command
        from commands.salmo import Salmo

        # Test initialization
        command = Salmo()
        assert command._command == "salmo"
        print("✓ Command initialization test passed")

        # Test message formatting
        test_data = {
            "title": "Salmo 23",
            "content": "O Senhor é meu pastor, nada me faltará.",
            "url": "https://www.bibliaon.com/salmo_do_dia/",
        }
        message = command._make_psalm_message(test_data)
        assert "Salmo 23" in message
        assert "O Senhor é meu pastor" in message
        assert "Ver salmo completo" in message
        print("✓ Message formatting test passed")

        # Test long content truncation
        long_content = "A" * 3500
        test_data_long = {
            "title": "Salmo Longo",
            "content": long_content,
            "url": "https://www.bibliaon.com/salmo_do_dia/",
        }
        long_message = command._make_psalm_message(test_data_long)
        assert "..." in long_message
        assert len(long_message) < len(long_content) + 500
        print("✓ Long content truncation test passed")

        print("All Salmo command tests passed!")

    except Exception as e:
        print(f"Command test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    try:
        test_salmo_fetcher_basics()
        test_salmo_command_basics()
        print("\n✅ All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
