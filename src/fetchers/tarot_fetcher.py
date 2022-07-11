from fetchers import Fetcher


class TarotFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://joaobidu.com.br/oraculos/taro-resultado.php?carta={card}"  # noqa

    def _fetch(self, soup):
        parent = soup.find('div', class_='textoResultado')
        texts = parent.find('p')

        # fetch title
        title = parent.find('b').string

        # fetch body
        body = ''
        for text in texts:
            if text.string and text.string != '\n':
                body += text.string
        body = body.replace('\n', '').strip()

        # fetch image
        parent = soup.find('div', class_='taroResultado')
        relative = parent.find('img')['src']
        image = self._base_url + relative

        return {'title': title, 'body': body, 'image': image}

    def fetch(self, card):
        url = self._url.format(card=card)
        soup = self._make_soup(url)

        prediction = self._fetch(soup)
        clean_url = url.split('resultado')[0]  # send to tarot home page

        return {
            'title': prediction['title'],
            'body': prediction['body'],
            'image': prediction['image'],
            'url': clean_url
        }
