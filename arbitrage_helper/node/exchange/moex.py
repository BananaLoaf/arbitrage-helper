import json

import requests

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class MOEX(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, security: str, trader_mode: bool = False):
        super().__init__(base, quote, trader_mode=trader_mode)
        self.security = security

    def parse(self):
        r = requests.get(f"https://iss.moex.com/cs/engines/currency/markets/selt/boardgroups/13/securities/{self.security}.hs?s1.type=candles&interval=24&candles=2")
        data = json.loads(r.text)

        if data := data["candles"][0]["data"]:
            self._buy_price = data[-1][4]  # TS, OHLC
            self._sell_price = data[-1][4]


class MOEX_EURRUB_TOD(MOEX):
    def __init__(self):
        super().__init__(base=Fiat.EUR, quote=Fiat.RUB, security="EUR_RUB__TOD")


class MOEX_USDRUB_TOD(MOEX):
    def __init__(self):
        super().__init__(base=Fiat.USD, quote=Fiat.RUB, security="USD000000TOD")
