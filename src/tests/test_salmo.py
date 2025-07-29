import unittest
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSalmoFetcher(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Import the fetcher directly to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetchers"))
        from salmo_fetcher import SalmoFetcher

        self.salmo_fetcher = SalmoFetcher()

    def test_salmo_fetcher_with_successful_response(self):
        """Test SalmoFetcher with a successful response."""
        # Import the fetcher directly to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetchers"))
        from salmo_fetcher import SalmoFetcher
        
        with patch('salmo_fetcher.requests.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.text = """
            <html>
            <head><title>Salmo do Dia</title></head>
            <body>
                <h1>Salmo 23</h1>
                <div class="salmo">
                    O Senhor é meu pastor, nada me faltará.
                    Em verdes pastos me faz descansar.
                </div>
            </body>
            </html>
            """
            mock_get.return_value = mock_response

            fetcher = SalmoFetcher()
            result = fetcher.fetch()

            self.assertIsInstance(result, dict)
            self.assertIn("title", result)
            self.assertIn("content", result)
            self.assertIn("url", result)
            self.assertEqual(result["url"], "https://www.bibliaon.com/salmo_do_dia/")

    def test_salmo_fetcher_with_error(self):
        """Test SalmoFetcher with network error."""
        # Import the fetcher directly to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fetchers"))
        from salmo_fetcher import SalmoFetcher
        
        with patch('salmo_fetcher.requests.get') as mock_get:
            # Mock network error
            mock_get.side_effect = Exception("Network error")

            fetcher = SalmoFetcher()
            result = fetcher.fetch()

            self.assertIsInstance(result, dict)
            self.assertEqual(result["title"], "Erro ao carregar salmo")
            self.assertIn("Não foi possível buscar o salmo do dia", result["content"])

    def test_salmo_fetcher_initialization(self):
        """Test that SalmoFetcher initializes correctly."""
        self.assertEqual(
            self.salmo_fetcher._url, "https://www.bibliaon.com/salmo_do_dia/"
        )


if __name__ == "__main__":
    unittest.main()
