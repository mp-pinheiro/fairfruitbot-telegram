import logging
import re
from collections import deque, defaultdict
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from modules import Singleton
from environment import Environment
from utils import create_message_data
from clients.openai_client import OpenAIClient


class TypoDetector(metaclass=Singleton):
    def __init__(self):
        self._env = Environment()
        self._target_group_ids = self._env.summary_group_ids
        # store recent messages from the target groups
        self._message_buffer = deque(maxlen=50)
        # minimum different users required to trigger
        self._min_users = 3
        # OpenAI client for typo validation
        self._openai_client = OpenAIClient()

        logging.info(
            f"TypoDetector initialized - target groups: {list(self._target_group_ids)}, min users: {self._min_users}"
        )
        logging.info(f"TypoDetector setup complete and ready to process messages")

    def _extract_words(self, message_text):
        if not message_text:
            return []

        # clean text and extract words
        text = message_text.strip().lower()
        # remove punctuation from start/end of words
        words = re.findall(r"\b\w+\b", text)

        # filter out very short words (less than 3 characters)
        words = [word for word in words if len(word) >= 3]

        logging.debug(f"TypoDetector - extracted words from '{message_text}': {words}")
        return words

    def _is_typo_via_gpt(self, word, context_messages):
        try:
            # Create examples and context for the prompt
            examples = [
                "User says 'me' repeatedly → Actually meant 'né' (Brazilian Portuguese for 'right?')",
                "User says 'casa' repeatedly → Actually meant 'cada' (each instead of house)",
                "User says 'fazedo' repeatedly → Actually meant 'fazendo' (doing)",
                "User says 'mudno' repeatedly → Actually meant 'mundo' (world)",
                "User says 'tendeyu' repeatedly → Actually meant 'entendeu' (understood)",
            ]

            # Build context from recent messages
            context = "\n".join([f"User {msg['user_id']}: {msg['text']}" for msg in context_messages[-5:]])

            messages = [
                {
                    "role": "system",
                    "content": f"""You are a typo detector for Brazilian Portuguese. Analyze if a word being repeated by multiple users is likely a typo or intentional repetition.

Examples of common typos:
{chr(10).join(examples)}

Respond with only "YES" if it's likely a typo, or "NO" if it's intentional repetition or a real word being used correctly.""",
                },
                {
                    "role": "user",
                    "content": f"""Word being repeated: "{word}"

Recent conversation context:
{context}

Is "{word}" likely a typo? Answer only YES or NO.""",
                },
            ]

            response = self._openai_client.make_request(messages, max_tokens=10)
            is_typo = response.strip().upper() == "YES"

            logging.info(f"TypoDetector - GPT analysis for '{word}': {response.strip()} (is_typo: {is_typo})")
            return is_typo

        except Exception as e:
            logging.error(f"Error calling GPT for typo validation: {e}")
            return True

    def _store_message(self, message):
        if message.chat_id in self._target_group_ids:
            try:
                # Get text from either message text or photo caption
                text_content = message.text or (message.caption if hasattr(message, "caption") else None)

                if text_content:
                    message_data = create_message_data(message)
                    # Override text with caption if it's a photo
                    if message.caption and not message.text:
                        message_data["text"] = message.caption

                    self._message_buffer.append(message_data)
                    logging.info(
                        f"TypoDetector - stored message from user {message_data['user_id']}: '{message_data['text']}' (buffer size: {len(self._message_buffer)})"
                    )
            except Exception as e:
                logging.error(f"Failed to store message: {e}")
                raise

    def _detect_repetition_pattern(self, current_message):
        # Get text from message or caption
        current_text = current_message.text or (
            current_message.caption if hasattr(current_message, "caption") else None
        )
        if not current_text:
            return None

        # extract words from current message
        current_words = self._extract_words(current_text)

        logging.info(f"TypoDetector - current message '{current_text}' has words: {current_words}")

        if not current_words:
            return None

        # check each word for repetition patterns
        for word in current_words:
            logging.info(f"TypoDetector - checking repetition pattern for: '{word}'")

            # look for this word in recent messages (including current)
            original_msg = None
            different_users = set()
            all_messages_with_word = []

            # search through recent messages
            for msg_data in list(self._message_buffer):
                msg_words = self._extract_words(msg_data["text"])

                if word in msg_words:
                    different_users.add(msg_data["user_id"])
                    all_messages_with_word.append(msg_data)

                    # store the earliest occurrence as original
                    if original_msg is None:
                        original_msg = msg_data

            # also check the current message
            different_users.add(current_message.from_user.id)
            current_msg_data = {
                "text": current_text,
                "user_id": current_message.from_user.id,
                "message_id": current_message.message_id,
            }
            all_messages_with_word.append(current_msg_data)

            logging.info(
                f"TypoDetector - word '{word}' found in {len(different_users)} different users: {sorted(different_users)}"
            )

            # pattern detected if same word appears by 3+ different users
            if len(different_users) >= self._min_users:
                logging.info(f"TypoDetector - REPETITION PATTERN DETECTED for '{word}' - {len(different_users)} users")

                # validate with GPT if it's actually a typo
                is_typo = self._is_typo_via_gpt(word, all_messages_with_word)

                if is_typo:
                    logging.info(f"TypoDetector - GPT confirmed '{word}' is a typo - triggering response!")
                    return original_msg
                else:
                    logging.info(f"TypoDetector - GPT says '{word}' is not a typo - skipping")
            else:
                logging.info(
                    f"TypoDetector - pattern NOT detected for '{word}' - need: {self._min_users}+ users ({len(different_users)} found)"
                )

        return None

    def _process(self, update, context):
        message = update.message
        if not message:
            return

        # Get text from either message text or photo caption
        text_content = message.text or (message.caption if hasattr(message, "caption") else None)
        if not text_content:
            return

        chat_id = message.chat_id

        try:
            user_info = f"({message.from_user.id}) {message.from_user.username or message.from_user.full_name}"
            content_type = "caption" if message.caption and not message.text else "text"
            logging.info(f"TypoDetector - chat: {chat_id} - user: {user_info} - {content_type}: {text_content}")
        except Exception:
            content_type = "caption" if message.caption and not message.text else "text"
            logging.info(f"TypoDetector - chat: {chat_id} - {content_type}: {text_content}")

        # only process messages from target groups
        if chat_id not in self._target_group_ids:
            logging.info(
                f"TypoDetector - ignoring message from chat {chat_id} (not in target groups: {list(self._target_group_ids)})"
            )
            return

        try:
            # check for repetition pattern BEFORE storing the current message
            original_msg = self._detect_repetition_pattern(message)

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
                    f"TypoDetector triggered for repeated word in: '{text_content}' - "
                    f"original by user {original_msg.get('user', original_msg.get('user_id'))}"
                )

        except Exception as e:
            logging.error(f"Error in TypoDetector._process: {e}")

    def setup(self, dispatcher):
        text_handler = MessageHandler(Filters.text & Filters.group, self._process)
        photo_handler = MessageHandler(Filters.photo & Filters.group & Filters.caption, self._process)

        dispatcher.add_handler(text_handler, group=1)
        dispatcher.add_handler(photo_handler, group=1)

        logging.info("TypoDetector handlers registered successfully (text messages and photo captions) with group=1")
