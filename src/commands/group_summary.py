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
        self._trigger_patterns = [
            "6 falam",
            "vcs falam",
            "ces falam",
            "6️⃣"
        ]
        self._openai_client = OpenAIClient()
        # Store recent messages from the target groups
        self._message_buffer = deque(maxlen=100)

    def _should_trigger(self, message_text, chat_id):
        """Check if message should trigger the summary feature."""
        # Check if it's one of the target groups
        if chat_id not in self._target_group_ids:
            return False

        # Check if message contains any trigger patterns
        message_lower = message_text.lower()
        for pattern in self._trigger_patterns:
            if pattern.lower() in message_lower:
                return True

        return False

    def _store_message(self, message):
        """Store a message in the buffer for later summarization."""
        if message.chat_id in self._target_group_ids and message.text:
            # Store relevant message info
            user_name = message.from_user.username or message.from_user.first_name or "Usuário"
            message_data = {
                "user": user_name,
                "text": message.text,
                "timestamp": message.date
            }
            self._message_buffer.append(message_data)

    def _get_recent_messages(self, limit=100):
        """Get the last N messages from the buffer."""
        try:
            if not self._message_buffer:
                return ["[Nenhuma mensagem recente disponível]"]

            # Convert stored messages to text format for summarization
            messages = []
            for msg_data in list(self._message_buffer)[-limit:]:
                formatted_msg = f"{msg_data['user']}: {msg_data['text']}"
                messages.append(formatted_msg)

            return messages

        except Exception as e:
            logging.error(f"Error getting recent messages: {e}")
            return ["[Erro ao recuperar mensagens]"]

    def _summarize_messages(self, messages):
        """Use OpenAI to summarize the messages in Portuguese."""
        try:
            # Prepare the conversation context for OpenAI
            messages_text = "\n".join(messages)

            system_prompt = (
                "Você é um assistente que resume conversas em português brasileiro. "
                "Crie um resumo conciso e natural do que foi discutido, "
                "focando nos principais tópicos e pontos importantes. "
                "Mantenha o resumo breve e informativo."
            )

            user_prompt = f"Resuma esta conversa em português:\n\n{messages_text}"

            openai_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            summary = self._openai_client.make_request(
                messages=openai_messages,
                max_tokens=300
            )

            return summary.strip() if summary else "Não foi possível gerar um resumo."

        except Exception as e:
            logging.error(f"Error summarizing messages: {e}")
            return "Erro ao processar o resumo."

    def _process(self, update, context):
        """Process incoming messages and trigger summary if needed."""
        message = update.message
        if not message or not message.text:
            return

        chat_id = message.chat_id
        message_text = message.text

        # Always store messages from the target group for later summarization
        self._store_message(message)

        # Log the message for debugging
        user_info = f"({message.from_user.id}) {message.from_user.username or message.from_user.full_name}"
        logging.info(f"GroupSummary - chat: {chat_id} - user: {user_info} - text: {message_text}")

        # Check if this message should trigger the summary
        if not self._should_trigger(message_text, chat_id):
            return

        try:
            # Get recent messages from our buffer
            recent_messages = self._get_recent_messages()

            # Skip if we don't have enough messages
            if len(recent_messages) < 5:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="6️⃣ falam eim! Mas ainda não tenho mensagens suficientes para resumir.",
                    parse_mode=ParseMode.HTML
                )
                return

            # Generate summary
            summary = self._summarize_messages(recent_messages)

            # Send response
            response_text = f"6️⃣ falam eim! Foi falado: {summary}"

            context.bot.send_message(
                chat_id=chat_id,
                text=response_text,
                parse_mode=ParseMode.HTML
            )

        except Exception as e:
            logging.error(f"Error in GroupSummary._process: {e}")
            # Send error message
            context.bot.send_message(
                chat_id=chat_id,
                text="Ops! Não consegui processar o resumo agora.",
                parse_mode=ParseMode.HTML
            )

    def setup(self, dispatcher):
        """Setup the message handler."""
        message_handler = MessageHandler(
            Filters.text & Filters.group,
            self._process
        )
        dispatcher.add_handler(message_handler)
