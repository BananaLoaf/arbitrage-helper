import itertools

from arbitrage_helper.currency import *
from arbitrage_helper.node import *


class NodeHolder:
    def all_nodes(self, crypto: bool) -> dict[str, GenericNode]:
        nodes = []

        ################################################################
        # Crypto exchanges
        nodes += self.get_binance_spot(crypto=crypto)
        nodes += self.get_cryptology_spot(crypto=crypto)
        nodes += self.get_garantex(crypto=crypto)

        ################################################################
        # Exchanges
        nodes += self.get_moex()
        nodes += self.get_kase()

        ################################################################
        # Banks
        nodes += self.get_ru_tinkoff_bank()
        nodes += self.get_kz_freedom_finance_bank()
        nodes += self.get_jusan()
        nodes += self.get_vexel(crypto=crypto)
        nodes += self.get_vexel_utils()
        nodes += self.get_paysera()

        ################################################################
        # P2P
        # Russia
        main_methods = [
            BPM.Tinkoff,
            BPM.RosBank,
            BPM.RaiffeisenBankRussia,
            BPM.QIWI,
            BPM.PostBankRussia,
        ]
        minor_methods = [
            BPM.YandexMoney,
            BPM.ABank,
            BPM.MTSBank,
            BPM.HomeCreditBank,
            BPM.RenaissanceCredit,
            BPM.BankSaintPetersburg,
            BPM.RussianStandardBank,
        ]
        unusable_methods = [BPM.Payeer, BPM.Advcash]

        nodes += self.get_binance_p2p_russia(
            crypto=crypto,
            payment_method=main_methods,
            custom_method_name='MainBanks',
        )
        nodes += self.get_binance_p2p_russia(
            crypto=crypto,
            payment_method=minor_methods,
            custom_method_name='MinorBanks',
        )
        # nodes += self.get_binance_p2p_russia(
        #     crypto=crypto,
        #     payment_method=unusable_methods,
        # )

        for payment_method in main_methods + minor_methods:
            nodes += self.get_binance_p2p_russia(
                crypto=crypto,
                payment_method=payment_method,
            )

        # Kazakhstan
        nodes += self.get_binance_p2p_kazakhstan(
            crypto=crypto,
            payment_method=BPM.JysanBank,
        )

        # Indonesia
        for payment_method in [BPM.PermataMe, BPM.BankTransfer]:
            nodes += self.get_binance_p2p_indonesia(
                crypto=crypto,
                payment_method=payment_method,
            )

        # Uzbekistan
        uz_methods = [
            BPM.Paysend,
            BPM.Uzcard,
            BPM.Kapitalbank,
            BPM.Tinkoff,
            BPM.BankTransfer,
        ]
        for payment_method in uz_methods:
            nodes += self.get_binance_p2p_uzbekistan(
                crypto=crypto,
                payment_method=payment_method,
            )

        ################################################################
        nodes += self.get_paysend()

        return {node.repr: node for node in nodes}

    ################################################################
    # Crypto exchanges
    def get_binance_spot(self, crypto: bool) -> list[GenericNode]:
        nodes = [
            BinanceExchange(base=Stable.USDT, quote=Stable.DAI),
            # BinanceExchange(base=Stable.USDT, quote=Stable.USDT),
            BinanceExchange(base=Stable.USDT, quote=BinanceFiat.RUB),

            BinanceExchange(base=Stable.BUSD, quote=Stable.DAI),
            BinanceExchange(base=Stable.BUSD, quote=Stable.USDT),
            BinanceExchange(base=Stable.BUSD, quote=BinanceFiat.RUB),
        ]

        if crypto:
            nodes += [
                BinanceExchange(base=Crypto.BTC, quote=Stable.DAI),
                BinanceExchange(base=Crypto.BTC, quote=Stable.USDT),
                BinanceExchange(base=Crypto.BTC, quote=BinanceFiat.RUB),

                BinanceExchange(base=Crypto.ETH, quote=Stable.DAI),
                BinanceExchange(base=Crypto.ETH, quote=Stable.USDT),
                BinanceExchange(base=Crypto.ETH, quote=BinanceFiat.RUB),

                BinanceExchange(base=Crypto.BNB, quote=Stable.DAI),
                BinanceExchange(base=Crypto.BNB, quote=Stable.USDT),
                BinanceExchange(base=Crypto.BNB, quote=BinanceFiat.RUB),

                # BinanceExchange(base=Crypto.SHIB, quote=Stable.DAI),
                BinanceExchange(base=Crypto.SHIB, quote=Stable.USDT),
                # BinanceExchange(base=Crypto.SHIB, quote=BinanceFiat.RUB),

                # BinanceExchange(base=Crypto.DOGE, quote=Stable.DAI),
                BinanceExchange(base=Crypto.DOGE, quote=Stable.USDT),
                BinanceExchange(base=Crypto.DOGE, quote=BinanceFiat.RUB),
            ]

        return nodes

    def get_cryptology_spot(self, crypto: bool) -> list[GenericNode]:
        nodes = [
            CryptologyExchange(base=Stable.USDT, quote=Fiat.USD),
            CryptologyExchange(base=Stable.BUSD, quote=Fiat.EUR),
            CryptologyExchange(base=Stable.DAI, quote=Fiat.EUR),
            CryptologyExchange(base=Stable.USDC, quote=Fiat.EUR),
            CryptologyExchange(base=Stable.USDT, quote=Fiat.EUR),
            CryptologyExchange(base=Stable.BUSD, quote=Stable.USDT),
            CryptologyExchange(base=Stable.USDC, quote=Stable.USDT),
        ]

        if crypto:
            nodes += [
                CryptologyExchange(base=Crypto.BTC, quote=Fiat.USD),
                CryptologyExchange(base=Crypto.ETH, quote=Fiat.USD),
                CryptologyExchange(base=Crypto.SHIB, quote=Fiat.USD),
                CryptologyExchange(base=Crypto.BCH, quote=Fiat.USD),
                CryptologyExchange(base=Crypto.LTC, quote=Fiat.USD),

                CryptologyExchange(base=Crypto.BTC, quote=Fiat.EUR),
                CryptologyExchange(base=Crypto.ETH, quote=Fiat.EUR),
                CryptologyExchange(base=Crypto.BCH, quote=Fiat.EUR),
                CryptologyExchange(base=Crypto.LTC, quote=Fiat.EUR),

                CryptologyExchange(base=Crypto.BTC, quote=Stable.BUSD),

                CryptologyExchange(base=Crypto.BNB, quote=Stable.USDT),
                CryptologyExchange(base=Crypto.BTC, quote=Stable.USDT),
                CryptologyExchange(base=Crypto.SHIB, quote=Stable.USDT),
                CryptologyExchange(base=Crypto.BCH, quote=Stable.USDT),
                CryptologyExchange(base=Crypto.ETH, quote=Stable.USDT),
                CryptologyExchange(base=Crypto.LTC, quote=Stable.USDT),

                CryptologyExchange(base=Crypto.BTC, quote=Stable.DAI),

                CryptologyExchange(base=Crypto.BNB, quote=Stable.USDC),
                CryptologyExchange(base=Crypto.BTC, quote=Stable.USDC),
                CryptologyExchange(base=Crypto.ETH, quote=Stable.USDC),
                CryptologyExchange(base=Crypto.LTC, quote=Stable.USDC),
            ]

        return nodes

    def get_garantex(self, crypto: bool) -> list[GenericNode]:
        nodes = [
            GarantexExchange(base=Stable.USDT, quote=Fiat.RUB),
            GarantexExchange(base=Stable.DAI, quote=Fiat.RUB),
            GarantexExchange(base=Stable.USDC, quote=Fiat.RUB),
            GarantexExchange(base=Stable.USDC, quote=Stable.USDT),
        ]
        if crypto:
            nodes += [
                GarantexExchange(base=Crypto.BTC, quote=Fiat.RUB),
                GarantexExchange(base=Crypto.ETH, quote=Fiat.RUB),
                GarantexExchange(base=Crypto.BTC, quote=Stable.USDT),
                GarantexExchange(base=Crypto.ETH, quote=Crypto.BTC),
                GarantexExchange(base=Crypto.ETH, quote=Stable.USDT),
            ]
        return nodes

    ################################################################
    # Exchanges
    def get_moex(self) -> list[GenericNode]:
        return [
            MOEX_USDRUB_TOD(),
            MOEX_EURRUB_TOD(),
        ]

    def get_kase(self) -> list[GenericNode]:
        return [
            KASE_EURKZT(),
            KASE_EURUSD(),
            KASE_RUBKZT(),
            KASE_USDKZT(),
        ]

    ################################################################
    # Banks
    def get_ru_tinkoff_bank(self) -> list[GenericNode]:
        pairs = list(
            itertools.combinations(
                [Fiat.USD, Fiat.RUB, Fiat.EUR, Fiat.GBP, Fiat.UZS],
                2,
            ),
        )
        return [RUTinkoff(base=base, quote=quote) for base, quote in pairs]

    def get_kz_freedom_finance_bank(self) -> list[GenericNode]:
        return [
            KZFreedomFinance(base=Fiat.USD, quote=Fiat.RUB),
            KZFreedomFinance(base=Fiat.EUR, quote=Fiat.USD),
            KZFreedomFinance(base=Fiat.EUR, quote=Fiat.RUB),
            KZFreedomFinance(base=Fiat.RUB, quote=Fiat.KZT),
            KZFreedomFinance(base=Fiat.EUR, quote=Fiat.KZT),
        ]

    def get_jusan(self) -> list[GenericNode]:
        return [
            Jusan(base=Fiat.USD, quote=Fiat.KZT),
            Jusan(base=Fiat.RUB, quote=Fiat.KZT),
            Jusan(base=Fiat.EUR, quote=Fiat.KZT),
        ]

    def get_vexel(self, crypto: bool) -> list[GenericNode]:
        symbols = [
            VexelFiat.EUR,
            VexelFiat.USD,
            VexelFiat.RUB,
            Stable.USDT,
            Stable.USDC,
        ]
        if crypto:
            symbols += [Crypto.BTC, Crypto.ETH]

        return [
            Vexel(base=base, quote=quote)
            for base, quote in itertools.combinations(symbols, 2)
        ]

    def get_vexel_utils(self) -> list[GenericNode]:
        return [
            FixedRate(
                base=VexelFiat.RUB,
                quote=Fiat.RUB,
                buy_price=None,
                sell_price=0.98,
                name='Vexel2Card',
            ),
            FixedRate(
                base=VexelFiat.EUR,
                quote=Fiat.EUR,
                buy_price=1,
                sell_price=1,
                name='Vexel SWIFT/SEPA',
            ),
        ]

    def get_paysera(self) -> list[GenericNode]:
        return [
            Paysera(base=Fiat.RUB, quote=Fiat.KZT, base_amount=100000),
            Paysera(base=Fiat.USD, quote=Fiat.RUB, base_amount=1000),
            Paysera(base=Fiat.EUR, quote=Fiat.RUB, base_amount=1000),
            Paysera(base=Fiat.USD, quote=Fiat.EUR, base_amount=1000),
            Paysera(base=Fiat.USD, quote=Fiat.KZT, base_amount=1000),
            Paysera(base=Fiat.EUR, quote=Fiat.KZT, base_amount=1000),
        ]

    ################################################################
    # P2P Binance
    def get_binance_p2p_russia(
        self,
        crypto: bool,
        payment_method: Union[Iterable[BPM], BPM],
        custom_method_name: Optional[str] = None,
    ) -> list[GenericNode]:
        kwargs = {
            'quote': Fiat.RUB,
            'payment_method': payment_method,
            'custom_method_name': custom_method_name,
        }

        nodes = [
            BinanceP2P(base=Stable.USDT, **kwargs),
            BinanceP2P(base=Stable.BUSD, **kwargs),
            BinanceP2P(base=BinanceFiat.RUB, **kwargs),
        ]

        if crypto:
            nodes += [
                BinanceP2P(base=Crypto.BTC, **kwargs),
                BinanceP2P(base=Crypto.BNB, **kwargs),
                BinanceP2P(base=Crypto.ETH, **kwargs),
                BinanceP2P(base=Crypto.SHIB, **kwargs),
            ]

        return nodes

    def get_binance_p2p_kazakhstan(
        self,
        crypto: bool,
        payment_method: BPM
    ) -> list[GenericNode]:
        bases = [Stable.USDT, Stable.BUSD, Stable.DAI]
        if crypto:
            bases += [Crypto.BTC, Crypto.BNB, Crypto.ETH, Crypto.SHIB]
        quotes = [Fiat.KZT, Fiat.USD, Fiat.EUR]

        return [
            BinanceP2P(base=base, quote=quote, payment_method=payment_method)
            for base, quote in itertools.product(bases, quotes)
        ]

    def get_binance_p2p_indonesia(
        self,
        crypto: bool,
        payment_method: BPM
    ) -> list[GenericNode]:
        bases = [Stable.USDT, Stable.BUSD, Stable.BIDR]
        if crypto:
            bases += [Crypto.BTC, Crypto.BNB, Crypto.ETH, Crypto.DOGE]

        return [
            BinanceP2P(base=base, quote=Fiat.IDR, payment_method=payment_method)
            for base in bases
        ]

    def get_binance_p2p_uzbekistan(
        self,
        crypto: bool,
        payment_method: BPM
    ) -> list[GenericNode]:
        bases = [Stable.USDT, Stable.BUSD]
        if crypto:
            bases += [Crypto.BTC, Crypto.BNB, Crypto.ETH, Crypto.SHIB]

        return [
            BinanceP2P(base=base, quote=Fiat.UZS, payment_method=payment_method)
            for base in bases
        ]

    ################################################################
    # Other
    def get_paysend(self) -> list[GenericNode]:
        return [
            Paysend_KZTIDR(),
            Paysend_KZTUSD_KZ(),
            Paysend_RUBUZS(),
            Paysend_RUBTJS(),
            Paysend_UZSKZT(),
            Paysend_UZSUSD_KZ(),
        ]
