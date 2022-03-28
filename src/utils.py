from datetime import datetime


def force_format_timestamp(date):
    """
    Force format a timestamp to a date object.
    """
    formatted_date = None
    try:
        formatted_date = datetime.datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    except ValueError:
        # stupid azure devops omitting .0 floating points
        formatted_date = datetime.datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%SZ").date()

    return formatted_date


def get_date():
    return datetime.now().strftime('%d/%m/%Y')


def prepare_message(message):
    return message.replace("-", "\-") \
                  .replace(".", "\.") \
                  .replace("(", "\(") \
                  .replace(")", "\)") \
                  .replace("=", "\=") \
                  .replace("{", "\{") \
                  .replace("}", "\}") \
                  .replace("!", "\!") # noqa
