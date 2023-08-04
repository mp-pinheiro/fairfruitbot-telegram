from fetchers import Fetcher


class SignFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://joaobidu.com.br/horoscopo/signos/previsao-{sign}"  # noqa
        self._image_url = "https://joaobidu.com.br/static/img/ico-{sign}.png"  # noqa

    def _fetch(self, soup):
        parent = soup.find("div", class_="theiaPostSlider_preloadedSlide")

        # fetch basic info
        elements = parent.find("div", class_="zoxrel left").find("p")
        prediction = elements.get_text().strip()

        # fetch guess and color of the day
        guess_of_the_day = ""
        color_of_the_day = ""
        elements = soup.find_all("p")
        for element in elements:
            text = element.get_text().lower().strip()
            if "palplite do dia:" in text or "cor do dia:" in text:
                split = text.split("cor do dia:")
                guess_of_the_day = (
                    split[0].replace("palpite do dia:", "").strip()
                )  # noqa
                color_of_the_day = split[1].replace("cor do dia:", "").strip()  # noqa

        return {
            "prediction": prediction,
            "guess_of_the_day": guess_of_the_day,
            "color_of_the_day": color_of_the_day,
        }

    def fetch(self, sign):
        url = self._url.format(sign=sign)
        soup = self._make_soup(url)

        data = self._fetch(soup)
        data["sign"] = sign
        data["image"] = self._image_url.format(sign=sign)
        data["url"] = url

        return data
