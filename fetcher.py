import requests

from datetime import datetime

from bs4 import BeautifulSoup


class Fetcher:
    def __init__(self):
        self._url = "https://joaobidu.com.br/horoscopo/signos/previsao-{sign}"

    def _make_soup(self, sign):
        url = self._url.format(sign=sign)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup

    def _fetch_image(self, soup):
        parent = soup.find('figure', class_='imgDestaque')
        img_src = parent.find('img').get('src')

        return img_src

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

        image = self._fetch_image(soup)
        prediction = self._fetch_prediction(soup)
        date = datetime.now().strftime('%d/%m/%Y')
        url = self._url.format(sign=sign)

        return {
            'sign': sign,
            'image': image,
            'prediction': prediction,
            'date': date,
            'url': url
        }
