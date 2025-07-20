from datetime import datetime, timedelta

from clients import OpenAIClient
from fetchers import TarotFetcher, SignFetcherGPT
from modules import AstroModule


class TarotFetcherGPT(TarotFetcher):
    PREDICTION_SIZE_CHARS = 320

    def __init__(self):
        super().__init__()
        self._client = OpenAIClient()
        self._astro = AstroModule()

    def _fetch(self, card):
        now = datetime.utcnow() - timedelta(hours=3)
        today = now.strftime("%Y-%m-%d %H:%M:%S - %A")

        # persona info
        category = TarotFetcher.tarot_map[card]
        arcana_name = TarotFetcher.category_map[category]
        arcanas = self._arcanas[category].values()
        title = f"{card} ({arcana_name})"

        # tarot prediction
        now = now.isoformat()
        results = self._astro.get_astro_for_signs(now)
        system_prompt = SignFetcherGPT.MODEL_SYSTEM_PROMPT.format(today=today, planets=results)
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Escreva uma previsão de tarô para a carta: '{card}'. Responda em um único parágrafo. Use "
                "seus conhecimentos de tarô. Seja preciso e direto, use metáforas, figuras de linguagem, sem clichês. "
                "Seja claro, evite ambiguidades. Arrisque, seja sinistro. Não comece com 'hoje', 'a carta', 'o tarô', "
                "ou outros inícios genéricos. Garanta que o texto seja atemporal, e que as previsões sejam sempre bem "
                f"diferentes umas das outras. Sem mencionar diretamente Persona, use os dados: '{arcanas}'. "
                "Faça previsões arriscadas, seja o menos genérico possível. Seja muito ousado, dê conselhos e futuro "
                "com exatidão, de forma única e vidente, e sempre criativa, pra que a previsão seja incrível. A carta "
                "deve ter um papel central na previsão. A previsão deve obrigatoriamente ter uma previsão de futuro "
                "específica baseada nos termos acima. Extrapole nos chutes. "
                f"Responda em aproximadamente {TarotFetcherGPT.PREDICTION_SIZE_CHARS} caracteres (20% mais ou menos)",
            },
        ]
        body = self._client.make_request(messages)

        # fetch image
        image = TarotFetcher.arcana_map[arcana_name]["url"]

        return {
            "title": title,
            "body": body,
            "image": image,
            "arcanas": arcanas,
        }

    def fetch(self, card):
        prediction = self._fetch(card)

        return {
            "title": prediction["title"],
            "body": prediction["body"],
            "image": prediction["image"],
            "arcanas": prediction["arcanas"],
        }
