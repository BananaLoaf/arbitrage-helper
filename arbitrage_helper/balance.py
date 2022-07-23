from arbitrage_helper.currency import CEnum


class Balance:
    def __init__(self, value: float, currency: CEnum):
        self._value = value
        self._currency = currency

    @property
    def value(self):
        return self._value

    @property
    def currency(self):
        return self._currency

    def __repr__(self) -> str:
        return f"{self.value} {self.currency.repr}"

    def __add__(self, other):
        assert self.currency == other.currency
        return Balance(value=self.value + other.value, currency=self.currency)

    def __sub__(self, other):
        assert self.currency == other.currency
        return Balance(value=self.value - other.value, currency=self.currency)

    def __eq__(self, other):
        return self.value == other.value and self.currency == other.currency

    def __truediv__(self, other):
        assert self.currency == other.currency
        return self.value / other.value