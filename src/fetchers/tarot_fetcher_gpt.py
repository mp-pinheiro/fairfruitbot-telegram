import random
from datetime import datetime, timedelta

from clients import OpenAIClient
from fetchers import TarotFetcher, SignFetcherGPT
from modules import AstroModule


class TarotFetcherGPT(TarotFetcher):
    TAROT_SYSTEM_PROMPT = (
        "Você é um místico tarólogo com personalidade única, especializado em leituras de tarô. "
        "Sua abordagem é mais esotérica e simbólica que astrológica. Hoje é {today}. "
        "Use linguagem poética, misteriosa e envolvente, com metáforas ligadas ao simbolismo das cartas. "
        "Seja dramático quando necessário, use elementos como 'véus do mistério', 'sussurros do destino', "
        "'energias ancestrais', 'portais do tempo'. Varie entre tons solenes, brincalhões, enigmáticos ou "
        "irreverentes dependendo da carta. As energias cósmicas são: {planets} - use-as como inspiração "
        "sutil, não como foco principal. Cada previsão deve ter uma personalidade única e imprevisível. "
        "Crie narrativas que soem como profecias ou revelações místicas, não conselhos astrológicos. "
        "Seja mais teatral e menos científico que um astrólogo. Use linguagem coloquial misturada com "
        "misticismo - como um oráculo moderno que fala gírias."
    )

    TAROT_PERSONAS = [
        "sábio ancestral que sussurra segredos",
        "oráculo irreverente e moderno",
        "vidente dramático e teatral",
        "místico brincalhão e enigmático",
        "profeta urbano com linguagem de rua",
        "bruxa contemporânea e perspicaz",
    ]

    TAROT_STYLES = [
        "tom de suspense e mistério",
        "estilo de conversa íntima e conspiratorial",
        "linguagem de conto de fadas sombrio",
        "narrativa de filme noir místico",
        "prosa poética e envolvente",
        "estilo de podcast sobrenatural",
    ]

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

        # tarot prediction with randomized style
        now = now.isoformat()
        results = self._astro.get_astro_for_signs(now)

        # Add randomization for more variety
        tarot_reader = random.choice(self.TAROT_PERSONAS)
        narrative_style = random.choice(self.TAROT_STYLES)

        # Extract character names from Persona game data for subtle references
        persona_characters = []
        for arcana_data in arcanas:
            for character in arcana_data.get("characters", []):
                persona_characters.append(character["name"])
        characters_text = ", ".join(persona_characters) if persona_characters else "nenhum"

        system_prompt = self.TAROT_SYSTEM_PROMPT.format(today=today, planets=results)
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Escreva uma previsão de tarô para a carta: '{card}' como um {tarot_reader}, usando {narrative_style}. "
                "Responda em um único parágrafo. Use seus conhecimentos de tarô e simbolismo das cartas. "
                "Seja místico e envolvente, use metáforas esotéricas, elementos sobrenaturais, sem clichês banais. "
                "Seja enigmático, evite previsões óbvias. Mergulhe no simbolismo da carta. Não comece com frases "
                "genéricas como 'a carta revela', 'o tarô mostra'. Vá direto ao ponto com linguagem poética e "
                "misteriosa. Garanta que o texto seja atemporal e que cada previsão tenha uma voz completamente "
                f"diferente. Se apropriado, faça referências sutis aos personagens: {characters_text}. "
                "Faça revelações ousadas e específicas sobre o futuro, como se fosse uma visão mística real. "
                "A carta deve ser o centro da revelação. Seja profético, não apenas conselheiro. Ouse nas profecias. "
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
