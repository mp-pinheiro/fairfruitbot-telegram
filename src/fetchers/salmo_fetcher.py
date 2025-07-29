import requests
from bs4 import BeautifulSoup

from fetchers import Fetcher


class SalmoFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://www.bibliaon.com/salmo_do_dia/"

    def _fetch_psalm_content(self):
        """Fetch psalm content using requests + BeautifulSoup."""
        try:
            soup = self._make_soup(self._url)

            # Try to find the psalm content using common selectors
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
                "title": "Erro ao carregar salmo",
                "content": f"Não foi possível buscar o salmo do dia: {str(e)}",
                "url": self._url,
            }

    def fetch(self, args=None):
        """Fetch daily psalm content."""
        return self._fetch_psalm_content()
