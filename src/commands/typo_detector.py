import logging
import re
from collections import deque
from telegram import ParseMode, ChatAction
from telegram.ext import MessageHandler, Filters

from environment import Environment
from utils import create_message_data
from modules import PrivacyManager
from modules.typo_tracker import TypoTracker
from clients.openai_client import OpenAIClient
from commands.command import Command


class TypoDetector(Command):
    def __init__(self):
        super().__init__()
        self._env = Environment()
        self._message_buffers = {}  # per-group message buffers
        self._min_users = int(self._env._validate_optional("MIN_USERS", "3"))
        self._last_triggered_words = {}  # per-group cooldowns
        self._openai_client = OpenAIClient()
        self._typo_tracker = TypoTracker()


    def _extract_words(self, message_text):
        if not message_text:
            return []

        text = message_text.strip().lower()
        words = re.findall(r"\b\w+\b", text)

        words = [word for word in words if len(word) >= 3]

        return words

    def _is_typo_via_gpt(self, word, context_messages):
        try:
            # anonymize messages before sending to GPT
            privacy_manager = PrivacyManager()
            anon_messages, _ = privacy_manager.anonymize_messages(context_messages)
            
            examples = [
                "User says 'me' repeatedly → Actually meant 'né' (Brazilian Portuguese for 'right?')",
                "User says 'casa' repeatedly → Actually meant 'cada' (each instead of house)",
                "User says 'fazedo' repeatedly → Actually meant 'fazendo' (doing)",
                "User says 'mudno' repeatedly → Actually meant 'mundo' (world)",
                "User says 'tendeyu' repeatedly → Actually meant 'entendeu' (understood)",
            ]

            context = "\n".join([f"{msg['user']}: {msg['text']}" for msg in anon_messages[-5:]])

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

                    # get or create buffer for this group
                    chat_id = message.chat_id
                    if chat_id not in self._message_buffers:
                        self._message_buffers[chat_id] = deque(maxlen=50)
                    
                    self._message_buffers[chat_id].append(message_data)
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


        if not current_words:
            return None

        # get per-group last triggered word
        chat_id = current_message.chat_id
        last_triggered_word = self._last_triggered_words.get(chat_id)

        # reset cooldown if user says something different
        if current_words and last_triggered_word and last_triggered_word not in current_words:
            self._last_triggered_words[chat_id] = None
            last_triggered_word = None

        for word in current_words:
            # skip if we already triggered on this word recently
            if word == last_triggered_word:
                continue


            original_msg = None
            different_users = set()
            all_messages_with_word = []

            # use per-group buffer
            message_buffer = self._message_buffers.get(chat_id, deque())
            for msg_data in list(message_buffer):
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

            # if no original message found in buffer, use current message
            if original_msg is None:
                original_msg = current_msg_data


            if len(different_users) >= self._min_users:
                is_typo = self._is_typo_via_gpt(word, all_messages_with_word)

                if is_typo:
                    self._last_triggered_words[chat_id] = word
                    return original_msg

        return None

    def _process(self, update, context):
        message = update.message
        if not message:
            return

        text_content = message.text or (message.caption if hasattr(message, "caption") else None)
        if not text_content:
            return

        chat_id = message.chat_id


        if not self._is_user_authorized(message.from_user.id, message.chat.type, chat_id):
            return

        try:
            original_msg = self._detect_repetition_pattern(message)

            self._store_message(message)

            if original_msg:
                # send typing indicator now that we're confirmed to send a response
                context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                
                # get the criminal (user who made the original typo)
                criminal_user_id = original_msg["user_id"]
                criminal_username = original_msg.get("user", "Anônimo")
                last_triggered_word = self._last_triggered_words.get(chat_id)
                
                # add typo to tracker for the criminal
                self._typo_tracker.add_typo(criminal_user_id, criminal_username, last_triggered_word)
                
                # get top users by error count for ranking
                top_users = self._typo_tracker.get_top_users(3)
                
                # build the ultra-sarcastic wanted poster
                response_text = "🚨 ALERTA MÁXIMO: ERRO ORTOGRÁFICO DETECTADO 🚨\n\n"
                response_text += f"🎯 SUSPEITO PRINCIPAL: {criminal_username}\n"
                response_text += f"⚡ CRIME HEDIONDO: Escreveu '{last_triggered_word}'\n"
                response_text += f"📱 GRAVIDADE: Máxima (errar no Telegram!!)\n\n"

                if top_users:
                    response_text += "🏆 HERÓIS NACIONAIS (Top 3 Cagadores de Erro):\n"
                    for i, (username, error_count) in enumerate(top_users, 1):
                        response_text += f"{i}. {username} - {error_count} erro{'s' if error_count != 1 else ''}\n"
                else:
                    response_text += "🏆 NENHUM HERÓI NACIONAL (ainda)\n"

                response_text += "\n🤡 PARABÉNS GUYZ, COMEDY ACHIEVED! 🤡"

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

