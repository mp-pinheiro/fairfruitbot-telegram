import logging
from telegram.constants import ParseMode
from telegram.ext import MessageHandler, Filters

from clients import OpenAIClient
from modules import Singleton
from environment import Environment
from messaging import get_shared_message_buffer, PrivacyManager


class GroupSummary(metaclass=Singleton):
    def __init__(self):
        self._env = Environment()
        self._target_group_ids = set(self._env.summary_group_ids)
        self._trigger_patterns = ["6 falam", "vcs falam", "ces falam", "6️⃣"]
        self._openai_client = OpenAIClient()
        # use shared message buffer instance
        self._message_buffer = get_shared_message_buffer()
        # privacy manager for anonymizing usernames in LLM calls
        self._privacy_manager = PrivacyManager()

    def _should_trigger(self, message_text, chat_id):
        # check if it's one of the target groups
        if chat_id not in self._target_group_ids:
            return False

        # check if message contains any trigger patterns
        message_lower = message_text.lower()
        for pattern in self._trigger_patterns:
            if pattern.lower() in message_lower:
                return True

        return False

    def _store_message(self, message):
        """Store message data using shared buffer"""
        try:
            return self._message_buffer.store_message(message, self._target_group_ids)
        except Exception as e:
            logging.error(f"Failed to store message: {e}")
            # re-raise to let caller know storage failed
            raise

    def _get_recent_messages(self, limit=100):
        try:
            # Use shared buffer to get recent messages, filtered to exclude trigger patterns
            def filter_non_triggers(msg_data):
                message_text = msg_data["text"].lower()
                return not any(
                    pattern.lower() in message_text
                    for pattern in self._trigger_patterns
                )
                
            filtered_messages = self._message_buffer.get_recent_messages(
                limit=limit, 
                filter_func=filter_non_triggers
            )
            
            if not filtered_messages:
                return [], []

            # separate usernames and message texts for privacy processing
            usernames = set()
            message_texts = []
            formatted_messages = []
            
            for msg_data in filtered_messages:
                username = msg_data['user']
                text = msg_data['text']
                usernames.add(username)
                message_texts.append(text)
                # Store the original format for later anonymization
                formatted_messages.append((username, text))

            return formatted_messages, message_texts

        except Exception as e:
            logging.error(f"Error getting recent messages: {e}")
            return [], []

    def _summarize_messages(self, formatted_messages, message_texts):
        try:
            if not formatted_messages:
                return "Não foi possível gerar um resumo."
                
            # Extract usernames for privacy session
            usernames = {username for username, _ in formatted_messages}
            
            # Use privacy session for secure anonymization
            with self._privacy_manager.create_privacy_session(usernames, message_texts) as session:
                # anonymize messages for LLM call
                anonymized_messages = []
                for username, text in formatted_messages:
                    anonymous_username = session.get_anonymous_username(username)
                    # also anonymize any usernames mentioned in text content
                    anonymous_text = session.anonymize_text(text)
                    formatted_msg = f"{anonymous_username}: {anonymous_text}"
                    anonymized_messages.append(formatted_msg)
                
                # prepare the conversation context for OpenAI
                messages_text = "\n".join(anonymized_messages)

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

                # deanonymize the response to restore real usernames
                if summary:
                    summary = session.deanonymize_text(summary)

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

        # log the message for debugging - do this first to ensure logging happens
        try:
            user_info = f"({message.from_user.id}) {message.from_user.username or message.from_user.full_name}"
            logging.info(
                f"GroupSummary - chat: {chat_id} - user: {user_info} - text: {message_text}"
            )
        except Exception:
            logging.info(f"GroupSummary - chat: {chat_id} - text: {message_text}")

        # always store messages from the target group for later summarization
        try:
            self._store_message(message)
        except Exception as e:
            logging.error(f"GroupSummary processing stopped due to storage failure: {e}")
            return

        # check if this message should trigger the summary
        if not self._should_trigger(message_text, chat_id):
            return

        try:
            # get recent messages from our buffer
            formatted_messages, message_texts = self._get_recent_messages()

            # skip if we don't have enough messages
            if len(formatted_messages) < 5:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="6️⃣ falam eim! Mas ainda não tenho mensagens suficientes para resumir.",
                    parse_mode=ParseMode.HTML,
                )
                return

            # generate summary
            summary = self._summarize_messages(formatted_messages, message_texts)

            # send response
            response_text = (
                f"6️⃣ falam eim!\n\n{summary}\n\nResumo gerado por Bidu-GPT."
            )

            context.bot.send_message(
                chat_id=chat_id, text=response_text, parse_mode=ParseMode.HTML
            )

        except Exception as e:
            logging.error(f"Error in GroupSummary._process: {e}")
            # send error message
            context.bot.send_message(
                chat_id=chat_id,
                text="Ops! Não consegui processar o resumo agora.",
                parse_mode=ParseMode.HTML,
            )

    def setup(self, dispatcher):
        message_handler = MessageHandler(Filters.text & Filters.group, self._process)
        dispatcher.add_handler(message_handler)
