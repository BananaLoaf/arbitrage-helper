from typing import *
import requests
import json

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class Paysera(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, base_amount: int):
        super().__init__(base, quote, trader_mode=False)
        self.base_amount = base_amount

    @property
    def repr(self):
        return f"{super().repr} AMT:{self.base_amount}"

    def parse(self):
        self._buy_price = self._parse_buy_price()
        self._sell_price = self._parse_sell_price()
        pass

    def _parse_buy_price(self):
        r = requests.get(f"https://bank.paysera.com/lt/currency-exchange/rest/convert?clientType=natural&to_amount={self.base_amount}&from_currency[]={str(self.quote)}&providers[]=commercial&to_currency[]={str(self.base)}")
        from_amount = float(json.loads(r.text)["rates"][0]["from_amount"])
        return round(from_amount / self.base_amount, 8)

    def _parse_sell_price(self):
        r = requests.get(f"https://bank.paysera.com/lt/currency-exchange/rest/convert?clientType=natural&from_amount={self.base_amount}&from_currency[]={str(self.base)}&providers[]=commercial&to_currency[]={str(self.quote)}")
        to_amount = float(json.loads(r.text)["rates"][0]["to_amount"])
        return round(to_amount / self.base_amount, 8)
