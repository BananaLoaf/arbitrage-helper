from arbitrage_helper.currency import CEnum


class Stable(CEnum):
    USDT = "USDT"
    BUSD = "BUSD"
    USDC = "USDC"
    DAI = "DAI"
    MAI = "MAI"
    BIDR = "BIDR"
    IDRT = "IDRT"


class Crypto(CEnum):
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    DASH = "DASH"
    BCH = "BCH"
    BNB = "BNB"
    SHIB = "SHIB"
    DOGE = "DOGE"
