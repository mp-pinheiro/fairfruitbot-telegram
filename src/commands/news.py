from fetchers import NewsFetcher
from telegram import ParseMode
from telegram.ext import CommandHandler
from utils import get_date

from commands import Command


class News(Command):

    def __init__(self):
        super().__init__()
        self._command = "news"
        self._fetcher = NewsFetcher()

    def _make_prediction_message(self, data):
        url = data["url"]
        title = data["title"]
        summary = data["summary"]

        # prepare heading
        heading = f"{data['date']} - <b>{title}</b>\n\n"  # noqa

        # fetch and present body info
        body = f"{summary}\n\n"
        body += f"<a href=\"{url}\">Leia mais...</a>"

        # parse command characters
        message = str(heading + body)

        return message

    def _process(self, update, context):
        super()._process(update, context)

        data = self._fetcher.fetch()
        data["date"] = get_date()
        message = self._make_prediction_message(data)

        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)

    def setup(self, dispatcher):
        inline_handler = CommandHandler(self._command, self._process)
        dispatcher.add_handler(inline_handler)
