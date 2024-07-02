import logging

from telegram import ParseMode
from telegram.ext import CommandHandler

from modules import Singleton


class Command(metaclass=Singleton):
    def __init__(self):
        # override in subclass
        self._command = None
        self._fetcher = None

    def _process(self, update, context):
        # override in subclass, call super()
        userid = update.message.from_user.id
        display_name = update.message.from_user.username
        text = update.message.text
        channel = update.message.chat.id
        if not display_name:
            display_name = update.message.from_user.full_name
        logging.info(
            f"command: {self._command} - "
            f"user: ({userid}) {display_name} - "
            f"channel: {channel} - "
            f"text: {text}"
        )
        return context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Processando comando...",
            parse_mode=ParseMode.HTML,
        )

    def setup(self, dispatcher):
        inline_handler = CommandHandler(self._command, self._process)
        dispatcher.add_handler(inline_handler)
