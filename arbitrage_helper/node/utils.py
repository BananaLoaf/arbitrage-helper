from typing import *

from arbitrage_helper.balance import Balance
from arbitrage_helper.currency import *
from arbitrage_helper.node.generic import GenericNode


class FixedRate(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum,
                 buy_price: Optional[float] = None, sell_price: Optional[float] = None,
                 name: str = "FixedRate"):
        super().__init__(base, quote)
        self.name = name
        if buy_price is not None:
            self._buy_price = buy_price
        if sell_price is not None:
            self._sell_price = sell_price

    @property
    def repr(self):
        return f"{self.name} {self.base.repr}/{self.quote.repr}"

    def parse(self):
        pass


class PercFee(GenericNode):
    def __init__(self, fee_perc: float = 0.0, name: str = "PercFee"):
        super().__init__(base=Fiat.NONE, quote=Fiat.NONE)
        self.fee_perc = fee_perc
        self.name = name

    @property
    def repr(self):
        return f"{self.name} {self.fee_perc}%"

    @property
    def invalid(self):
        return False

    def parse(self):
        pass

    def exchange(self, balance: Balance) -> Balance:
        return Balance(balance.value * (100 - self.fee_perc) / 100, currency=balance.currency)


class FixedFee(GenericNode):
    def __init__(self, currency: CEnum, fee_value: float = 0.0, name: str = "FixedFee"):
        super().__init__(base=currency, quote=currency)
        self.fee_value = fee_value
        self.name = name

    @property
    def repr(self):
        return f"{self.name} {self.fee_value} {self.base.repr}"

    @property
    def invalid(self):
        return False

    def parse(self):
        pass

    def exchange(self, balance: Balance) -> Balance:
        return Balance(balance.value - self.fee_value, currency=balance.currency)
