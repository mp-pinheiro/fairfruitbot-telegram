import requests

from bs4 import BeautifulSoup


class Fetcher:

    def __init__(self):
        self._base_bidu_url = "https://joaobidu.com.br"  # noqa
        self._sign_url = "https://joaobidu.com.br/horoscopo/signos/previsao-{sign}"  # noqa
        self._sign_image_url = "https://joaobidu.com.br/static/img/ico-{sign}.png"  # noqa
        self._tarot_url = "https://joaobidu.com.br/oraculos/taro/resultado?carta={card}"  # noqa

    def _make_soup(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup

    def _fetch_sign_prediction(self, soup):
        parent = soup.find('div', class_='texto')

        # fetch basic info
        elements = parent.find('p', style='text-align: justify')
        prediction = ''
        guess_of_the_day = ''
        color_of_the_day = ''
        for element in elements:
            # if element is <br>, add newline
            if element.name == 'br':
                prediction += '\n'
            elif element.string:
                prediction += element.string.strip()

        # fetch guess and color of the day
        elements = soup.find_all('p')
        for element in elements:
            text = element.get_text().lower().strip()
            if 'palplite do dia:' in text or 'cor do dia:' in text:
                split = text.split('cor do dia:')
                guess_of_the_day = split[0].replace('palpite do dia:',
                                                    '').strip()  # noqa
                color_of_the_day = split[1].replace('cor do dia:',
                                                    '').strip()  # noqa

        # fetch more info
        elements = parent.find('section', id='mais-sobre-signos').find('ul')
        more_info = []
        for li in elements.find_all('li'):
            # split li into key and value
            key, value = li.get_text().split(': ')

            # add to more info
            more_info.append({'key': key, 'value': value})
        return {
            'prediction': prediction,
            'guess_of_the_day': guess_of_the_day,
            'color_of_the_day': color_of_the_day,
            'more_info': more_info
        }

    def fetch_sign_prediction(self, sign):
        url = self._sign_url.format(sign=sign)
        soup = self._make_soup(url)

        data = self._fetch_sign_prediction(soup)
        data['sign'] = sign
        data['image'] = self._sign_image_url.format(sign=sign)
        data['url'] = url

        return data

    def _fetch_tarot_prediction(self, soup):
        parent = soup.find('div', class_='textoResultado')
        texts = parent.find('p')

        # fetch title
        title = parent.find('b').string

        # fetch body
        body = ''
        for text in texts:
            if text.string and text.string != '\n':
                body += text.string
        body = body.replace('\n', '')

        # fetch image
        parent = soup.find('div', class_='taroResultado')
        relative = parent.find('img')['src']
        image = self._base_bidu_url + relative

        return {'title': title, 'body': body, 'image': image}

    def fetch_tarot_prediction(self, card):
        url = self._tarot_url.format(card=card)
        soup = self._make_soup(url)

        prediction = self._fetch_tarot_prediction(soup)
        clean_url = url.split('?')[0]  # remove query from url

        return {
            'title': prediction['title'],
            'body': prediction['body'],
            'image': prediction['image'],
            'url': clean_url
        }
