import random
from datetime import datetime

from fetchers import TarotFetcher
from telegram import ParseMode
from telegram.ext import CommandHandler
from utils import get_date


class Tarot:

    def __init__(self):
        self._command = "tarot"
        self._users = {}  # TODO: make a class to handle users
        self._fetcher = TarotFetcher()

    def _build_message(self, data):
        image = data['card']['image']
        title = data['card']['title']
        prediction_body = data['card']['body']
        url = data['card']['url']

        # prepare heading
        heading = f"{data['date']} - Tarot do Dia de {data['display_name']}\n\n"  # noqa

        # fetch and present body info
        body = f'<a href="{image}">• </a>'  # TODO: this is a hack
        body += f"<b>{title.upper()}</b>\n\n"
        body += f"{prediction_body}\n\n"
        body += f"Mais informações e outras cartas em: {url}\n"

        # parse command characters
        message = str(heading + body)

        return message

    def _draw_card(self, user):
        request_date = user['request_date']
        card = user['card']

        # if request date is not today, reset
        today = str(datetime.now().date())
        if not card or not request_date or request_date != today:
            user['request_date'] = today

            index = random.randint(1, 23)
            data = self._fetcher.fetch(index)
            card = {
                "title": data['title'],
                "body": data['body'],
                "image": data['image'],
                "url": data['url'],
            }
            user['card'] = card

        return user['card']

    def _get_user(self, userid, display_name):
        if userid not in self._users:
            self._users[userid] = {
                "display_name": display_name,
                "request_date": None,
                "card": None,
            }

        return self._users[userid]

    def _process(self, update, context):
        # fetch user data
        userid = update.message.from_user.id
        display_name = update.message.from_user.username
        if not display_name:
            display_name = update.message.from_user.full_name
        user = self._get_user(userid, display_name)
        card = self._draw_card(user)

        # fetch card data
        data = {'display_name': display_name, 'card': card, 'date': get_date()}

        # build message
        message = self._build_message(data)

        # send message
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=message,
                                 parse_mode=ParseMode.HTML,
                                 disable_web_page_preview=False)

    def setup(self, dispatcher):
        inline_handler = CommandHandler(self._command, self._process)
        dispatcher.add_handler(inline_handler)
