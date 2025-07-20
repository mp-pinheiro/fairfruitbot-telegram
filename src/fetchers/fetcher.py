import requests
from bs4 import BeautifulSoup


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
