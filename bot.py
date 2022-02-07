import logging

import difflib
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler, Updater

from fetcher import Fetcher
from environment import Environment

# load env
env = Environment()

# fetch updater and job queue
logging.info("Starting bot...")
updater = Updater(token=env.telegram_token, use_context=True)
dispatcher = updater.dispatcher

fetcher = Fetcher()

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
    "peixes": "Peixes"
}

NUMBER_OF_RESULTS = 3
CUTOFF = 0.2
DEFAULT_SIGN = "aries"


def prepare_message(message):
    return message.replace("-", "\-") \
              .replace(".", "\.") \
              .replace("(", "\(") \
              .replace(")", "\)") \
              .replace("!", "\!") # noqa


def parse_sign(sign):
    match = difflib.get_close_matches(sign,
                                      sign_map.keys(),
                                      n=NUMBER_OF_RESULTS,
                                      cutoff=CUTOFF)
    if len(match) == 0:
        return [DEFAULT_SIGN]

    return match


def make_prediction_message(data):
    # prepare heading
    sign = data['sign']
    heading = f"{data['date']} - {sign_map[sign]}\n\n"  # noqa
    working_text = "Processando..."
    message = prepare_message(str(heading + working_text))

    # fetch and present body info
    body = "```\n"
    body += f"{data['prediction']}\n\n"
    body += "```"
    body += f"Previsão completa em: {data['url']}\n"

    # parse command characters
    message = prepare_message(str(heading + body))

    return message


# set the function command callback for the daily
def bidu(update, context):
    query = update.inline_query.query

    if not query:
        return

    signs = parse_sign(query)
    results = []
    for sign in signs:
        data = fetcher.fetch(sign)
        message = make_prediction_message(data)
        description = data['prediction']

        results.append(
            InlineQueryResultArticle(
                id=sign.upper(),
                title=sign_map[sign],
                thumb_url=data['image'],
                description=description,
                input_message_content=InputTextMessageContent(message)))

    context.bot.answer_inline_query(update.inline_query.id, results)


inline_handler = InlineQueryHandler(bidu)
dispatcher.add_handler(inline_handler)

updater.start_polling()
logging.info("Bot started and listening for commands.")
