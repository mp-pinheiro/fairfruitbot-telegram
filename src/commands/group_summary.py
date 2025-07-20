import logging
import time
from collections import deque
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters

from clients import OpenAIClient
from environment import Environment
from utils import create_message_data
from commands.command import Command


class GroupSummary(Command):
    def __init__(self):
        super().__init__()
        self._env = Environment()
        self._trigger_patterns = [
            "6 falam",
            "vcs falam",
            "ces falam",
            "ceis falam",
            "seis falam",
            "voces falam",
            "vocês falam",
            "6️⃣",
        ]
        self._openai_client = OpenAIClient()
        self._message_buffer = deque(maxlen=100)
        self._last_summary_times = {}  # per-group cooldown tracking
        self._cooldown_seconds = 60  # 1 minute cooldown

    def _should_trigger(self, message_text):
        message_lower = message_text.lower()
        for pattern in self._trigger_patterns:
            if pattern.lower() in message_lower:
                return True
        return False

    def _store_message(self, message):
        if self._is_user_authorized(message.from_user.id, message.chat.type, message.chat_id) and message.text:
            try:
                message_data = create_message_data(message)
                simplified_data = {
                    "user": message_data["user"],
                    "text": message_data["text"],
                    "timestamp": message_data["timestamp"],
                }
                self._message_buffer.append(simplified_data)
            except Exception as e:
                logging.error(f"Failed to store message: {e}")
                raise

    def _get_recent_messages(self, limit=100):
        try:
            if not self._message_buffer:
                return ["[Nenhuma mensagem recente disponível]"]

            messages = []
            for msg_data in list(self._message_buffer)[-limit:]:
                message_text = msg_data["text"].lower()
                contains_trigger = any(pattern.lower() in message_text for pattern in self._trigger_patterns)

                if not contains_trigger:
                    formatted_msg = f"{msg_data['user']}: {msg_data['text']}"
                    messages.append(formatted_msg)

            return messages

        except Exception as e:
            logging.error(f"Error getting recent messages: {e}")
            return ["[Erro ao recuperar mensagens]"]

    def _summarize_messages(self, messages):
        try:
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

            summary = self._openai_client.make_request(messages=openai_messages, max_tokens=300)

            return summary.strip() if summary else "Não foi possível gerar um resumo."

        except Exception as e:
            logging.error(f"Error summarizing messages: {e}")
            return "Erro ao processar o resumo."

    def _process(self, update, context):
        message = update.message
        if not message or not message.text:
            return

        chat_id = message.chat_id
        message_text = message.text

        if message_text and isinstance(message_text, bytes):
            message_text = message_text.decode("utf-8", errors="replace")

        if not self._is_user_authorized(message.from_user.id, message.chat.type, chat_id):
            return


        try:
            self._store_message(message)
        except Exception as e:
            logging.error(f"GroupSummary processing stopped due to storage failure: {e}")
            return

        if not self._should_trigger(message_text):
            return

        # check per-group cooldown
        current_time = time.time()
        last_summary_time = self._last_summary_times.get(chat_id, 0)
        if current_time - last_summary_time < self._cooldown_seconds:
            remaining = int(self._cooldown_seconds - (current_time - last_summary_time))
            context.bot.send_message(
                chat_id=chat_id,
                text=f"🕐 Calma aí! Espera mais {remaining} segundos para outro resumo.",
                parse_mode=ParseMode.HTML,
            )
            return

        try:
            recent_messages = self._get_recent_messages()

            if len(recent_messages) < 5:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="6️⃣ falam eim! Mas ainda não tenho mensagens suficientes para resumir.",
                    parse_mode=ParseMode.HTML,
                )
                return

            summary = self._summarize_messages(recent_messages)

            response_text = f"6️⃣ falam eim!\n\n{summary}\n\nResumo gerado por Bidu-GPT."

            context.bot.send_message(chat_id=chat_id, text=response_text, parse_mode=ParseMode.HTML)
            
            # update per-group cooldown timestamp after successful summary
            self._last_summary_times[chat_id] = time.time()

        except Exception as e:
            logging.error(f"Error in GroupSummary._process: {e}")
            context.bot.send_message(
                chat_id=chat_id,
                text="Ops! Não consegui processar o resumo agora.",
                parse_mode=ParseMode.HTML,
            )

    def setup(self, dispatcher):
        message_handler = MessageHandler(Filters.text & Filters.group, self._process)
        dispatcher.add_handler(message_handler, group=0)
