from concurrent.futures import ThreadPoolExecutor

from fairfruitbot_telegram import __version__
from fetchers import TarotFetcher


def test_version():
    assert __version__ == '0.1.0'


def test_fetch_all_tarot_cards():
    fetcher = TarotFetcher()
    total_cards = 22

    # make async requests using threadpool
    ThreadPoolExecutor(max_workers=total_cards).map(fetcher.fetch,
                                                    range(1, total_cards + 1))
