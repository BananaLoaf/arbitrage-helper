from typing import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decouple import config

from arbitrage_helper.balance import Balance
from arbitrage_helper.currency import *


class GenericNode:
    _buy_price = 9223372036854775807  # I buy, someone sells to me, min price - 40000, ask
    _sell_price = 0  # I sell, someone buys from me, max price - 39000, bid

    def __init__(self, base: CEnum, quote: CEnum, trader_mode: bool = False):
        self.trader_mode = trader_mode

        self._base = base  # BTC
        self._quote = quote  # USD

    def get_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("window-size=1920,1080")
        driver = webdriver.Chrome(config("DRIVER_PATH"), options=chrome_options)
        driver.maximize_window()
        # driver.fullscreen_window()
        return driver

    def parse(self):
        raise NotImplementedError

    @property
    def invalid(self):
        return self._buy_price == self.__class__._buy_price and self._sell_price == self.__class__._sell_price or self._buy_price == 0.0

    @property
    def buy_price(self) -> float:
        if self.trader_mode:
            return self._sell_price
        else:
            return self._buy_price

    @property
    def sell_price(self) -> float:
        if self.trader_mode:
            return self._buy_price
        else:
            return self._sell_price

    @property
    def repr(self):
        return f"{self.__class__.__name__} {self.base.repr}/{self.quote.repr}"

    @property
    def base(self) -> CEnum:
        return self._base

    @property
    def quote(self) -> CEnum:
        return self._quote

    def exchange(self, balance: Balance) -> Balance:
        assert balance.currency == self.base or balance.currency == self.quote, "Wrong currency"

        if balance.currency == self.base:
            return Balance(balance.value * self.sell_price, currency=self.quote)
        elif balance.currency == self.quote:
            return Balance(balance.value / self.buy_price, currency=self.base)

    def currency_convert(self, currency: CEnum) -> Optional[CEnum]:
        if currency == self.quote:
            return self.base
        elif currency == self.base:
            return self.quote
        else:
            return None
