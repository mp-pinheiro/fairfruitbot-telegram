from unittest.mock import Mock

from commands import Sign
from fetchers import SignFetcher


def test_sign_fetch():
    sign = 'aries'
    fetcher = SignFetcher()
    data = fetcher.fetch(sign)

    assert data['sign'] == sign
    assert data[
        'image'] == 'https://joaobidu.com.br/static/img/ico-aries.png'  # noqa
    assert data[
        'url'] == 'https://joaobidu.com.br/horoscopo/signos/previsao-aries'  # noqa
    assert data['prediction']
    assert data['guess_of_the_day']
    assert data['color_of_the_day']


def test_sign_command():
    tarot = Sign()

    update = Mock()

    context = Mock()
    context.bot.send_message = Mock()
    context.args = ['aries']

    tarot._process(update, context)

    assert context.bot.send_message.called
