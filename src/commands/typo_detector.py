import logging
import re
import os
from collections import defaultdict
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from modules import Singleton
from environment import Environment
from messaging import BaseMessageBuffer


class TypoDetector(BaseMessageBuffer, metaclass=Singleton):
    def __init__(self):
        self._env = Environment()
        self._target_group_ids = set(self._env.summary_group_ids)
        super().__init__(max_size=50, target_group_ids=self._target_group_ids)
        self._portuguese_words = self._load_portuguese_words()
        self._min_users = 3

    def _load_portuguese_words(self):
        portuguese_words = set()
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(os.path.dirname(current_dir))
            words_file = os.path.join(root_dir, 'data', 'portuguese_words.txt')
            
            if os.path.exists(words_file):
                with open(words_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip().lower()
                        if word:
                            portuguese_words.add(word)
                logging.info(f"Loaded {len(portuguese_words)} Portuguese words for filtering")
            else:
                logging.warning(f"Portuguese words file not found at {words_file}")
        except Exception as e:
            logging.error(f"Error loading Portuguese words: {e}")
        
        return portuguese_words

    def _extract_potential_typos(self, message_text):
        if not message_text:
            return []

        text = message_text.strip().lower()
        potential_typos = set()

        if len(text) <= 20:
            words = text.split()
            if len(words) <= 2:
                cleaned_text = re.sub(r'^[^\w]+|[^\w]+$', '', text)
                if self._is_potential_typo_word(cleaned_text):
                    potential_typos.add(cleaned_text)

        words = text.split()
        for word in words:
            if self._is_potential_typo_word(word):
                cleaned_word = re.sub(r'^[^\w]+|[^\w]+$', '', word.strip().lower())
                if cleaned_word:
                    potential_typos.add(cleaned_word)

        return list(potential_typos)

    def _is_potential_typo_word(self, word):
        word = word.strip().lower()
        word = re.sub(r'^[^\w]+|[^\w]+$', '', word)

        if not word or len(word) <= 2 or len(word) > 15:
            return False

        if word in self._portuguese_words:
            return False

        basic_common_words = {
            "sim", "não", "nao", "ok", "oi", "tchau", "obrigado", "obrigada",
            "valeu", "kkkk", "kkk", "rsrs", "haha", "hehe", "top", "legal",
            "massa", "show", "blz", "beleza", "pqp", "mano", "cara", "né", "ne",
            "the", "and", "but", "you", "are", "can", "get", "all", "new", "now",
            "old", "see", "him", "her", "its", "our", "out", "day", "way", "use",
            "man", "may", "say", "she", "how", "who", "oil", "sit", "set", "run",
            "eat", "far", "sea", "eye", "was", "boy", "girl", "this", "is", "a",
            "very", "long", "message", "that", "should", "not", "be", "considered", "typo"
        }

        if word in basic_common_words:
            return False

        if len(word) >= 3 and len(set(word)) <= 2:
            return False

        if word.isdigit() or re.match(r"^[^\w\s]+$", word):
            return False

        return True

    def _store_message(self, message):
        try:
            return self.store_message(message)
        except Exception as e:
            logging.error(f"Failed to store message: {e}")
            raise

    def _detect_typo_pattern(self, current_message):
        current_typos = self._extract_potential_typos(current_message.text)
        
        if not current_typos:
            return None

        for typo in current_typos:
            original_msg = None
            different_users = set()
            has_part_of_message = False
            has_full_message = False

            recent_messages = self.get_recent_messages()
            for msg_data in recent_messages:
                msg_typos = self._extract_potential_typos(msg_data["text"])
                
                if typo in msg_typos:
                    different_users.add(msg_data["user_id"])

                    if original_msg is None:
                        original_msg = msg_data
                    
                    words = msg_data["text"].strip().split()
                    if len(words) <= 2:
                        has_full_message = True
                    else:
                        has_part_of_message = True

            different_users.add(current_message.from_user.id)
            current_words = current_message.text.strip().split()
            if len(current_words) <= 2:
                has_full_message = True
            else:
                has_part_of_message = True

            if (len(different_users) >= 3 and 
                has_part_of_message and 
                has_full_message):
                return original_msg

        return None

    def _process(self, update, context):
        message = update.message
        if not message or not message.text:
            return

        chat_id = message.chat_id

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
