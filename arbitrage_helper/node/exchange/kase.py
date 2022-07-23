from urllib.request import urlopen

from lxml import etree

from arbitrage_helper.node.generic import GenericNode
from arbitrage_helper.currency import *


class KASE(GenericNode):
    def __init__(self, base: CEnum, quote: CEnum, security: str):
        super().__init__(base, quote, trader_mode=False)
        self.security = security

    def bid_xpath(self, security: str) -> str:
        return self._circle_xpath(security=security) + " | " + self._table_bid_xpath(security=security)

    def ask_xpath(self, security: str) -> str:
        return self._circle_xpath(security=security) + " | " + self._table_ask_xpath(security=security)

    def _circle_xpath(self, security: str) -> str:
        return f"//span[@class=\"currency-round\"][span[contains(text(),\"{security}\")]]/span[1]/span[1]"  # get from circle

    def _table_bid_xpath(self, security: str) -> str:
        xpath = "//table/tbody/tr"
        xpath += f"[td[a[contains(text(),\"{security}\")]]]"  # td/a with needed security USDKZT_TOM
        xpath += "[td[8][not(contains(text(),\"–\"))]]"  # bid not empty
        xpath += "[td[9][not(contains(text(),\"–\"))]]"  # ask not empty
        xpath += "/td[8]"  # get bid
        return xpath

    def _table_ask_xpath(self, security: str) -> str:
        xpath = "//table/tbody/tr"
        xpath += f"[td[a[contains(text(),\"{security}\")]]]"  # td/a with needed security USDKZT_TOM
        xpath += "[td[8][not(contains(text(),\"–\"))]]"  # bid not empty
        xpath += "[td[9][not(contains(text(),\"–\"))]]"  # ask not empty
        xpath += "/td[9]"  # get ask
        return xpath

    def parse(self):
        r = urlopen("https://kase.kz/en/currency/")
        tree = etree.parse(r, etree.HTMLParser())

        buy_elems = tree.xpath(self._table_bid_xpath(security=self.security)) + \
                    tree.xpath(self._circle_xpath(security=self.security))
        self._buy_price = float(buy_elems[0].text.replace(",", "."))

        sell_elems = tree.xpath(self._table_ask_xpath(security=self.security)) + \
                     tree.xpath(self._circle_xpath(security=self.security))
        self._sell_price = float(sell_elems[0].text.replace(",", "."))


class KASE_EURKZT(KASE):
    def __init__(self):
        super().__init__(base=Fiat.EUR, quote=Fiat.KZT, security="EURKZT_TOM")


class KASE_EURUSD(KASE):
    def __init__(self):
        super().__init__(base=Fiat.EUR, quote=Fiat.USD, security="EURUSD_TOM")


class KASE_RUBKZT(KASE):
    def __init__(self):
        super().__init__(base=Fiat.RUB, quote=Fiat.KZT, security="RUBKZT_TOM")


class KASE_USDKZT(KASE):
    def __init__(self):
        super().__init__(base=Fiat.USD, quote=Fiat.KZT, security="USDKZT_TOM")
