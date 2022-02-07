import logging

import difflib
import telegram.ext
from telegram.ext import CommandHandler, Updater

from fetcher import Fetcher
from environment import Environment

# load env
env = Environment()

# fetch updater and job queue
logging.info("Starting bot...")
updater = Updater(token=env.telegram_token, use_context=True)
dispatcher = updater.dispatcher

fetcher = Fetcher()


def prepare_message(msg):
    return msg.replace("-", "\-") \
              .replace(".", "\.") \
              .replace("(", "\(") \
              .replace(")", "\)") \
              .replace("!", "\!") # noqa


signs = {
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
    "peixes": "Peixes"
}


def parse_sign(sign):
    match = difflib.get_close_matches(sign, signs.keys(), n=1)
    if len(match) == 0:
        return 'aries'

    return match[0]


# set the function command callback for the daily
def bidu(update, context):
    # prepare heading
    input = context.args[0] if len(context.args) > 0 else "aries"
    sign = parse_sign(input)
    data = fetcher.fetch(sign)

    heading = f"{data['date']} - {signs[sign]}\n\n"  # noqa
    working_text = "Processando..."
    msg = prepare_message(str(heading + working_text))

    # send message to show api is working
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2)

    # fetch and present body info
    body = "```\n"
    body += f"{data['prediction']}\n\n"
    body += "```"
    body += f"Previsão completa em: {data['url']}\n"

    # parse command characters
    msg = prepare_message(str(heading + body))

    # edit message with daily contents
    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                  message_id=message["message_id"],
                                  text=msg,
                                  parse_mode=telegram.ParseMode.MARKDOWN_V2)


handler = CommandHandler("bidu", bidu)
dispatcher.add_handler(handler)

updater.start_polling()
logging.info("Bot started and listening for commands.")
