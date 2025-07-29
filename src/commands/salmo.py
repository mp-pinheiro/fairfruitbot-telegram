from telegram import ParseMode, ChatAction
from telegram.ext import CommandHandler
from utils import get_date

from commands import Command
from fetchers import SalmoFetcher
from clients import OpenAIClient


class Salmo(Command):
    def __init__(self):
        super().__init__()
        self._command = "salmo"
        self._fetcher = SalmoFetcher()
        self._client = OpenAIClient()

    def _extract_key_verse(self, psalm_content, psalm_title):
        """Use OpenAI to extract the most important verse from the psalm."""
        system_prompt = (
            "Você é um especialista em textos bíblicos e espiritualidade. Sua tarefa é identificar "
            "o versículo mais importante e impactante de um salmo completo. Escolha o versículo que "
            "melhor representa a essência e mensagem central do salmo. Responda apenas com o versículo "
            "escolhido, sem explicações adicionais."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": f"Do seguinte salmo '{psalm_title}', extraia o versículo mais importante:\n\n{psalm_content}"
            }
        ]
        
        return self._client.make_request(messages)

    def _make_psalm_message(self, data):
        """Format the psalm data into a Telegram message following the pattern of other commands."""
        title = data["title"]
        key_verse = data["key_verse"]
        url = data["url"]

        # Prepare heading with date following the pattern of other commands
        heading = f"{get_date()} - {title}\n\n"

        # Format body following the pattern of sign/tarot commands
        body = f"{key_verse}\n\n"
        body += f'<a href="{url}">🔗 Ver salmo completo</a>'

        # Combine heading and body
        message = str(heading + body)

        return message

    def _process(self, update, context):
        """Process the /salmo command."""
        super()._process(update, context)

        # Send typing indicator while fetching and processing
        context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )

        # Fetch psalm data
        psalm_data = self._fetcher.fetch()
        
        # Extract the most important verse using AI
        key_verse = self._extract_key_verse(psalm_data["content"], psalm_data["title"])
        psalm_data["key_verse"] = key_verse

        # Format message
        message = self._make_psalm_message(psalm_data)

        # Send response
        context.bot.send_message(
            chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML
        )

    def setup(self, dispatcher):
        """Setup the command handler."""
        inline_handler = CommandHandler(self._command, self._process)
        dispatcher.add_handler(inline_handler)
