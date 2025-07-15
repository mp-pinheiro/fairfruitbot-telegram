import logging
import re
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
        # track how many times each potential typo appears
        self._typo_count = defaultdict(int)
        # store the original message for each typo
        self._typo_original = {}
        # minimum repetitions to consider it a typo pattern
        self._min_repetitions = 1

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
                if self._is_potential_typo_word(text):
                    potential_typos.add(text)

        # also check individual words in longer messages
        words = text.split()
        for word in words:
            if self._is_potential_typo_word(word):
                potential_typos.add(word)

        return list(potential_typos)

    def _is_potential_typo_word(self, word):
        """
        Determine if a single word could be a typo.
        """
        # clean word
        word = word.strip().lower()

        # ignore empty words
        if not word:
            return False

        # ignore very short words (1-2 chars) unless they look like typos
        if len(word) <= 2:
            return False

        # ignore very long words (unlikely to be simple typos)
        if len(word) > 15:
            return False

        # ignore common words that aren't typos
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
            "com",
            "sem",
            "por",
            "para",
            "mais",
            "menos",
            "muito",
            "pouco",
            "bem",
            "mal",
            "foi",
            "vai",
            "tem",
            "ter",
            "ser",
            "estar",
            "fazer",
            "dar",
            "ver",
            # add more common Portuguese words
            "de",
            "do",
            "da",
            "dos",
            "das",
            "em",
            "no",
            "na",
            "nos",
            "nas",
            "um",
            "uma",
            "uns",
            "umas",
            "ou",
            "se",
            "me",
            "te",
            "lhe",
            "nos",
            "vos",
            "lhes",
            "meu",
            "minha",
            "meus",
            "minhas",
            "seu",
            "sua",
            "seus",
            "suas",
            "nosso",
            "nossa",
            "nossos",
            "nossas",
            "este",
            "esta",
            "estes",
            "estas",
            "esse",
            "essa",
            "esses",
            "essas",
            "aquele",
            "aquela",
            "aqueles",
            "aquelas",
            "isto",
            "isso",
            "aquilo",
            "boca",
            "cheia",
            "meio",
            "cheio",
            "toda",
            "todo",
            "todos",
            "todas",
            "cada",
            "alguns",
            "algumas",
            "nenhum",
            "nenhuma",
            "outro",
            "outra",
            "outros",
            "outras",
        }

        if word in common_words:
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

        # ignore words with punctuation (likely not typos)
        if re.search(r"[.!?:;,]", word):
            return False

        return True

    def _store_message(self, message):
        """Store message data for typo detection"""
        if message.chat_id in self._target_group_ids and message.text:
            try:
                message_data = create_message_data(message)
                self._message_buffer.append(message_data)
            except Exception as e:
                logging.error(f"Failed to store message: {e}")
                raise

    def _detect_typo_pattern(self, current_message):
        """
        Detect if the current message contains a typo that's part of a repetition pattern
        Returns the original message if pattern detected, None otherwise
        """
        # extract potential typos from current message
        current_typos = self._extract_potential_typos(current_message.text)
        
        if not current_typos:
            return None

        # check each potential typo for repetition patterns
        for typo in current_typos:
            # look for this typo in recent messages (including current)
            original_msg = None
            repetition_count = 0
            different_users = set()

            # search through recent messages in chronological order to find the original
            for msg_data in list(self._message_buffer):
                msg_typos = self._extract_potential_typos(msg_data["text"])
                
                if typo in msg_typos:
                    repetition_count += 1
                    different_users.add(msg_data["user_id"])

                    # store the earliest occurrence as original
                    if original_msg is None:
                        original_msg = msg_data

            # also count the current message
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
