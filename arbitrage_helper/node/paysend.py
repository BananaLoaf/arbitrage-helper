import json
import requests

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class GenericPaysend(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, url: str):
        super().__init__(base, quote, trader_mode=False)
        self.url = url

    def parse(self):
        r = requests.post(self.url)
        res = json.loads(r.text)

        self._sell_price = res["commission"]["convertRate"]


class Paysend_KZTIDR(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.KZT, quote=Fiat.IDR, url="https://paysend.ru/api/ru-ru/otpravit-dengi/iz-kazahstana-v-indoneziyu?fromCurrId=398&toCurrId=360&isFrom=true")


class Paysend_KZTUSD_KZ(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.KZT, quote=Fiat.USD, url="https://paysend.ru/api/ru-ru/otpravit-dengi/iz-kazahstana-v-kazahstan?fromCurrId=398&toCurrId=840&isFrom=true")


class Paysend_RUBUZS(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.RUB, quote=Fiat.UZS, url="https://paysend.ru/api/ru-ru/otpravit-dengi/iz-rossii-v-uzbekistan?fromCurrId=643&toCurrId=860&isFrom=true")


class Paysend_RUBTJS(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.RUB, quote=Fiat.TJS, url="https://paysend.ru/api/ru-ru/otpravit-dengi/iz-rossii-v-tadzhikistan?fromCurrId=643&toCurrId=972&isFrom=true")


class Paysend_UZSKZT(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.UZS, quote=Fiat.KZT, url="https://paysend.ru/api/ru-ru/otpravit-dengi/iz-uzbekistana-v-kazahstan?fromCurrId=860&toCurrId=398&isFrom=true")


class Paysend_UZSUSD_KZ(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.UZS, quote=Fiat.USD, url="https://paysend.ru/api/ru-ru/otpravit-dengi/iz-uzbekistana-v-kazahstan?fromCurrId=860&toCurrId=840&isFrom=true")
