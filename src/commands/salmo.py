from fetchers.salmo_fetcher import SalmoFetcher
from telegram import ParseMode
from telegram.ext import CommandHandler
from utils import get_date

from commands import Command


class Salmo(Command):
    def __init__(self):
        super().__init__()
        self._command = "salmo"
        self._fetcher = SalmoFetcher()

    def _make_psalm_message(self, data):
        """Format the psalm data into a Telegram message."""
        title = data["title"]
        content = data["content"]
        url = data["url"]

        # Prepare heading with date
        heading = f"{get_date()} - <b>{title}</b>\n\n"

        # Format content - limit length for Telegram
        max_content_length = 3000  # Leave room for title and footer
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."

        # Build message body
        body = f"{content}\n\n"
        body += f'<a href="{url}">🔗 Ver salmo completo</a>'

        # Combine heading and body
        message = str(heading + body)

        return message

    def _process(self, update, context):
        """Process the /salmo command."""
        super()._process(update, context)

        # Show typing indicator
        self._send_typing_action(context, update.message.chat_id)

        # Fetch psalm data
        data = self._fetcher.fetch()

        # Format message
        message = self._make_psalm_message(data)

        # Send response
        context.bot.send_message(
            chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML
        )

    def setup(self, dispatcher):
        """Setup the command handler."""
        inline_handler = CommandHandler(self._command, self._process)
        dispatcher.add_handler(inline_handler)
