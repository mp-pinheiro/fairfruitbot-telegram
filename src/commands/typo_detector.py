import logging
import re
from collections import deque, defaultdict
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from environment import Environment
from utils import create_message_data
from clients.openai_client import OpenAIClient
from commands.command import Command


class TypoDetector(Command):
    def __init__(self):
        super().__init__()
        self._env = Environment()
        self._message_buffer = deque(maxlen=50)
        self._min_users = 1 if self._env.dev_mode else 3
        self._openai_client = OpenAIClient()

        logging.info(f"TypoDetector initialized - min users: {self._min_users}")
        logging.info(f"TypoDetector setup complete and ready to process messages")

    def _extract_words(self, message_text):
        if not message_text:
            return []

        text = message_text.strip().lower()
        words = re.findall(r"\b\w+\b", text)

        words = [word for word in words if len(word) >= 3]

        logging.debug(f"TypoDetector - extracted words from '{message_text}': {words}")
        return words

    def _is_typo_via_gpt(self, word, context_messages):
        try:
            examples = [
                "User says 'me' repeatedly → Actually meant 'né' (Brazilian Portuguese for 'right?')",
                "User says 'casa' repeatedly → Actually meant 'cada' (each instead of house)",
                "User says 'fazedo' repeatedly → Actually meant 'fazendo' (doing)",
                "User says 'mudno' repeatedly → Actually meant 'mundo' (world)",
                "User says 'tendeyu' repeatedly → Actually meant 'entendeu' (understood)",
            ]

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
        if self._is_user_authorized(message.from_user.id, message.chat.type, message.chat_id):
            try:
                text_content = message.text or (message.caption if hasattr(message, "caption") else None)

                if text_content:
                    message_data = create_message_data(message)
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
        current_text = current_message.text or (
            current_message.caption if hasattr(current_message, "caption") else None
        )
        if not current_text:
            return None

        current_words = self._extract_words(current_text)

        logging.info(f"TypoDetector - current message '{current_text}' has words: {current_words}")

        if not current_words:
            return None

        for word in current_words:
            logging.info(f"TypoDetector - checking repetition pattern for: '{word}'")

            original_msg = None
            different_users = set()
            all_messages_with_word = []

            for msg_data in list(self._message_buffer):
                msg_words = self._extract_words(msg_data["text"])

                if word in msg_words:
                    different_users.add(msg_data["user_id"])
                    all_messages_with_word.append(msg_data)

                    if original_msg is None:
                        original_msg = msg_data

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

            if len(different_users) >= self._min_users:
                logging.info(f"TypoDetector - REPETITION PATTERN DETECTED for '{word}' - {len(different_users)} users")

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

        if not self._is_user_authorized(message.from_user.id, message.chat.type, chat_id):
            return

        try:
            original_msg = self._detect_repetition_pattern(message)

            self._store_message(message)

            if original_msg:
                response_text = "Pronto, proibido errar nesse grupo. 🤪"

                context.bot.send_message(
                    chat_id=chat_id,
                    text=response_text,
                    reply_to_message_id=original_msg["message_id"],
                    parse_mode=ParseMode.HTML,
                )

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
