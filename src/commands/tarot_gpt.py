import random

from telegram import ChatAction
from commands import Tarot
from fetchers import TarotFetcher
from modules import PredictionModule, UsersModule


class TarotGPT(Tarot):
    def __init__(self):
        super().__init__()
        self._command = "tarot"
        self._prediction_module = PredictionModule()
        self._users_module = UsersModule()

    def _build_message(self, data):
        image = data["card"]["image"]
        title = data["card"]["title"]
        prediction_body = data["card"]["body"]
        tarot_type = data["card"]["type"]

        # prepare heading
        if tarot_type == "daily":
            heading = (
                f"{data['date']} - Tarot do Dia de {data['display_name']}\n\n"  # noqa
            )
        elif tarot_type == "info":
            heading = f"{data['date']} - Info de Tarot para {data['display_name']}\n\n"  # noqa

        # fetch and present body info
        body = f'<a href="{image}">•  </a>'
        body += f"<b>{title.upper()}</b>\n\n"
        body += f"{prediction_body}\n\n"

        # fetch and present arcanas info
        arcanas = data["card"]["arcanas"]
        body += f'<a href="{image}">•  </a>'
        body += "<b>PERSONA</b>\n\n"
        for arcana in arcanas:
            entry = f"<a href='{arcana['url']}'>  • {arcana['name']}</a>"
            body += f"\t{entry}\n"
            for character in arcana["characters"]:
                entry = f"<a href='{character['url']}'>   • {character['name']} ({character['game']})</a>"  # noqa
                body += f"\t\t{entry}\n"
        body += "\n"

        body += "Predição gerada por Bidu-GPT.\n\n"

        return heading + body

    def _fetch_data(self):
        index = random.randint(1, 22)
        arcana = list(TarotFetcher.tarot_map.keys())[index]
        return self._prediction_module.get_tarot_prediction(arcana)

    def _get_user(self, userid, display_name):
        user = self._users_module.get_user(userid)
        if not user:
            self._users_module.add_user(userid, display_name)
            user = self._users_module.get_user(userid)
        return user
