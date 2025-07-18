import logging
import re
import os
from collections import deque, defaultdict
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from modules import Singleton
from environment import Environment
from utils import create_message_data


class TypoDetector(metaclass=Singleton):
    def __init__(self):
        self._env = Environment()
        self._target_group_ids = self._env.summary_group_ids
        # store recent messages from the target groups
        self._message_buffer = deque(maxlen=50)
        # load Portuguese words for filtering
        self._portuguese_words = self._load_portuguese_words()
        # minimum different users required to trigger
        self._min_users = 2

        logging.info(
            f"TypoDetector initialized - target groups: {list(self._target_group_ids)}, min users: {self._min_users}, Portuguese words: {len(self._portuguese_words)}"
        )
        logging.info(f"TypoDetector setup complete and ready to process messages")

    def _load_portuguese_words(self):
        """Load Portuguese words from the word list file"""
        portuguese_words = set()
        try:
            # get the path to the data directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(os.path.dirname(current_dir))
            words_file = os.path.join(root_dir, "data", "portuguese_words.txt")

            if os.path.exists(words_file):
                with open(words_file, "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip().lower()
                        if word:
                            portuguese_words.add(word)
                logging.info(
                    f"Loaded {len(portuguese_words)} Portuguese words for filtering"
                )
            else:
                logging.warning(f"Portuguese words file not found at {words_file}")
        except Exception as e:
            logging.error(f"Error loading Portuguese words: {e}")

        return portuguese_words

    def _extract_potential_typos(self, message_text):
        """
        Extract potential typos from a message.
        Returns a list of potential typos found in the message.
        """
        if not message_text:
            return []

        # clean text
        text = message_text.strip().lower()
        potential_typos = set()  # use set to avoid duplicates

        # if the entire message is short, check if it's a potential typo
        if len(text) <= 20:
            words = text.split()
            if len(words) <= 2:
                # Clean the entire text for potential typo check
                cleaned_text = re.sub(r"^[^\w]+|[^\w]+$", "", text)
                if self._is_potential_typo_word(cleaned_text):
                    potential_typos.add(cleaned_text)
                    logging.debug(
                        f"TypoDetector - extracted full message typo: '{cleaned_text}' from '{message_text}'"
                    )

        # also check individual words in longer messages
        words = text.split()
        for word in words:
            if self._is_potential_typo_word(word):
                # Add the cleaned version of the word (punctuation removed)
                cleaned_word = re.sub(r"^[^\w]+|[^\w]+$", "", word.strip().lower())
                if cleaned_word:
                    potential_typos.add(cleaned_word)
                    logging.debug(
                        f"TypoDetector - extracted individual word typo: '{cleaned_word}' from '{message_text}'"
                    )

        result = list(potential_typos)
        if result:
            logging.debug(
                f"TypoDetector - total potential typos extracted from '{message_text}': {result}"
            )
        return result

    def _is_potential_typo_word(self, word):
        """
        Determine if a single word could be a typo.
        """
        # clean word and remove punctuation
        word = word.strip().lower()
        # Remove common punctuation from the end/beginning of words
        word = re.sub(r"^[^\w]+|[^\w]+$", "", word)

        # ignore empty words
        if not word:
            return False

        # ignore very short words (1-2 chars) unless they look like typos
        if len(word) <= 2:
            return False

        # ignore very long words (unlikely to be simple typos)
        if len(word) > 15:
            return False

        # ignore Portuguese words using the loaded word list
        if word in self._portuguese_words:
            return False

        # ignore basic common words that might not be in the Portuguese list
        basic_common_words = {
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
            # Common English words that might appear in mixed messages
            "the",
            "and",
            "but",
            "you",
            "are",
            "can",
            "get",
            "all",
            "new",
            "now",
            "old",
            "see",
            "him",
            "her",
            "its",
            "our",
            "out",
            "day",
            "way",
            "use",
            "man",
            "may",
            "say",
            "she",
            "how",
            "who",
            "oil",
            "sit",
            "set",
            "run",
            "eat",
            "far",
            "sea",
            "eye",
            "was",
            "boy",
            "girl",
            "this",
            "is",
            "a",
            "very",
            "long",
            "message",
            "that",
            "should",
            "not",
            "be",
            "considered",
            "typo",
        }

        if word in basic_common_words:
            return False

        # ignore repeated character patterns like "kkkkk", "hahaha", etc.
        if len(word) >= 3 and len(set(word)) <= 2:
            return False

        # ignore pure numbers
        if word.isdigit():
            return False

        # ignore pure emoji or symbols
        if re.match(r"^[^\w\s]+$", word):
            return False

        return True

    def _store_message(self, message):
        """Store message data for typo detection"""
        if message.chat_id in self._target_group_ids and message.text:
            try:
                message_data = create_message_data(message)
                self._message_buffer.append(message_data)
                logging.info(
                    f"TypoDetector - stored message from user {message_data['user_id']}: '{message_data['text']}' (buffer size: {len(self._message_buffer)})"
                )
            except Exception as e:
                logging.error(f"Failed to store message: {e}")
                raise

    def _detect_typo_pattern(self, current_message):
        """
        Detect if the current message contains a typo that's part of a repetition pattern
        Returns the original message if pattern detected, None otherwise

        New pattern: requires 3 different users with specific conditions:
        - At least one occurrence as part of a longer message (original context)
        - At least one occurrence as the full message (≤ 2 words)
        """
        # extract potential typos from current message
        current_typos = self._extract_potential_typos(current_message.text)

        logging.info(
            f"TypoDetector - current message '{current_message.text}' has potential typos: {current_typos}"
        )

        if not current_typos:
            return None

        # check each potential typo for repetition patterns
        for typo in current_typos:
            logging.info(f"TypoDetector - checking typo pattern for: '{typo}'")

            # look for this typo in recent messages (including current)
            original_msg = None
            different_users = set()
            has_part_of_message = False  # typo as part of longer message
            has_full_message = False  # typo as the full message

            # search through recent messages in chronological order
            for msg_data in list(self._message_buffer):
                msg_typos = self._extract_potential_typos(msg_data["text"])

                if typo in msg_typos:
                    different_users.add(msg_data["user_id"])

                    # store the earliest occurrence as original
                    if original_msg is None:
                        original_msg = msg_data

                    # check message context - important: check if the typo is the ENTIRE message
                    # (not just <= 2 words, but actually the cleaned text equals the typo)
                    cleaned_text = re.sub(
                        r"^[^\w]+|[^\w]+$", "", msg_data["text"].strip().lower()
                    )
                    if cleaned_text == typo:
                        has_full_message = True
                        logging.info(
                            f"TypoDetector - found '{typo}' as FULL MESSAGE in: '{msg_data['text']}' by user {msg_data['user_id']}"
                        )
                    else:
                        has_part_of_message = True
                        logging.info(
                            f"TypoDetector - found '{typo}' as PART OF MESSAGE in: '{msg_data['text']}' by user {msg_data['user_id']}"
                        )

            # also check the current message
            different_users.add(current_message.from_user.id)
            current_cleaned_text = re.sub(
                r"^[^\w]+|[^\w]+$", "", current_message.text.strip().lower()
            )
            if current_cleaned_text == typo:
                has_full_message = True
                logging.info(
                    f"TypoDetector - current message '{current_message.text}' has '{typo}' as FULL MESSAGE by user {current_message.from_user.id}"
                )
            else:
                has_part_of_message = True
                logging.info(
                    f"TypoDetector - current message '{current_message.text}' has '{typo}' as PART OF MESSAGE by user {current_message.from_user.id}"
                )

            logging.info(
                f"TypoDetector - typo '{typo}' analysis: users={sorted(different_users)}, has_part_of_message={has_part_of_message}, has_full_message={has_full_message}"
            )

            # pattern detected if:
            # 1. Same word appears by min_users different users
            # 2. At least one occurrence is part of a longer message
            # 3. At least one occurrence is the full message
            if (
                len(different_users) >= self._min_users
                and has_part_of_message
                and has_full_message
            ):
                logging.info(
                    f"TypoDetector - PATTERN DETECTED for '{typo}' - triggering response!"
                )
                return original_msg
            else:
                logging.info(
                    f"TypoDetector - pattern NOT detected for '{typo}' - need: {self._min_users}+ users ({len(different_users)} found), part_of_message ({has_part_of_message}), full_message ({has_full_message})"
                )

        return None

    def _process(self, update, context):
        message = update.message
        if not message or not message.text:
            return

        chat_id = message.chat_id

        try:
            user_info = f"({message.from_user.id}) {message.from_user.username or message.from_user.full_name}"
            logging.info(
                f"TypoDetector - chat: {chat_id} - user: {user_info} - text: {message.text}"
            )
        except Exception:
            logging.info(f"TypoDetector - chat: {chat_id} - text: {message.text}")

        # only process messages from target groups
        if chat_id not in self._target_group_ids:
            logging.info(
                f"TypoDetector - ignoring message from chat {chat_id} (not in target groups: {list(self._target_group_ids)})"
            )
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

                # only log when we actually trigger
                logging.info(
                    f"TypoDetector triggered for typo: '{message.text}' - "
                    f"original by user {original_msg['user']}"
                )

        except Exception as e:
            logging.error(f"Error in TypoDetector._process: {e}")

    def setup(self, dispatcher):
        message_handler = MessageHandler(Filters.text & Filters.group, self._process)
        dispatcher.add_handler(message_handler)
        logging.info("TypoDetector handler registered successfully")
