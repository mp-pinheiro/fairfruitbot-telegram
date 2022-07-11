from fetchers import Fetcher


class SignFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://joaobidu.com.br/horoscopo/signos/previsao-{sign}"  # noqa
        self._image_url = "https://joaobidu.com.br/static/img/ico-{sign}.png"  # noqa

    def _fetch(self, soup):
        parent = soup.find('div', class_='theiaPostSlider_preloadedSlide')

        # fetch basic info
        prediction = ''
        elements = parent.find('div', class_='zoxrel left').children
        for element in elements:
            # if element is <br>, add newline
            if element.name == 'br':
                prediction += '\n'
            elif element.string:
                prediction += element.string.strip()

        # fetch guess and color of the day
        guess_of_the_day = ''
        color_of_the_day = ''
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
        elements = parent.find('ul')

        return {
            'prediction': prediction,
            'guess_of_the_day': guess_of_the_day,
            'color_of_the_day': color_of_the_day,
        }

    def fetch(self, sign):
        url = self._url.format(sign=sign)
        soup = self._make_soup(url)

        data = self._fetch(soup)
        data['sign'] = sign
        data['image'] = self._image_url.format(sign=sign)
        data['url'] = url

        return data
