from datetime import datetime, timedelta

from clients import OpenAIClient
from fetchers import TarotFetcher
from modules import AstroModule


class TarotFetcherGPT(TarotFetcher):
    MODEL_SYSTEM_PROMPT = (
        "Você é um tarólogo profissional responsável por escrever horóscopos e tarôs para um site de astrologia. "
        "Mostre conhecimento astrológico e de contexto, especialmente usando a data de hoje: {today}. "
        "Se for mencionar o dia, use o formato 'segunda-feira', 'terça-feira', 'segunda', hoje', 'amanhã', 'ontem'. "
        "Use termos coloquais como 'segundou', 'terçou', 'sextou' e outras coloquialidades. para trazer mais "
        "proximidade com o leitor. Seja criativo e não use esses exatos termos, mas sim variações. Lembre-se que "
        "várias previsões serão feitas, uma para cada signo. Então termos variados são importantes para não "
        "repetir o mesmo 'segundou' várias vezes. As posições dos planetas e estrelas são: {planets}, use-as "
        "com parcimônia, sem sobrecarregar o texto com informações astrológicas. Seja criativo e use-as de forma "
        "sutil e natural. Não use uma estrutura fixa (exemplo: primeiro planetas, depois amor, depois trabalho, etc). "
        "Inclua outros temas, mude a ordem, crie previsões diferenciadas e com personalidade. Crie narrativas "
        "envolventes e interessantes."
    )
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
        system_prompt = TarotFetcherGPT.MODEL_SYSTEM_PROMPT.format(today=today, planets=results)
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Escreva uma previsão de tarô para a carta: '{card}'. Responda em um único parágrafo. Use "
                "seus conhecimentos de tarô. Seja criativo, use metáforas e figuras de linguagem. Evite clichês. "
                "Seja claro, evite ambiguidades. Seja conciso, evite redundâncias. Não comece com 'hoje' ou 'a carta' "
                "ou outros inícios genéricos. garanta que o texto seja atemporal, e que as previsões sejam sempre bem "
                f"diferentes umas das outras. Sem mencionar diretamente Persona, use os dados: '{arcanas}'. "
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
