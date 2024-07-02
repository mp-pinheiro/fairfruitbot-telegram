import difflib

from telegram import ParseMode

from commands import Command
from fetchers import SignFetcher
from utils import get_date


class Sign(Command):
    sign_map = {
        "aries": "Áries",
        "touro": "Touro",
        "gemeos": "Gêmeos",
        "cancer": "Câncer",
        "leao": "Leão",
        "virgem": "Virgem",
        "libra": "Libra",
        "escorpiao": "Escorpião",
        "sagitario": "Sagitário",
        "capricornio": "Capricórnio",
        "aquario": "Aquário",
        "peixes": "Peixes",
    }

    CUTOFF = 0.2
    DEFAULT_SIGN = "aries"

    def __init__(self):
        self._command = "bidu_old"
        self._fetcher = SignFetcher()

    # TODO: this is duplicated in `tarot.py`
    def _parse_sign(self, sign):
        match = difflib.get_close_matches(
            sign,
            Sign.sign_map.keys(),
            n=1,
            cutoff=Sign.CUTOFF,
        )
        if len(match) == 0:
            return Sign.DEFAULT_SIGN

        return match[0]

    def _make_prediction_message(self, data):
        sign = data["sign"]
        image = data["image"]
        prediction = data["prediction"]
        guess_of_the_day = data["guess_of_the_day"]
        color_of_the_day = data["color_of_the_day"]
        url = data["url"]

        # prepare heading
        heading = f"{data['date']} - Horóscopo de {Sign.sign_map[sign]}\n\n"  # noqa

        # fetch and present body info
        body = f'<a href="{image}">• </a>'  # TODO: this is a hack
        body += f"{prediction}\n\n"
        body += f'<a href="{image}">• </a>'
        body += f"<b>Palpite do dia:</b> {guess_of_the_day}\n"
        body += f'<a href="{image}">• </a>'
        body += f"<b>Cor do dia:</b> {color_of_the_day}\n"
        body += "\n"
        body += f"Mais informações em: {url}\n"

        # parse command characters
        message = str(heading + body)

        return message

    def _process(self, update, context):
        super()._process(update, context)

        args = context.args
        query = " ".join(args)

        sign = self._parse_sign(query)
        data = self._fetcher.fetch(sign)
        data["date"] = get_date()
        message = self._make_prediction_message(data)

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
        )
