from datetime import datetime, timedelta

from fetchers import SignFetcherGPT, TarotFetcherGPT
from modules import Singleton


class PredictionModule(metaclass=Singleton):
    def __init__(self):
        self._users = {}
        self._fetchers = {
            "sign": SignFetcherGPT(),
            "tarot": TarotFetcherGPT(),
        }
        self._predictions = {
            "sign": {},
            "tarot": {},
        }

    def _make_prediction(self, module, **kwargs):
        if module not in self._fetchers:
            raise ValueError(f"Module '{module}' not found")

        brt_offset = timedelta(hours=-3)
        date = datetime.utcnow() + brt_offset
        date = date.date()
        fetcher = self._fetchers[module]
        data = fetcher.fetch(**kwargs)
        data["date"] = date

        return data

    def _is_expired(self, request_date):
        brt_offset = timedelta(hours=-3)
        now_utc = datetime.utcnow()
        now_brt = now_utc + brt_offset
        now_brt = now_brt.date()

        return now_brt > request_date

    def _get_prediction(self, prediction_type, cache_key, **kwargs):
        prediction = self._predictions[prediction_type].get(cache_key, None)
        if not prediction or self._is_expired(prediction["date"]):
            prediction = self._make_prediction(prediction_type, **kwargs)

        self._predictions[prediction_type][cache_key] = prediction
        return prediction

    def get_sign_prediction(self, sign):
        return self._get_prediction("sign", sign, sign=sign)

    def get_tarot_prediction(self, card):
        return self._get_prediction("tarot", card, card=card)
