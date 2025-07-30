from clients import OpenAIClient
from fetchers import Fetcher, SalmoFetcher


class SalmoFetcherGPT(Fetcher):
    def __init__(self):
        super().__init__()
        self._client = OpenAIClient()
        self._base_fetcher = SalmoFetcher()

    def _extract_key_verse(self, psalm_content, psalm_title):
        """use OpenAI to extract the most important verse from the psalm"""
        system_prompt = (
            "Você é um especialista em textos bíblicos e espiritualidade. Sua tarefa é identificar "
            "o versículo mais importante e impactante de um salmo completo. Escolha o versículo que "
            "melhor representa a essência e mensagem central do salmo. Responda apenas com o versículo "
            "escolhido, sem explicações adicionais."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": f"Do seguinte salmo '{psalm_title}', extraia o versículo mais importante:\n\n{psalm_content}"
            }
        ]
        
        return self._client.make_request(messages)

    def fetch(self):
        # get psalm data from base fetcher
        psalm_data = self._base_fetcher.fetch()
        
        # extract key verse using AI
        key_verse = self._extract_key_verse(psalm_data["content"], psalm_data["title"])
        psalm_data["key_verse"] = key_verse
        
        return psalm_data