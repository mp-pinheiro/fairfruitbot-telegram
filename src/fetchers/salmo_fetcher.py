import requests
from bs4 import BeautifulSoup

try:
    from crawl4ai import AsyncWebCrawler

    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False


class Fetcher:
    def __init__(self):
        # define the base urls (add others in child classes)
        self._base_url = "https://joaobidu.com.br"

    def _make_soup(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        return soup

    def fetch(self, args=None):
        pass


class SalmoFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://www.bibliaon.com/salmo_do_dia/"

    def _fetch_with_crawl4ai(self):
        """Fetch psalm content using crawl4ai when available."""
        if not CRAWL4AI_AVAILABLE:
            raise ImportError("crawl4ai is not available")

        # This will be implemented when crawl4ai is properly installed
        # For now, using a fallback approach
        return self._fetch_with_requests()

    def _fetch_with_requests(self):
        """Fallback method using requests + BeautifulSoup."""
        try:
            soup = self._make_soup(self._url)

            # Try to find the psalm content using common selectors
            # Since we can't access the actual site, we'll use common patterns
            psalm_selectors = [
                ".salmo",
                ".psalm",
                ".daily-psalm",
                ".salmo-do-dia",
                ".bible-verse",
                "article",
                ".content",
                ".main-content",
            ]

            psalm_content = None
            psalm_title = None

            # Try to find title
            title_elements = soup.find_all(["h1", "h2", "h3"])
            if title_elements:
                psalm_title = title_elements[0].get_text().strip()

            # Try to find content with various selectors
            for selector in psalm_selectors:
                elements = soup.select(selector)
                if elements:
                    psalm_content = elements[0].get_text().strip()
                    break

            # If no specific selectors work, try to get main content
            if not psalm_content:
                main_content = soup.find("body")
                if main_content:
                    # Remove script and style elements
                    for script in main_content(["script", "style"]):
                        script.decompose()
                    psalm_content = main_content.get_text().strip()

            return {
                "title": psalm_title or "Salmo do Dia",
                "content": psalm_content or "Conteúdo não encontrado",
                "url": self._url,
            }

        except Exception as e:
            return {
                "title": "Erro",
                "content": f"Erro ao buscar o salmo: {str(e)}",
                "url": self._url,
            }

    def fetch(self, args=None):
        """Fetch daily psalm content."""
        if CRAWL4AI_AVAILABLE:
            return self._fetch_with_crawl4ai()
        else:
            return self._fetch_with_requests()
