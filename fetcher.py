import requests

from datetime import datetime

from bs4 import BeautifulSoup


class Fetcher:
    def __init__(self):
        self._url = "https://joaobidu.com.br/horoscopo/signos/previsao-{sign}"
        self._image_url = "https://joaobidu.com.br/static/img/ico-{sign}.png"

    def _make_soup(self, sign):
        url = self._url.format(sign=sign)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup

    def _fetch_prediction(self, soup):
        parent = soup.find('div', class_='texto')
        texts = parent.find('p')

        prediction = ''
        for text in texts:
            if text.string and text.string != '\n':
                prediction += text.string

        prediction = prediction.replace('\n', '')

        return prediction

    def fetch(self, sign):
        soup = self._make_soup(sign)

        prediction = self._fetch_prediction(soup)
        date = datetime.now().strftime('%d/%m/%Y')
        image = self._image_url.format(sign=sign)
        url = self._url.format(sign=sign)

        return {
            'sign': sign,
            'image': image,
            'prediction': prediction,
            'date': date,
            'url': url
        }
