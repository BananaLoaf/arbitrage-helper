from typing import *
import requests
import json
from enum import Enum

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class BPM(Enum):  # Binance Payment Method
    All = None
    Tinkoff = "Tinkoff"
    RosBank = "RosBank"
    RUBfiatbalance = "RUBfiatbalance"
    Paysend = "Paysend"
    Uzcard = "Uzcard"
    Humo = "Humo"
    Kapitalbank = "Kapitalbank"
    PermataMe = "PermataMe"
    BankTransfer = "BANK"
    HalykBank = "HalykBank"
    AltynBank = "AltynBank"
    JysanBank = "JysanBank"

    def __str__(self):
        return str(self.value)


class BinanceP2P(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, payment_method: Union[BPM, Iterable[BPM]],
                 custom_method_name: Optional[str] = None, trader_mode: bool = False, merchant_check: bool = False):
        super().__init__(base, quote, trader_mode)
        if isinstance(payment_method, BPM):
            self.payment_method = (payment_method, )
        else:
            self.payment_method = tuple(payment_method)
        self.custom_method_name = custom_method_name
        self.merchant_check = merchant_check

    @property
    def repr(self):
        if self.custom_method_name is not None:
            method_name = self.custom_method_name
        else:
            method_name = ','.join(map(str, self.payment_method))
        return f"BinanceP2P {method_name} {self.base.repr}/{self.quote.repr}"

    def parse(self):
        self._buy_price = self._parse_buy_price(base=self.base, quote=self.quote)
        self._sell_price = self._parse_sell_price(base=self.base, quote=self.quote)

    def _parse_price(self, json_data) -> Optional[float]:
        r = requests.post('https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search', json=json_data)
        if len((res := json.loads(r.text))["data"]) > 0:
            return float(res["data"][0]["adv"]["price"])
        else:
            return None

    def _parse_buy_price(self, base: CEnum, quote: CEnum):
        json_data = {
            "asset": str(base),
            "fiat": str(quote),
            "page": 1,
            "payTypes": [],
            "publisherType": None,
            "rows": 3,
            "tradeType": "BUY"
        }
        if self.payment_method != BPM.All:
            json_data["payTypes"] = [m.value for m in self.payment_method]
        if self.merchant_check:
            json_data["publisherType"] = "merchant"

        if (res := self._parse_price(json_data)) is None:
            return self.buy_price
        else:
            return res

    def _parse_sell_price(self, base: CEnum, quote: CEnum):
        json_data = {
            "asset": str(base),
            "fiat": str(quote),
            "page": 1,
            "payTypes": [],
            "publisherType": None,
            "rows": 3,
            "tradeType": "SELL"
        }
        if self.payment_method != BPM.All:
            json_data["payTypes"] = [m.value for m in self.payment_method]
        if self.merchant_check:
            json_data["publisherType"] = "merchant"

        if (res := self._parse_price(json_data)) is None:
            return self.sell_price
        else:
            return res
