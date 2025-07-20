from telegram import ParseMode

from commands import Sign
from modules import PredictionModule


class SignGPT(Sign):
    def __init__(self):
        super().__init__()
        self._command = "bidu"
        self._prediction_module = PredictionModule()

    def _make_prediction_message(self, data):
        sign = data["sign"]
        image = data["image"]
        prediction = data["prediction"]
        guess_of_the_day = data["guess_of_the_day"]
        color_of_the_day = data["color_of_the_day"]

        # prepare heading
        heading = f"{data['date']} - Horóscopo de {Sign.sign_map[sign]}\n\n"  # noqa

        # fetch and present body info
        body = f'<a href="{image}">• </a>'
        body += f"{prediction}\n\n"
        body += f'<a href="{image}">• </a>'
        body += f"<b>Palpite do dia:</b> {guess_of_the_day}\n"
        body += f'<a href="{image}">• </a>'
        body += f"<b>Cor do dia:</b> {color_of_the_day}\n\n"

        body += "Predição gerada por Bidu-GPT.\n\n"

        # parse command characters
        message = str(heading + body)

        return message

    def _fetch(self, sign):
        return self._prediction_module.get_sign_prediction(sign)

    def _process(self, update, context):
        telegram_message = super(Sign, self)._process(update, context)

        args = context.args
        query = " ".join(args)
        sign = self._parse_sign(query)

        data = self._fetch(sign)
        message = self._make_prediction_message(data)

        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=telegram_message["message_id"],
            text=message,
            parse_mode=ParseMode.HTML,
        )
