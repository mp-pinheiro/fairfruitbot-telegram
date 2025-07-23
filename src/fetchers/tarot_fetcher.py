import json
from fetchers import Fetcher


class TarotFetcher(Fetcher):
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
        "II": "Priestess",
        "III": "Empress",
        "IV": "Emperor",
        "V": "Hierophant",
        "VI": "Lovers",
        "VII": "Chariot",
        "VIII": "Justice",
        "IX": "Hermit",
        "X": "Fortune",
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
    arcana_map = {
        "Fool": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/5/53/Fool-0.png/revision/latest/scale-to-width-down/130?cb=20160404201043",  # noqa
            "description": "O Louco representa novos começos, espontaneidade e inocência. Eles são frequentemente vistos como despreocupados e aventureiros, mas também podem ser ingênuos e propensos a cometer erros.",  # noqa
        },
        "Magician": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/c/cb/Magician-0.png/revision/latest/scale-to-width-down/130?cb=20160404201629",  # noqa
            "description": "O Mago é um mestre em sua arte, usando suas habilidades e conhecimento para manifestar seus desejos. Eles são versáteis e engenhosos, mas também podem ser manipuladores e enganosos.",  # noqa
        },
        "Priestess": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/a/ad/Priestess-0.png/revision/latest/scale-to-width-down/130?cb=20160404201724",  # noqa
            "description": "A Sacerdotisa é uma guardiã de segredos e mistérios, representando intuição e conhecimento oculto. Elas são frequentemente vistas como sábias e intuitivas, mas também podem ser secretas e distantes.",  # noqa
        },
        "Empress": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/6/63/Empress-0.png/revision/latest/scale-to-width-down/130?cb=20160404201807",  # noqa
            "description": "A Imperatriz personifica a nutrição e a abundância, representando fertilidade e criação. Ela é frequentemente vista como carinhosa e solidária, mas também pode ser possessiva e controladora.",  # noqa
        },
        "Emperor": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/e/e6/Emperor-0.png/revision/latest/scale-to-width-down/130?cb=20160404201848",  # noqa
            "description": "O Imperador representa autoridade e estrutura, personificando liderança e estabilidade. Ele é frequentemente visto como disciplinado e responsável, mas também pode ser rígido e dominador.",  # noqa
        },
        "Hierophant": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/f/f6/Hierophant-0.png/revision/latest/scale-to-width-down/130?cb=20160404201947",  # noqa
            "description": "O Papa representa a tradição e a conformidade, personificando religião e espiritualidade. Ele é frequentemente visto como sábio e conhecedor, mas também pode ser dogmático e inflexível.",  # noqa
        },
        "Lovers": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/a/a5/Lovers-0.png/revision/latest/scale-to-width-down/130?cb=20160404202019",  # noqa
            "description": "Os Enamorados representam escolha e parceria, personificando amor e paixão. Eles são frequentemente vistos como apaixonados e românticos, mas também podem ser indecisos e propensos a conflitos.",  # noqa
        },
        "Chariot": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/1/15/Chariot-0.png/revision/latest/scale-to-width-down/130?cb=20160404202048",  # noqa
            "description": "O Carro representa força de vontade e determinação, personificando vitória e sucesso. Ele é frequentemente visto como motivado e ambicioso, mas também pode ser competitivo e agressivo.",  # noqa
        },
        "Justice": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/8/83/Justice-0.png/revision/latest/scale-to-width-down/130?cb=20160404202153",  # noqa
            "description": "A Justiça representa equilíbrio e justiça, personificando lei e ordem. Ela é frequentemente vista como objetiva e imparcial, mas também pode ser julgadora e inflexível.",  # noqa
        },
        "Hermit": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/a/ab/Hermit-0.png/revision/latest/scale-to-width-down/130?cb=20160404202218",  # noqa
            "description": "O Eremita representa introspecção e solidão, personificando sabedoria e autodescoberta. Ele é frequentemente visto como perspicaz e reflexivo, mas também pode ser recluso e isolado.",  # noqa
        },
        "Fortune": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/f/f3/Fortune-0.png/revision/latest/scale-to-width-down/130?cb=20160404202245",  # noqa
            "description": "A Fortuna representa sorte e destino, personificando mudança e incerteza. Ela é frequentemente vista como aventureira e imprevisível, mas também pode ser impulsiva e imprudente.",  # noqa
        },
        "Strength": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/b/b0/Strength-0.png/revision/latest/scale-to-width-down/130?cb=20160404202121",  # noqa
            "description": "A Força representa coragem e resiliência, personificando força interior e determinação. Ela é frequentemente vista como poderosa e destemida, mas também pode ser teimosa e dominadora.",  # noqa
        },
        "Hanged Man": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/2/2f/Hanged_Man.png/revision/latest/scale-to-width-down/130?cb=20160404202318",  # noqa
            "description": "O Enforcado representa sacrifício e entrega, personificando altruísmo e iluminação. Ele é frequentemente visto como não convencional e espiritual, mas também pode ser passivo e indeciso.",  # noqa
        },
        "Death": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/d/df/Death-0.png/revision/latest/scale-to-width-down/130?cb=20160404202413",  # noqa
            "description": "A Morte representa transformação e renovação, personificando o fim e novos começos. Ela é frequentemente vista como transformadora e libertadora, mas também pode ser assustadora e intimidante.",  # noqa
        },
        "Temperance": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/2/2d/Temperance-0.png/revision/latest/scale-to-width-down/130?cb=20160404202449",  # noqa
            "description": "A Temperança representa equilíbrio e harmonia, personificando moderação e autocontrole. Ela é frequentemente vista como paciente e harmoniosa, mas também pode ser indecisa e passiva.",  # noqa
        },
        "Devil": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/4/4b/Devil-0.png/revision/latest/scale-to-width-down/130?cb=20160404202521",  # noqa
            "description": "O Diabo representa tentação e materialismo, personificando prazeres e desejos mundanos. Ele é frequentemente visto como sedutor e atraente, mas também pode ser manipulador e egoísta.",  # noqa
        },
        "Tower": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/1/1f/Tower-0.png/revision/latest/scale-to-width-down/130?cb=20160404202557",  # noqa
            "description": "A Torre representa o caos e a agitação, personificando destruição e mudança. Ela é frequentemente vista como catastrófica e destrutiva, mas também pode ser transformadora e libertadora.",  # noqa
        },
        "Star": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/1/15/Star-0.png/revision/latest/scale-to-width-down/130?cb=20160404202628",  # noqa
            "description": "A Estrela representa esperança e inspiração, personificando positividade e otimismo. Ela é frequentemente vista como radiante e inspiradora, trazendo calor e luz para aqueles ao seu redor.",  # noqa
        },
        "Moon": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/c/ce/Moon-0.png/revision/latest/scale-to-width-down/130?cb=20160404202708",  # noqa
            "description": "A Lua representa intuição e ilusão, personificando mistério e subconsciência. Ela é frequentemente vista como elusiva e enigmática, mas também pode ser confusa e perturbadora.",  # noqa
        },
        "Sun": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/f/ff/Sun-0.png/revision/latest/scale-to-width-down/130?cb=20160404202738",  # noqa
            "description": "O Sol representa vitalidade e iluminação, personificando alegria e sucesso. Ele é frequentemente visto como positivo e radiante, trazendo calor e luz para aqueles ao seu redor.",  # noqa
        },
        "Judgement": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/b/b0/Judgement.png/revision/latest/scale-to-width-down/130?cb=20160404202809",  # noqa
            "description": "O Julgamento representa renascimento e renovação, personificando julgamento e despertar. Ele é frequentemente visto como um chamado à ação ou um toque de despertar, fazendo com que alguém assuma a responsabilidade por suas ações e siga em frente com clareza e propósito.",  # noqa
        },
        "World": {
            "url": "https://static.wikia.nocookie.net/megamitensei/images/a/a9/World-0.png/revision/latest/scale-to-width-down/130?cb=20160404202908",  # noqa
            "description": "O Mundo representa realização e cumprimento, personificando realização e conquista. Ele é frequentemente visto como um símbolo de sucesso e realização, representando uma sensação de completude e unidade com o universo.",  # noqa
        },
    }

    def __init__(self):
        super().__init__()
        self._url = (
            "https://joaobidu.com.br/oraculos/tarot-online/carta-{card}/"  # noqa
        )
        self._wiki_url = "https://megamitensei.fandom.com/wiki/{arcana}_Arcana"

        # load persona data
        with open("data/arcanas.json", "r") as f:
            self._arcanas = json.load(f)

    def _make(self, arcana):
        # find category in category map values
        category = next(
            key for key, value in TarotFetcher.category_map.items() if value == arcana
        )

        # fetch title
        title = arcana.upper()

        # fetch body
        body = TarotFetcher.arcana_map[arcana]["description"]

        # fetch persona info
        arcanas = self._arcanas[category].values()

        # fetch image
        image = TarotFetcher.arcana_map[arcana]["url"]

        return {
            "title": title,
            "body": body,
            "image": image,
            "arcanas": arcanas,
        }

    def _fetch(self, soup):
        parent = soup.find("div", class_="textoResultado")
        texts = parent.find("p")

        # fetch title
        title = parent.find("b").string.strip()
        category = TarotFetcher.tarot_map[title.lower().strip()]
        arcana_name = TarotFetcher.category_map[category]
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
        image = TarotFetcher.arcana_map[arcana_name]["url"]

        return {
            "title": title,
            "body": body,
            "image": image,
            "arcanas": arcanas,
        }

    def make(self, arcana):
        """Unlike `fetch`, will not fetch a prediction for the card.
        Only persona info will be returned.
        """
        prediction = self._make(arcana)
        formatted_arcana = arcana.replace(" ", "_")
        url = self._wiki_url.format(arcana=formatted_arcana)

        return {
            "title": prediction["title"],
            "body": prediction["body"],
            "image": prediction["image"],
            "arcanas": prediction["arcanas"],
            "url": url,
        }

    def fetch(self, card):
        url = self._url.format(card=card)
        soup = self._make_soup(url)
        prediction = self._fetch(soup)
        clean_url = "/".join(self._url.split("/")[:-2])

        return {
            "title": prediction["title"],
            "body": prediction["body"],
            "image": prediction["image"],
            "arcanas": prediction["arcanas"],
            "url": clean_url,
        }
