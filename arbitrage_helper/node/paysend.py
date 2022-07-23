from urllib.request import urlopen
import time

from lxml import etree

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class GenericPaysend(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, link: str, quote_first: int = False):
        super().__init__(base, quote, trader_mode=False)
        self.link = link

        self.quote_first = quote_first

    def parse(self):
        r = urlopen(self.link)
        tree = etree.parse(r, etree.HTMLParser())
        sell_text = tree.xpath("/html[1]/body[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/span[1]") + tree.xpath("/html[1]/body[1]/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/span[1]")
        sell_text = sell_text[0].text

        self._sell_price = float(sell_text.split(" = ")[1].split(" ")[0])
        if self.quote_first:
            self._sell_price = 1 / self._sell_price


class Paysend_KZTIDR(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.KZT, quote=Fiat.IDR, link="https://paysend.com/ru-nl/otpravit-dengi/iz-kazahstana-v-indoneziyu")


class Paysend_RUBUZS(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.RUB, quote=Fiat.UZS, link="https://paysend.com/ru-nl/otpravit-dengi/iz-rossii-v-uzbekistan")


class Paysend_RUBTJS(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.RUB, quote=Fiat.TJS, link="https://paysend.com/ru-nl/otpravit-dengi/iz-rossii-v-tadzhikistan", quote_first=True)


class Paysend_UZSKZT(GenericPaysend):
    def __init__(self):
        super().__init__(base=Fiat.UZS, quote=Fiat.KZT, link="https://paysend.com/en-ru/send-money/from-uzbekistan-to-kazakhstan", quote_first=True)
