import difflib
from datetime import datetime


def force_format_timestamp(date):
    """
    Force format a timestamp to a date object.
    """
    formatted_date = None
    try:
        formatted_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    except ValueError:
        # stupid azure devops omitting .0 floating points
        formatted_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").date()

    return formatted_date


def get_date():
    return datetime.now().strftime("%d/%m/%Y")


def prepare_message(message):
    return (
        message.replace("-", "\\-")
        .replace(".", "\\.")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("=", "\\=")
        .replace("{", "\\{")
        .replace("}", "\\}")
        .replace("!", "\\!")
    )  # noqa


def parse_sign(sign):
    sign_map = {
        "aries": "Áries",
        "touro": "Touro",
        "gemeos": "Gêmeos",
        "cancer": "Câncer",
        "leao": "Leão",
        "virgem": "Virgem",
        "libra": "Libra",
        "escorpiao": "Escorpião",
        "sagitario": "Sagitário",
        "capricornio": "Capricórnio",
        "aquario": "Aquário",
        "peixes": "Peixes",
    }
    cutoff = 0.2
    default_sign = "aries"

    match = difflib.get_close_matches(sign, sign_map.keys(), n=1, cutoff=cutoff)
    if len(match) == 0:
        return default_sign

    return match[0]
