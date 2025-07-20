import random
from datetime import datetime, timedelta

from clients import OpenAIClient
from fetchers import Fetcher
from modules import AstroModule


class SignFetcherGPT(Fetcher):
    MODEL_SYSTEM_PROMPT = (
        "Você é um tarólogo e astrólogo responsável por escrever horóscopos e tarôs para um site de astrologia. "
        "Mostre conhecimento astrológico e de tarologia, especialmente usando a data de hoje: {today}. "
        "Se for mencionar o dia, use o formato 'segunda-feira', 'terça-feira', 'segunda', hoje', 'amanhã', 'ontem'. "
        "Use termos coloquais como 'segundou', 'terçou', 'sextou' de forma totalmente irônica, para trazer mais "
        "proximidade com o leitor. Seja criativo e não use esses exatos termos, mas sim variações. Lembre-se que "
        "várias previsões serão feitas, uma para cada signo, então termos variados são importantes para não "
        "repetir o mesmo 'segundou' várias vezes. As posições dos planetas e estrelas são: {planets}, use-as "
        "com parcimônia, **sem** sobrecarregar o texto com informações astronômicas. Seja criativo e use-as de forma "
        "sutil e natural. Não use uma estrutura fixa (exemplo: primeiro planetas, depois amor, depois trabalho, etc). "
        "Inclua outros temas, mude a ordem, crie previsões diferenciadas e com personalidade. Crie narrativas "
        "envolventes e interessantes. Faça previsões ousadas, chute mesmo. Seja impessoal, sem nomes ou lugares. "
    )
    PREDICTION_SIZE_CHARS = 420

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
                "seus conhecimentos. Seja engraçado e preciso, use metáforas, figuras de linguagem, sem clichês. "
                "Seja claro, evite ambiguidades. Arrisque, seja sinistro. Não comece com 'signo', 'hoje', 'o signo', "
                "ou outros inícios genéricos. Garanta que o texto seja atemporal, e que as previsões sejam sempre bem "
                "diferentes umas das outras. "
                "Faça previsões arriscadas, seja o menos genérico possível. Seja muito ousado, dê conselhos e futuro "
                "com exatidão (ex: 'você vai ganhar na loteria'), de forma unica e vidente, e sempre criativo, pra "
                "garantir que a previsão seja incrível. O signo deve ter um papel central na previsão. A previsão deve "
                "obrigatoriamente ter uma previsão de futuro específica baseada nos termos acima. Extrapole nos chutes."
                f"Responda em aproximadamente {SignFetcherGPT.PREDICTION_SIZE_CHARS} caracteres (20% mais ou menos)",
            },
        ]
        horoscope = self._client.make_request(messages)

        # guess of the day
        guesses = []
        while len(guesses) < 3:
            guess = random.randint(1, 99)
            if guess not in guesses:
                guesses.append(guess)
        guesses = sorted(guesses)
        guess_of_the_day = ", ".join([f"{guess}" for guess in guesses])
        guess_of_the_day = f"{guess_of_the_day}."

        # color of the day
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Responda com uma única palavra para uma cor, sem formatação. Use cores criativas e "
                f"inusitadas, evite cores simples como apenas 'Vermelho' ou 'Azul'. Baseie-se na previsão: '{horoscope}'. ",
            },
        ]
        color_of_the_day = f"{self._client.make_request(messages)}"

        return {
            "prediction": horoscope,
            "guess_of_the_day": guess_of_the_day,
            "color_of_the_day": color_of_the_day,
        }

    def fetch(self, sign):
        data = self._fetch(sign)
        data["sign"] = sign
        data["image"] = self._image_url.format(sign=sign)

        return data
