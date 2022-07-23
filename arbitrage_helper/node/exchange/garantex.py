import json

import requests

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class GarantexExchange(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, trader_mode: bool = False):
        super().__init__(base, quote, trader_mode=trader_mode)

    def parse(self):
        pair = f"{self.base}{self.quote}".lower()
        r = requests.get(f"https://garantex.io/api/v2/depth?market={pair}")
        data = json.loads(r.text)

        if data.get("error") is None:
            self._buy_price = float(data["asks"][0]["price"])
            self._sell_price = float(data["bids"][0]["price"])
