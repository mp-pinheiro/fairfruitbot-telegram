import logging
import re
from collections import deque, defaultdict
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from modules import Singleton
from environment import Environment


class TypoDetector(metaclass=Singleton):
    def __init__(self):
        self._env = Environment()
        self._target_group_ids = self._env.summary_group_ids
        # store recent messages from the target groups
        self._message_buffer = deque(maxlen=50)
        # track how many times each potential typo appears
        self._typo_count = defaultdict(int)
        # store the original message for each typo
        self._typo_original = {}
        # minimum repetitions to consider it a typo pattern
        self._min_repetitions = 2

    def _is_potential_typo(self, text):
        """
        Determine if a message could be a typo being repeated.
        Focus on short words or phrases that are likely typos.
        """
        # clean text
        text = text.strip().lower()

        # ignore empty messages
        if not text:
            return False

        # ignore messages that are too long (likely not just a typo)
        if len(text) > 20:
            return False

        # ignore messages with multiple words (unless very short)
        words = text.split()
        if len(words) > 2:
            return False
        if len(words) == 2 and len(text) > 15:
            return False

        # ignore common short words/phrases that aren't typos
        common_words = {
            "sim",
            "não",
            "nao",
            "ok",
            "oi",
            "tchau",
            "obrigado",
            "obrigada",
            "valeu",
            "kkkk",
            "kkk",
            "rsrs",
            "haha",
            "hehe",
            "top",
            "legal",
            "massa",
            "show",
            "blz",
            "beleza",
            "pqp",
            "mano",
            "cara",
            "né",
            "ne",
            "pra",
            "pro",
            "que",
            "q",
            "eh",
            "é",
            "ta",
            "tá",
        }

        if text in common_words:
            return False

        # ignore repeated character patterns like "kkkkk", "hahaha", etc.
        if len(text) >= 3 and len(set(text)) <= 2:
            return False

        # ignore pure numbers
        if text.isdigit():
            return False

        # ignore pure emoji or symbols
        if re.match(r"^[^\w\s]+$", text):
            return False

        return True

    def _store_message(self, message):
        """Store message data for typo detection"""
        if message.chat_id in self._target_group_ids and message.text:
            try:
                user_name = (
                    message.from_user.username
                    or message.from_user.first_name
                    or "Usuário"
                )
                message_data = {
                    "user": user_name,
                    "user_id": message.from_user.id,
                    "text": message.text,
                    "timestamp": message.date,
                    "message_id": message.message_id,
                    "chat_id": message.chat_id,
                }
                self._message_buffer.append(message_data)
            except Exception as e:
                logging.error(f"Failed to store message: {e}")
                raise

    def _detect_typo_pattern(self, current_message):
        """
        Detect if the current message is part of a typo repetition pattern
        Returns the original message if pattern detected, None otherwise
        """
        current_text = current_message.text.strip().lower()

        if not self._is_potential_typo(current_text):
            return None

        # look for this text in recent messages (including current)
        original_msg = None
        repetition_count = 0
        different_users = set()

        # search through recent messages in chronological order to find the original
        for msg_data in list(self._message_buffer):
            msg_text = msg_data["text"].strip().lower()

            if msg_text == current_text:
                repetition_count += 1
                different_users.add(msg_data["user_id"])

                # store the earliest occurrence as original
                if original_msg is None:
                    original_msg = msg_data

        # also count the current message
        if current_text == current_message.text.strip().lower():
            repetition_count += 1
            different_users.add(current_message.from_user.id)

        # pattern detected if:
        # 1. At least min_repetitions + 1 occurrences (original + min_repetitions repeats)
        # 2. At least 2 different users involved
        if (
            repetition_count >= (self._min_repetitions + 1)
            and len(different_users) >= 2
        ):
            return original_msg

        return None

    def _process(self, update, context):
        message = update.message
        if not message or not message.text:
            return

        chat_id = message.chat_id

        # log the message for debugging
        try:
            user_info = f"({message.from_user.id}) {message.from_user.username or message.from_user.full_name}"
            logging.info(
                f"TypoDetector - chat: {chat_id} - user: {user_info} - text: {message.text}"
            )
        except Exception:
            logging.info(f"TypoDetector - chat: {chat_id} - text: {message.text}")

        # only process messages from target groups
        if chat_id not in self._target_group_ids:
            return

        try:
            # check for typo pattern BEFORE storing the current message
            original_msg = self._detect_typo_pattern(message)

            # store the message after pattern detection
            self._store_message(message)

            if original_msg:
                # send the response as a reply to the original message
                response_text = "Pronto, proibido errar nesse grupo. 🤪"

                context.bot.send_message(
                    chat_id=chat_id,
                    text=response_text,
                    reply_to_message_id=original_msg["message_id"],
                    parse_mode=ParseMode.HTML,
                )

                logging.info(
                    f"TypoDetector triggered for typo: '{message.text}' - "
                    f"original by user {original_msg['user']}"
                )

        except Exception as e:
            logging.error(f"Error in TypoDetector._process: {e}")

    def setup(self, dispatcher):
        message_handler = MessageHandler(Filters.text & Filters.group, self._process)
        dispatcher.add_handler(message_handler)
