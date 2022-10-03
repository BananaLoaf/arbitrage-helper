from arbitrage_helper.currency import CEnum


class Fiat(CEnum):
    NONE = None
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    RUB = "RUB"
    KZT = "KZT"
    IDR = "IDR"
    UZS = "UZS"
    TJS = "TJS"
    CNY = "CNY"


# class TinkoffBank(CEnum):
#     RUB = "RUB"
#     KZT = "KZT"
#     IDR = "IDR"
#     USD = "USD"
#     EUR = "EUR"
#     GBP = "GBP"
#
#
# class PermataBank(CEnum):
#     IDR = "IDR"


class BinanceFiat(CEnum):
    RUB = "RUB"
    KZT = "KZT"
    USD = "USD"
    EUR = "EUR"
    IDR = "IDR"
    GBP = "GBP"


class VexelFiat(CEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class AdvCashFiat(CEnum):
    RUB = "RUB"
    EUR = "EUR"
