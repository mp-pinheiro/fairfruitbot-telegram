import logging
import re
import traceback

from telegram.ext import Updater

from commands import Sign, Tarot, SignGPT, TarotGPT, GroupSummary
from environment import Environment

# load env
env = Environment()

# load commands
commands = [Sign(), Tarot(), SignGPT(), TarotGPT()]

# load message handlers (non-command handlers)
message_handlers = [GroupSummary()]

# fetch updater and job queue
logging.info("Starting bot...")
updater = Updater(token=env.telegram_token, use_context=True)
dispatcher = updater.dispatcher

# setup commands
for command in commands:
    command.setup(dispatcher)

# setup message handlers
for handler in message_handlers:
    handler.setup(dispatcher)


def prepare_message(msg, hard_parse=False):
    if hard_parse:
        # hard parse is used for error messages
        msg = re.sub(r"([^\\])", r"\\\1", msg)

        # ignore markdown monospace character
        return msg.replace("\\`", "`")
    else:
        return msg.replace("-", "\\-").replace(".", "\\.").replace("(", "\\(").replace(")", "\\)").replace("!", "\\!")


# register exception handler
def error_handler(update, context):
    logging.error("Error: %s", context.error)

    text = "Ops! Algo deu errado. O Bidu provavelmente tá de palhaçada.\n\n"
    text += "Erro:\n"
    text += "```\n"
    text += traceback.format_exc()
    text += "```"

    # send error message
    update.message.reply_text(
        text=prepare_message(text, hard_parse=False),
        parse_mode="MarkdownV2",
    )


dispatcher.add_error_handler(error_handler)

# start bot
updater.start_polling()
logging.info("Bot started and listening for commands.")
