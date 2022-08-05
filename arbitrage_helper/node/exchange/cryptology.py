import json
import time

import requests

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class CryptologyExchange(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, trader_mode: bool = False):
        super().__init__(base, quote, trader_mode=trader_mode)

    def parse(self):
        timeout = 1

        while True:
            r = requests.get(f"https://api.cryptology.com/v1/public/get-order-book?trade_pair={str(self.base)}_{str(self.quote)}")
            data = json.loads(r.text)

            if book_data := data.get("data"):
                self._buy_price = float(book_data["asks"][0][0])
                self._sell_price = float(book_data["bids"][0][0])
            elif error_data := data.get("error"):
                if error_data["code"] == "TOO_MANY_REQUESTS":
                    time.sleep(timeout)
                    timeout *= 1.5
                    continue

            break
