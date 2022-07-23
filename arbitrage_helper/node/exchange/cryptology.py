import json

import requests

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class CryptologyExchange(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, trader_mode: bool = False):
        super().__init__(base, quote, trader_mode=trader_mode)

    def parse(self):
        r = requests.get(f"https://api.cryptology.com/v1/public/get-order-book?trade_pair={str(self.base)}_{str(self.quote)}")
        data = json.loads(r.text)

        if data := data["data"]:
            self._buy_price = float(data["asks"][0][0])
            self._sell_price = float(data["bids"][0][0])
        else:
            pass
