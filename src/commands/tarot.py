import difflib
import random
from datetime import datetime

from telegram import ParseMode, ChatAction

from commands import Command
from fetchers import TarotFetcher
from utils import get_date


class Tarot(Command):
    CUTOFF = 0.2

    def __init__(self):
        super().__init__()
        self._command = "tarot_old"
        self._users = {}
        self._fetcher = TarotFetcher()

    def _parse_arcana(self, arcana):
        match = difflib.get_close_matches(
            arcana,
            TarotFetcher.category_map.values(),
            n=1,
            cutoff=Tarot.CUTOFF,
        )
        if len(match) == 0:
            return None

        return match[0]

    def _build_message(self, data):
        image = data["card"]["image"]
        title = data["card"]["title"]
        prediction_body = data["card"]["body"]
        url = data["card"]["url"]
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

        body += f"Mais informações em: {url}\n"

        # parse command characters
        message = str(heading + body)

        return message

    def _make_card(self, arcana):
        """Unlike `_draw_card`, this function will fabricate a card
        with only the arcana information, no prediction. It is used
        when the user requests a specific arcana.
        """
        data = self._fetcher.make(arcana)
        card = {
            "title": data["title"],
            "body": data["body"],
            "image": data["image"],
            "url": data["url"],
            "arcanas": data["arcanas"],
            "type": "info",
        }

        return card

    def _fetch_data(self):
        index = random.randint(1, 22)
        return self._fetcher.fetch(index)

    def _draw_card(self, user):
        request_date = user.get("request_date", None)
        card = user["card"]

        # if request date is not today, reset
        today = str(datetime.now().date())
        if not request_date or request_date != today:
            user["request_date"] = today
            oldcard = card

            while oldcard == card:
                data = self._fetch_data()
                card = {
                    "title": data.get("title"),
                    "body": data.get("body"),
                    "image": data.get("image"),
                    "url": data.get("url"),
                    "arcanas": data.get("arcanas"),
                    "type": "daily",
                }
                user["card"] = card

        return user["card"]

    def _get_user(self, userid, display_name):
        if userid not in self._users:
            self._users[userid] = {
                "display_name": display_name,
                "request_date": None,
                "card": None,
            }

        return self._users[userid]

    def _process(self, update, context):
        telegram_message = super()._process(update, context)

        # send typing indicator for longer processing commands
        context.bot.send_chat_action(
            chat_id=update.message.chat_id, action=ChatAction.TYPING
        )

        # fetch user data
        userid = update.message.from_user.id
        display_name = update.message.from_user.username
        if not display_name:
            display_name = update.message.from_user.full_name

        # determine command type (daily or info)
        args = context.args
        if len(args) > 0:
            # if more than one argument, assume info
            query = " ".join(args)
            arcana = self._parse_arcana(query)
            card = self._make_card(arcana)
        else:
            user = self._get_user(userid, display_name)
            arcana = None
            card = self._draw_card(user)

        # fetch card data
        data = {
            "display_name": display_name,
            "card": card,
            "arcana": arcana,
            "date": get_date(),
        }

        # build message
        message = self._build_message(data)

        # send message
        context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            message_id=telegram_message["message_id"],
            disable_web_page_preview=False,
        )
