import logging

from telegram.constants import ParseMode
from telegram.ext import CommandHandler

from modules import Singleton
from environment import Environment


class Command(metaclass=Singleton):
    def __init__(self):
        # override in subclass
        self._command = None
        self._fetcher = None
        self._env = Environment()

    def _is_user_authorized(self, user_id, chat_type=None, chat_id=None):
        # backward compatibility: no chat_type provided
        if chat_type is None:
            if not self._env.allowed_user_ids:
                return True
            return user_id in self._env.allowed_user_ids

        # private messages: check user authorization
        if chat_type == 'private':
            if not self._env.allowed_user_ids:
                return True
            return user_id in self._env.allowed_user_ids

        # group messages: allow any user in allowed groups
        if chat_type in ['group', 'supergroup']:
            if not self._env.allowed_user_ids:
                return True
            import os
            explicit_summary_groups = os.getenv('SUMMARY_GROUP_IDS')
            if not explicit_summary_groups:
                return True
            return chat_id in self._env.summary_group_ids

        # default to user-based authorization
        if not self._env.allowed_user_ids:
            return True
        return user_id in self._env.allowed_user_ids

    def _process(self, update, context):
        # override in subclass, call super()
        userid = update.message.from_user.id
        display_name = update.message.from_user.username
        text = update.message.text
        chat_id = update.message.chat.id
        chat_type = update.message.chat.type
        if not display_name:
            display_name = update.message.from_user.full_name

        # check authorization
        if not self._is_user_authorized(userid, chat_type, chat_id):
            logging.warning(
                f"Unauthorized access attempt - "
                f"command: {self._command} - "
                f"user: ({userid}) {display_name} - "
                f"chat: {chat_id} - "
                f"chat_type: {chat_type}"
            )
            return context.bot.send_message(
                chat_id=update.message.chat.id,
                text="🚫 Você não tem permissão para usar este comando.",
                parse_mode=ParseMode.HTML,
            )

        logging.info(
            f"command: {self._command} - "
            f"user: ({userid}) {display_name} - "
            f"chat: {chat_id} - "
            f"chat_type: {chat_type} - "
            f"text: {text}"
        )
        return context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Processando comando...",
            parse_mode=ParseMode.HTML,
        )

    def setup(self, dispatcher):
        inline_handler = CommandHandler(self._command, self._process)
        dispatcher.add_handler(inline_handler)
