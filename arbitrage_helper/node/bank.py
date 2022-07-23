import requests
import json

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import CEnum


################################################################
class Tinkoff(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum):
        super().__init__(base, quote, trader_mode=False)

    def parse(self):
        r = requests.get(f"https://api.tinkoff.ru/v1/currency_rates?from={str(self.base)}&to={str(self.quote)}")
        res = json.loads(r.text)

        rate = next(filter(lambda x: x["category"] == "DebitCardsOperations", res["payload"]["rates"]))

        self._buy_price = rate["sell"]
        self._sell_price = rate["buy"]


################################################################
class Jusan(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum):
        super().__init__(base, quote, trader_mode=False)

    def parse(self):
        r = requests.get(f"https://jusan.kz/banking/v1/currency/exchange")
        res = json.loads(r.text)

        for rate in res:
            if rate["currencyFrom"] == str(self.base) and rate["currencyTo"] == str(self.quote):
                self._buy_price = rate["buyingSum"]
                self._sell_price = rate["saleSum"]
                break


################################################################
class Vexel(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum):
        super().__init__(base, quote, trader_mode=False)

    def parse(self):
        r = requests.post(f"https://vexel.online/api/v2/info",
                          json={"from": str(self.quote), "to": str(self.base),
                                "amount": "1", "information": "getExchangeRate"})
        if data := json.loads(r.text)["data"]:
            self._buy_price = 1/float(data["rate"])

        r = requests.post(f"https://vexel.online/api/v2/info",
                          json={"from": str(self.base), "to": str(self.quote),
                                "amount": "1", "information": "getExchangeRate"})
        if data := json.loads(r.text)["data"]:
            self._sell_price = float(data["rate"])
