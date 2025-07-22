import os
import time

from click import UsageError
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, RateLimitError

load_dotenv()


class OpenAIClient:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_DEFAULT = os.getenv("OPENAI_MODEL_DEFAULT", "deepseek-reasoner")
    REQUEST_MAX_RETRIES = 12
    MAX_TOKENS = 200

    def __init__(self) -> None:
        try:
            self._client = OpenAI(api_key=OpenAIClient.OPENAI_API_KEY, base_url="https://api.deepseek.com")
        except OpenAIError:
            raise UsageError(
                "Could not initialize OpenAI client. Make sure you have the `OPENAI_API_KEY` environment variable set."
            )

    def make_request(self, messages, model=None, max_tokens=None):
        """Makes a translation request to OpenAI's API. You should use this
        with a fine-tuned model.

        Args:
            messages (list): List of messages with conversation context. Format:
                [
                    {
                        "role": "system",
                        "content": "You are a translator for the game Primateria.",
                    },
                    {
                        "role": "user",
                        "content": {"key": "{key}", "source": "{source_string}", "language": "{language}"}
                    }
                ]

        Returns:
            str: The translated text.
        """
        if model is None:
            model = OpenAIClient.MODEL_DEFAULT

        if max_tokens is None:
            max_tokens = OpenAIClient.MAX_TOKENS

        response = None
        retries = 0
        sleep_time = 1
        while response is None and retries < OpenAIClient.REQUEST_MAX_RETRIES:
            try:
                response = self._client.chat.completions.create(
                    model=model, messages=messages, stream=False, max_tokens=max_tokens
                )
            except RateLimitError:
                print(
                    "Rate limit exceeded. Waiting {sleep_time} seconds "
                    f"({retries}/{OpenAIClient.REQUEST_MAX_RETRIES} retries)."
                )
                time.sleep(sleep_time)
                sleep_time *= 2
                retries += 1

        if response is None:
            print("Request failed. Returning empty string.")
            return ""

        return response.choices[0].message.content
