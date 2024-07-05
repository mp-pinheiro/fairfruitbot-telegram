from datetime import datetime, timedelta

from clients import OpenAIClient
from fetchers import Fetcher
from modules import AstroModule


class SignFetcherGPT(Fetcher):
    MODEL_SYSTEM_PROMPT = (
        "Você é um astrólogo profissional responsável por escrever horóscopos e tarôs para um site de astrologia. "
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
    PREDICTION_SIZE_CHARS = 425

    def __init__(self):
        super().__init__()
        self._image_url = "https://joaobidu.com.br/static/img/ico-{sign}.png"  # noqa
        self._client = OpenAIClient()
        self._astro = AstroModule()

    def _fetch(self, sign):
        now = datetime.utcnow() - timedelta(hours=3)
        today = now.strftime("%Y-%m-%d %H:%M:%S - %A")

        # planets
        now = now.isoformat()
        results = self._astro.get_astro_for_signs(now)

        # horoscope prediction
        system_prompt = SignFetcherGPT.MODEL_SYSTEM_PROMPT.format(today=today, planets=results)
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Escreva um horóscopo para o signo de {sign}. Responda em um único parágrafo. Use seus "
                "conhecimentos astrológicos. Seja consistente, fale de amor, vida, trabalho, saúde, dinheiro, etc. "
                "no meio do texto. Não hesite em fazer previsões neutras ou negativas, seja realista, a vida das "
                "pessoas não é sempre positiva. Não use palavras negativas como 'não', 'nunca', 'nada', 'ninguém',"
                " 'nenhum'. Use palavras positivas como 'se', 'quando', 'pode', 'possível', 'talvez'. Seja "
                "específico, evite generalizações. Seja criativo, evite clichês. Seja claro, evite ambiguidades. "
                "Seja criativo no uso de metáforas e figuras de linguagem. Evite começar com 'Signo,' ou 'Previsão'. "
                "Seja conciso, evite redundâncias. "
                f"Responda em no máximo {SignFetcherGPT.PREDICTION_SIZE_CHARS} caracteres.",
            },
        ]
        horoscope = self._client.make_request(messages)

        # guess of the day
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Qual é o palpite do dia para o signo de {sign}? Responda com três números no formato "
                "'X, Y e Z' e apenas isso. Use suas habilidades astrológicas. Seja conciso, evite redundâncias. "
                "Use suas habilidades astrológicas. Seja conciso, evite redundâncias. Use como base o seguinte "
                f"horóscopo: {horoscope}.",
            },
        ]
        guess_of_the_day = self._client.make_request(messages)

        # color of the day
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Qual é a cor do dia para o signo de {sign}? Responda com uma única palavra. "
                "Use cores criativas, evite cores simples como apenas 'vermelho' ou 'amarelo'. Use suas "
                "habilidades astrológicas. Seja conciso, evite redundâncias. Use como base o seguinte horóscopo: "
                f"{horoscope} e a seguinte previsão: {guess_of_the_day}.",
            },
        ]

        return {
            "prediction": horoscope,
            "guess_of_the_day": guess_of_the_day,
            "color_of_the_day": self._client.make_request(messages),
        }

    def fetch(self, sign):
        data = self._fetch(sign)
        data["sign"] = sign
        data["image"] = self._image_url.format(sign=sign)

        return data
