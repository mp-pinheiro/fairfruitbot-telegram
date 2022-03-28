import logging

from telegram.ext import Updater

from commands import sign, tarot
from environment import Environment

# load env
env = Environment()

# load commands
commands = [sign.Sign(), tarot.Tarot()]

# fetch updater and job queue
logging.info("Starting bot...")
updater = Updater(token=env.telegram_token, use_context=True)
dispatcher = updater.dispatcher

# setup commands
for command in commands:
    command.setup(dispatcher)

# start bot
updater.start_polling()
logging.info("Bot started and listening for commands.")
