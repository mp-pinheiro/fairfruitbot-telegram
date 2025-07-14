import logging
from collections import deque
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from clients import OpenAIClient
from modules import Singleton
from environment import Environment


class GroupSummary(metaclass=Singleton):
    def __init__(self):
        self._env = Environment()
        self._target_group_ids = self._env.summary_group_ids
        self._trigger_patterns = ["6 falam", "vcs falam", "ces falam", "6️⃣"]
        self._openai_client = OpenAIClient()
        # store recent messages from the target groups
        self._message_buffer = deque(maxlen=100)

    def _should_trigger(self, message_text, chat_id):
        try:
            # check if it's one of the target groups
            if chat_id not in self._target_group_ids:
                return False

            # safely check if message contains any trigger patterns
            if not message_text:
                return False
                
            message_lower = message_text.lower()
            for pattern in self._trigger_patterns:
                if pattern.lower() in message_lower:
                    return True

            return False
        except Exception as e:
            logging.error(f"Error in _should_trigger: {e}")
            return False  # Fail safely by not triggering

    def _store_message(self, message):
        # Add safety checks to prevent any failures in message storage
        try:
            if not message or not hasattr(message, 'chat_id') or not hasattr(message, 'text'):
                return
                
            if message.chat_id not in self._target_group_ids or not message.text:
                return
                
            # safely extract user name with fallbacks
            try:
                user_name = (
                    message.from_user.username or 
                    message.from_user.first_name or 
                    f"User_{message.from_user.id}" if message.from_user else "Unknown"
                )
            except (AttributeError, TypeError):
                user_name = "Unknown"
            
            # safely extract timestamp
            try:
                timestamp = message.date
            except (AttributeError, TypeError):
                from datetime import datetime
                timestamp = datetime.now()
            
            message_data = {
                "user": user_name,
                "text": message.text,
                "timestamp": timestamp,
            }
            self._message_buffer.append(message_data)
            
        except Exception as e:
            # Log the error but don't let it propagate and break message logging
            logging.error(f"Error in _store_message: {e}")
            logging.debug(f"Message object: {message}")  # Add debug info

    def _get_recent_messages(self, limit=100):
        try:
            if not self._message_buffer:
                return ["[Nenhuma mensagem recente disponível]"]

            # convert stored messages to text format for summarization
            messages = []
            for msg_data in list(self._message_buffer)[-limit:]:
                # filter out messages that contain trigger patterns
                message_text = msg_data["text"].lower()
                contains_trigger = any(
                    pattern.lower() in message_text
                    for pattern in self._trigger_patterns
                )

                if not contains_trigger:
                    formatted_msg = f"{msg_data['user']}: {msg_data['text']}"
                    messages.append(formatted_msg)

            return messages

        except Exception as e:
            logging.error(f"Error getting recent messages: {e}")
            return ["[Erro ao recuperar mensagens]"]

    def _summarize_messages(self, messages):
        try:
            # prepare the conversation context for OpenAI
            messages_text = "\n".join(messages)

            system_prompt = (
                "Você é um assistente que resume conversas em português brasileiro. "
                "Crie um resumo conciso e natural do que foi discutido, "
                "focando nos principais tópicos e pontos importantes. "
                "Mantenha o resumo breve e informativo. "
                "NÃO comece o resumo com 'Resumo da conversa' ou similar."
            )

            user_prompt = f"Resuma esta conversa em português:\n\n{messages_text}"

            openai_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            summary = self._openai_client.make_request(
                messages=openai_messages, max_tokens=300
            )

            return summary.strip() if summary else "Não foi possível gerar um resumo."

        except Exception as e:
            logging.error(f"Error summarizing messages: {e}")
            return "Erro ao processar o resumo."

    def _process(self, update, context):
        # Early validation with minimal processing to ensure logging happens first
        if not update or not update.message:
            return
        
        message = update.message
        if not message.text:
            return

        chat_id = message.chat_id
        message_text = message.text

        # Only process messages from target groups
        if chat_id not in self._target_group_ids:
            return

        # Log the message FIRST and ALWAYS - this is the critical functionality
        # Wrap in try-catch to ensure this never fails and stops processing
        try:
            user_info = f"({message.from_user.id}) {message.from_user.username or message.from_user.full_name}"
            logging.info(
                f"GroupSummary - chat: {chat_id} - user: {user_info} - text: {message_text}"
            )
        except Exception as e:
            # Use a fallback logging approach if user info extraction fails
            try:
                logging.info(f"GroupSummary - chat: {chat_id} - user: [ERROR getting user info] - text: {message_text}")
                logging.debug(f"Error extracting user info: {e}")
            except Exception as e2:
                # Last resort logging
                logging.error(f"Critical error in GroupSummary message logging: {e2}")

        # Store messages from target groups - isolated from logging
        try:
            self._store_message(message)
        except Exception as e:
            logging.error(f"Error storing message in GroupSummary: {e}")

        # Check if this message should trigger the summary - isolated from logging
        try:
            should_trigger = self._should_trigger(message_text, chat_id)
        except Exception as e:
            logging.error(f"Error checking trigger in GroupSummary: {e}")
            return

        if not should_trigger:
            return

        # Summary generation and sending - isolated from logging
        try:
            # get recent messages from our buffer
            recent_messages = self._get_recent_messages()

            # skip if we don't have enough messages
            if len(recent_messages) < 5:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="6️⃣ falam eim! Mas ainda não tenho mensagens suficientes para resumir.",
                    parse_mode=ParseMode.HTML,
                )
                return

            # generate summary
            summary = self._summarize_messages(recent_messages)

            # send response
            response_text = (
                f"6️⃣ falam eim!\n\n{summary}\n\nResumo gerado por Bidu-GPT."
            )

            context.bot.send_message(
                chat_id=chat_id, text=response_text, parse_mode=ParseMode.HTML
            )

        except Exception as e:
            logging.error(f"Error in GroupSummary summary processing: {e}")
            try:
                # send error message
                context.bot.send_message(
                    chat_id=chat_id,
                    text="Ops! Não consegui processar o resumo agora.",
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e2:
                logging.error(f"Error sending error message in GroupSummary: {e2}")

    def setup(self, dispatcher):
        message_handler = MessageHandler(Filters.text & Filters.group, self._process)
        dispatcher.add_handler(message_handler)
