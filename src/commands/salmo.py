from telegram import ParseMode, ChatAction

from commands import Command
from modules import PredictionModule


class Salmo(Command):
    def __init__(self):
        super().__init__()
        self._command = "salmo"
        self._prediction_module = PredictionModule()

    def _make_psalm_message(self, data):
        title = data["title"]
        key_verse = data["key_verse"]
        url = data["url"]

        # prepare heading with date following the pattern of other commands
        heading = f"{data['date']} - {title}\n\n"

        # format body following the pattern of sign/tarot commands
        body = f"{key_verse}\n\n"
        body += f'🔗 <a href="{url}">Ver salmo completo</a>'

        # combine heading and body
        message = str(heading + body)

        return message

    def _process(self, update, context):
        """process the /salmo command"""
        telegram_message = super()._process(update, context)

        # send typing indicator while generating prediction
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        # fetch cached or generate new psalm prediction
        data = self._prediction_module.get_salmo_prediction()
        message = self._make_psalm_message(data)

        # edit the processing message with the result
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=telegram_message["message_id"],
            text=message,
            parse_mode=ParseMode.HTML,
        )
