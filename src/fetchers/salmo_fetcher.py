import requests
from bs4 import BeautifulSoup

try:
    from .fetcher import Fetcher
except ImportError:
    from fetcher import Fetcher


class SalmoFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://www.bibliaon.com/salmo_do_dia/"

    def _fetch(self, soup):
        """Extract psalm content from soup following the pattern of SignFetcher."""
        try:
            # Try to find the psalm title
            psalm_title = "Salmo do Dia"
            title_selectors = [
                "h1", "h2", "h3", 
                ".title", ".psalm-title", ".salmo-title",
                ".page-title", ".entry-title", ".post-title"
            ]
            
            for selector in title_selectors:
                title_elements = soup.select(selector)
                if title_elements:
                    title_text = title_elements[0].get_text().strip()
                    if title_text and len(title_text) < 100 and "salmo" in title_text.lower():
                        psalm_title = title_text
                        break

            # Try to find the psalm content using multiple strategies
            psalm_content = None
            
            # Strategy 1: Look for common Portuguese religious website selectors
            content_selectors = [
                ".salmo", ".psalm", ".daily-psalm", ".salmo-do-dia", ".salmo_do_dia",
                ".bible-verse", ".verse", ".versiculo", ".texto-biblico",
                ".content-text", ".entry-content", ".post-content", 
                "article", ".content", ".main-content", ".texto",
                ".container p", ".row p", "main p"
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    text = elements[0].get_text().strip()
                    # Filter for reasonable psalm content length
                    if text and 50 < len(text) < 3000:
                        psalm_content = text
                        break
            
            # Strategy 2: Look for paragraphs that might contain psalm verses
            if not psalm_content:
                paragraphs = soup.find_all("p")
                potential_content = []
                
                for p in paragraphs:
                    text = p.get_text().strip()
                    # Look for Bible-like content (has verse-like characteristics)
                    if (text and len(text) > 30 and 
                        any(word in text.lower() for word in ["senhor", "deus", "ele", "tu", "vós"]) and
                        not any(word in text.lower() for word in ["cookies", "política", "privacidade", "menu", "navegação"])):
                        potential_content.append(text)
                
                if potential_content:
                    # Join the first few paragraphs that look like psalm content
                    psalm_content = "\n\n".join(potential_content[:3])
            
            # Strategy 3: Last resort - find the main content area and clean it
            if not psalm_content:
                # Remove unwanted elements
                for unwanted in soup(["nav", "header", "footer", "script", "style", "aside", "menu"]):
                    unwanted.decompose()
                
                # Look for content in main areas
                main_areas = soup.select("main, .main, #main, .container, .row")
                if main_areas:
                    main_text = main_areas[0].get_text().strip()
                    if main_text and 50 < len(main_text) < 5000:
                        psalm_content = main_text

            return {
                "title": psalm_title,
                "content": psalm_content or "Conteúdo não encontrado",
            }

        except Exception as e:
            return {
                "title": "Erro ao processar salmo",
                "content": f"Erro ao extrair conteúdo: {str(e)}",
            }

    def fetch(self, args=None):
        """Fetch daily psalm content following the pattern of SignFetcher."""
        try:
            soup = self._make_soup(self._url)
            data = self._fetch(soup)
            data["url"] = self._url
            return data
            
        except Exception as e:
            return {
                "title": "Erro ao carregar salmo",
                "content": f"Não foi possível buscar o salmo do dia: {str(e)}",
                "url": self._url,
            }
