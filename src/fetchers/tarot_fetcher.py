import json
from fetchers import Fetcher

tarot_map = {
    "o papa": "V",
    "o mago": "I",
    "a temperança": "XIV",
    "a força": "XI",
    "a lua": "XVIII",
    "a papisa": "II",
    "o eremita": "IX",
    "o mundo": "XXI",
    "o sol": "XIX",
    "o diabo": "XV",
    "a morte": "XIII",
    "o louco": "0",
    "o julgamento": "XX",
    "o hermita": "IX",
    "a justiça": "VIII",
    "a torre": "XVI",
    "a imperatriz": "III",
    "o imperador": "IV",
    "os enamorados": "VI",
    "o carro": "VII",
    "a estrela": "XVII",
    "a temperança": "XIV",
    "o enforcado": "XII",
    "o julgamento": "XX",
    "o mundo": "XXI",
    "o aeon": "XXI",
    "a roda da fortuna": "X",
}

category_map = {
    "0": "Fool",
    "I": "Magician",
    "II": "High Priestess",
    "III": "Empress",
    "IV": "Emperor",
    "V": "Hierophant",
    "VI": "Lovers",
    "VII": "Chariot",
    "VIII": "Justice",
    "IX": "Hermit",
    "X": "Wheel of Fortune",
    "XI": "Strength",
    "XII": "Hanged Man",
    "XIII": "Death",
    "XIV": "Temperance",
    "XV": "Devil",
    "XVI": "Tower",
    "XVII": "Star",
    "XVIII": "Moon",
    "XIX": "Sun",
    "XX": "Judgement",
    "XXI": "World",
}

image_map = {
    "Fool": "https://static.wikia.nocookie.net/megamitensei/images/5/53/Fool-0.png/revision/latest/scale-to-width-down/130?cb=20160404201043",  # noqa
    "Magician": "https://static.wikia.nocookie.net/megamitensei/images/c/cb/Magician-0.png/revision/latest/scale-to-width-down/130?cb=20160404201629",  # noqa
    "Priestess": "https://static.wikia.nocookie.net/megamitensei/images/a/ad/Priestess-0.png/revision/latest/scale-to-width-down/130?cb=20160404201724",  # noqa
    "Empress": "https://static.wikia.nocookie.net/megamitensei/images/6/63/Empress-0.png/revision/latest/scale-to-width-down/130?cb=20160404201807",  # noqa
    "Emperor": "https://static.wikia.nocookie.net/megamitensei/images/e/e6/Emperor-0.png/revision/latest/scale-to-width-down/130?cb=20160404201848",  # noqa
    "Hierophant": "https://static.wikia.nocookie.net/megamitensei/images/f/f6/Hierophant-0.png/revision/latest/scale-to-width-down/130?cb=20160404201947",  # noqa
    "Lovers": "https://static.wikia.nocookie.net/megamitensei/images/a/a5/Lovers-0.png/revision/latest/scale-to-width-down/130?cb=20160404202019",  # noqa
    "Chariot": "https://static.wikia.nocookie.net/megamitensei/images/1/15/Chariot-0.png/revision/latest/scale-to-width-down/130?cb=20160404202048",  # noqa
    "Justice": "https://static.wikia.nocookie.net/megamitensei/images/8/83/Justice-0.png/revision/latest/scale-to-width-down/130?cb=20160404202153",  # noqa
    "Hermit": "https://static.wikia.nocookie.net/megamitensei/images/a/ab/Hermit-0.png/revision/latest/scale-to-width-down/130?cb=20160404202218",  # noqa
    "Fortune": "https://static.wikia.nocookie.net/megamitensei/images/f/f3/Fortune-0.png/revision/latest/scale-to-width-down/130?cb=20160404202245",  # noqa
    "Strength": "https://static.wikia.nocookie.net/megamitensei/images/b/b0/Strength-0.png/revision/latest/scale-to-width-down/130?cb=20160404202121",  # noqa
    "Hanged_Man": "https://static.wikia.nocookie.net/megamitensei/images/2/2f/Hanged_Man.png/revision/latest/scale-to-width-down/130?cb=20160404202318",  # noqa
    "Death": "https://static.wikia.nocookie.net/megamitensei/images/d/df/Death-0.png/revision/latest/scale-to-width-down/130?cb=20160404202413",  # noqa
    "Temperance": "https://static.wikia.nocookie.net/megamitensei/images/2/2d/Temperance-0.png/revision/latest/scale-to-width-down/130?cb=20160404202449",  # noqa
    "Devil": "https://static.wikia.nocookie.net/megamitensei/images/4/4b/Devil-0.png/revision/latest/scale-to-width-down/130?cb=20160404202521",  # noqa
    "Tower": "https://static.wikia.nocookie.net/megamitensei/images/1/1f/Tower-0.png/revision/latest/scale-to-width-down/130?cb=20160404202557",  # noqa
    "Star": "https://static.wikia.nocookie.net/megamitensei/images/1/15/Star-0.png/revision/latest/scale-to-width-down/130?cb=20160404202628",  # noqa
    "Moon": "https://static.wikia.nocookie.net/megamitensei/images/c/ce/Moon-0.png/revision/latest/scale-to-width-down/130?cb=20160404202708",  # noqa
    "Sun": "https://static.wikia.nocookie.net/megamitensei/images/f/ff/Sun-0.png/revision/latest/scale-to-width-down/130?cb=20160404202738",  # noqa
    "Judgement": "https://static.wikia.nocookie.net/megamitensei/images/b/b0/Judgement.png/revision/latest/scale-to-width-down/130?cb=20160404202809",  # noqa
    "World": "https://static.wikia.nocookie.net/megamitensei/images/a/a9/World-0.png/revision/latest/scale-to-width-down/130?cb=20160404202908",  # noqa
}


class TarotFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://joaobidu.com.br/oraculos/tarot-online/carta-{card}/"  # noqa
        self._persona_card_url = "https://static.wikia.nocookie.net/megamitensei/images/5/53/Fool-0.png/revision/latest?cb=20160404201043"  # noqa

        # load persona data
        with open("data/arcanas.json", "r") as f:
            self._arcanas = json.load(f)

    def _fetch(self, soup):
        parent = soup.find("div", class_="textoResultado")
        texts = parent.find("p")

        # fetch title
        title = parent.find("b").string
        category = tarot_map[title.lower().strip()]
        arcana_name = category_map[category]
        title = f"{title} ({arcana_name})"

        # fetch body
        body = ""
        for text in texts:
            if text.string and text.string != "\n":
                body += text.string
        body = body.replace("\n", "").strip()

        # fetch persona info
        arcanas = self._arcanas[category].values()

        # fetch image
        image = image_map[arcana_name]

        return {
            "title": title,
            "body": body,
            "image": image,
            "arcanas": arcanas,
        }

    def fetch(self, card):
        url = self._url.format(card=card)
        soup = self._make_soup(url)

        prediction = self._fetch(soup)
        clean_url = url.split("resultado")[0]  # send to tarot home page

        return {
            "title": prediction["title"],
            "body": prediction["body"],
            "image": prediction["image"],
            "arcanas": prediction["arcanas"],
            "url": clean_url,
        }
