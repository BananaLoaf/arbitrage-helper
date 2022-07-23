import json

import requests

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class BinanceExchange(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, trader_mode: bool = False):
        super().__init__(base, quote, trader_mode=trader_mode)

    def parse(self):
        r = requests.get(f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={str(self.base)}{str(self.quote)}")
        data = json.loads(r.text)

        try:
            self._buy_price = float(data["askPrice"])
            self._sell_price = float(data["bidPrice"])
        except KeyError:
            pass
