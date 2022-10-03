from typing import *
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from copy import deepcopy

from tqdm import tqdm

from arbitrage_helper.node import *
from arbitrage_helper.balance import Balance
from arbitrage_helper.currency import *


class Route:
    def __init__(self, nodes: List[GenericNode]):
        self._nodes = nodes

    def __len__(self):
        return len(self._nodes)

    def __add__(self, other):
        if isinstance(other, Route):
            return Route(self.nodes + other.nodes)
        else:
            raise TypeError

    @property
    def nodes(self):
        return self._nodes

    def parse(self):
        for node in self._nodes:
            node.parse()

    def evaluate_loop(self, currency: CEnum, size: Optional[int] = None) -> bool:
        if size is not None and len(self) < size:
            return False

        first_node = self._nodes[0]
        last_node = self._nodes[-1]

        next_currency = first_node.currency_convert(currency)
        if next_currency is None:
            return False

        for i, node in enumerate(self._nodes[1:-1]):
            next_currency = node.currency_convert(currency=next_currency)
            if next_currency is None:
                return False

        next_currency = last_node.currency_convert(currency=next_currency)
        if next_currency is None or next_currency != currency:
            return False

        return True

    def forward(self, balance: Balance) -> Tuple[Balance]:
        balances = [balance, ]

        for node in self._nodes:
            new_balance = node.exchange(balance)
            balances.append(new_balance)
            balance = new_balance

        return tuple(balances)


class RouteGenerator:
    def all_nodes(self, crypto: bool) -> Dict[str, GenericNode]:
        nodes = {}

        nodes.update(self.get_binance_spot(crypto=crypto))
        nodes.update(self.get_cryptology(crypto=crypto))
        nodes.update(self.get_garantex(crypto=crypto))

        ################################################################
        # Russia
        main_methods = [BPM.Tinkoff, BPM.RosBank, BPM.RaiffeisenBankRussia, BPM.QIWI, BPM.PostBankRussia]
        minor_methods = [BPM.YandexMoney, BPM.ABank, BPM.MTSBank, BPM.HomeCreditBank,
                         BPM.RenaissanceCredit, BPM.BankSaintPetersburg, BPM.RussianStandardBank]
        unusable_methods = [BPM.Payeer, BPM.Advcash]

        nodes.update(self.get_binance_p2p_russia(crypto=crypto, payment_method=main_methods,
                                                 custom_method_name="MainBanks"))
        nodes.update(self.get_binance_p2p_russia(crypto=crypto, payment_method=minor_methods,
                                                 custom_method_name="MinorBanks"))
        nodes.update(self.get_binance_p2p_russia(crypto=crypto, payment_method=unusable_methods))

        for payment_method in main_methods + minor_methods + unusable_methods:
            nodes.update(self.get_binance_p2p_russia(crypto=crypto, payment_method=payment_method))
        # self.nodes.update(self.get_binance_p2p_russia(crypto=crypto, payment_method=BPM.RUBfiatbalance))  # TODO

        ################################################################
        # Kazakhstan
        nodes.update(self.get_binance_p2p_kazakhstan(crypto=crypto, payment_method=BPM.JysanBank))
        nodes.update(self.get_freedom_finance_bank())

        ################################################################
        # Indonesia
        for payment_method in [BPM.PermataMe, BPM.BankTransfer]:
            nodes.update(self.get_binance_p2p_indonesia(crypto=crypto, payment_method=payment_method))

        ################################################################
        # Uzbekistan
        for payment_method in [BPM.Paysend, BPM.Uzcard, BPM.Kapitalbank, BPM.Tinkoff, BPM.BankTransfer]:
            nodes.update(self.get_binance_p2p_uzbekistan(crypto=crypto, payment_method=payment_method))

        ################################################################
        nodes.update(self.get_tinkoff_bank())
        nodes.update(self.get_paysera())
        nodes.update(self.get_paysend())
        nodes.update(self.get_vexel(crypto=crypto))
        nodes.update(self.get_vexel_utils())
        nodes.update(self.get_moex())
        nodes.update(self.get_kase())

        return nodes

    def parse_nodes(self, nodes: Dict[str, GenericNode], workers: int = 10,
                    filter_invalid: bool = True, progress_bar: bool = False) -> Dict[str, GenericNode]:
        nodes_clone = deepcopy(nodes)

        if progress_bar:
            pbar = tqdm(desc="Parsing nodes", total=len(nodes_clone))

        with ThreadPoolExecutor(max_workers=workers) as ex:
            def wrapped(node):
                node.parse()
                if progress_bar:
                    pbar.update(1)

            node_keys = list(nodes_clone.keys())
            random.shuffle(node_keys)
            for node_key in node_keys:
                ex.submit(wrapped, nodes_clone[node_key])

        if progress_bar:
            pbar.close()

        if filter_invalid:
            # Filter unchanged nodes
            empty_nodes = []
            for alias, node in nodes_clone.items():
                if node.invalid:
                    empty_nodes.append(alias)
            for alias in empty_nodes:
                del nodes_clone[alias]

        return nodes_clone

    def dumbgen_loop_routes(self, nodes: Dict[str, GenericNode], size: int, currency: CEnum) -> List[Route]:
        routes = []
        n_perms = len(nodes) ** size
        with tqdm(desc="Evaluating routes", total=n_perms, mininterval=n_perms / 10000) as pbar:
            with ThreadPoolExecutor(max_workers=10) as ex:
                def wrapped(route):
                    if route.evaluate_loop(currency=currency):
                        routes.append(route)
                    pbar.update(1)

                for route_nodes in itertools.product(*[nodes for _ in range(size)]):
                    ex.submit(wrapped, Route(nodes=route_nodes))

        return routes

    def smartgen_loop_routes(self, nodes: Dict[str, GenericNode], size: int, currency: CEnum) -> Generator[Route, None, None]:
        pbar = tqdm(iterable=self._walk_node_tree(nodes=nodes, route_nodes=[], route_size=size, currency=currency, last_currency=currency),
                    desc=f"Generating routes, size: {size}, currency: {currency}")
        for route_nodes in pbar:
            if (route := Route(route_nodes)).evaluate_loop(currency=currency, size=size):
                yield route

    def _walk_node_tree(self, nodes: Dict[str, GenericNode], route_nodes: List[GenericNode], route_size: int, currency: CEnum, last_currency: CEnum) -> Generator[List[GenericNode], None, None]:
        # If there are nodes to add
        if len(route_nodes) < route_size:
            for node in nodes.values():
                # Node is valid for insertion
                chain_start = len(route_nodes) != route_size - 1 and currency in [node.base, node.quote]
                chain_end = len(route_nodes) == route_size - 1 and currency in [node.base, node.quote] and node.currency_convert(currency) == last_currency

                # At the chain start yield node + anything else recursively
                if chain_start:
                    for chain_part in self._walk_node_tree(nodes=nodes, route_nodes=route_nodes + [node], route_size=route_size,
                                                           currency=node.currency_convert(currency), last_currency=last_currency):
                        yield [node] + chain_part
                    else:
                        yield [node]

                # At the chain end yield last node
                elif chain_end:
                    yield [node]

    ################################################################
    def get_binance_spot(self, crypto: bool) -> Dict[str, GenericNode]:
        nodes = {}

        symbols = [Stable.USDT, Stable.BUSD]
        if crypto: symbols += [Crypto.BTC, Crypto.ETH, Crypto.BNB, Crypto.SHIB, Crypto.DOGE]

        for base in symbols:
            for quote in [Stable.DAI, Stable.USDT, BinanceFiat.RUB]:
                node = BinanceExchange(base=base, quote=quote)
                nodes[node.repr] = node

        return nodes

    def get_tinkoff_bank(self) -> Dict[str, GenericNode]:
        pairs = list(itertools.combinations([Fiat.USD, Fiat.RUB, Fiat.EUR, Fiat.GBP, Fiat.UZS], 2))
        nodes = {}
        for base, quote in pairs:
            node = Tinkoff(base=base, quote=quote)
            nodes[node.repr] = node

        return nodes

    def get_freedom_finance_bank(self) -> Dict[str, GenericNode]:
        nodes = [
            FreedomFinance(base=Fiat.USD, quote=Fiat.RUB),
            FreedomFinance(base=Fiat.EUR, quote=Fiat.USD),
            FreedomFinance(base=Fiat.EUR, quote=Fiat.RUB),
            FreedomFinance(base=Fiat.RUB, quote=Fiat.KZT),
            FreedomFinance(base=Fiat.EUR, quote=Fiat.KZT),
        ]
        return {node.repr: node for node in nodes}

    def get_paysera(self) -> Dict[str, GenericNode]:
        nodes = [
            Paysera(base=Fiat.RUB, quote=Fiat.KZT, base_amount=100000),
            Paysera(base=Fiat.USD, quote=Fiat.RUB, base_amount=1000),
            Paysera(base=Fiat.EUR, quote=Fiat.RUB, base_amount=1000),
            Paysera(base=Fiat.USD, quote=Fiat.EUR, base_amount=1000),
            Paysera(base=Fiat.USD, quote=Fiat.KZT, base_amount=1000),
            Paysera(base=Fiat.EUR, quote=Fiat.KZT, base_amount=1000),
        ]
        return {node.repr: node for node in nodes}

    def get_paysend(self) -> Dict[str, GenericNode]:
        nodes = [Paysend_KZTIDR(),
                 Paysend_RUBUZS(),
                 Paysend_RUBTJS(),
                 Paysend_UZSKZT()]
        return {node.repr: node for node in nodes}

    def get_binance_p2p_russia(self, crypto: bool, payment_method: Union[Iterable[BPM], BPM],
                               custom_method_name: Optional[str] = None) -> Dict[str, GenericNode]:
        nodes = [
            BinanceP2P(base=Stable.USDT, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
            BinanceP2P(base=Stable.BUSD, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
            BinanceP2P(base=BinanceFiat.RUB, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
        ]

        if crypto:
            nodes += [
                BinanceP2P(base=Crypto.BTC, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
                BinanceP2P(base=Crypto.BNB, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
                BinanceP2P(base=Crypto.ETH, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
                BinanceP2P(base=Crypto.SHIB, quote=Fiat.RUB, payment_method=payment_method, custom_method_name=custom_method_name),
            ]

        return {node.repr: node for node in nodes}

    def get_binance_p2p_kazakhstan(self, crypto: bool, payment_method: BPM):
        nodes = {}

        symbols = [Stable.USDT, Stable.BUSD, Stable.DAI]
        if crypto: symbols += [Crypto.BTC, Crypto.BNB, Crypto.ETH, Crypto.SHIB]

        for base in symbols:
            for quote in [Fiat.KZT, Fiat.USD, Fiat.EUR]:
                node = BinanceP2P(base=base, quote=quote, payment_method=payment_method)
                nodes[node.repr] = node

        return nodes

    def get_binance_p2p_indonesia(self, crypto: bool, payment_method: BPM):
        nodes = {}

        quote = Fiat.IDR
        symbols = [Stable.USDT, Stable.BUSD, Stable.BIDR]
        if crypto: symbols += [Crypto.BTC, Crypto.BNB, Crypto.ETH, Crypto.DOGE]

        for base in symbols:
            node = BinanceP2P(base=base, quote=quote, payment_method=payment_method)
            nodes[node.repr] = node

        return nodes

    def get_binance_p2p_uzbekistan(self, crypto: bool, payment_method: BPM):
        nodes = {}

        quote = Fiat.UZS
        symbols = [Stable.USDT, Stable.BUSD]
        if crypto: symbols += [Crypto.BTC, Crypto.BNB, Crypto.ETH, Crypto.SHIB]

        for base in symbols:
            node = BinanceP2P(base=base, quote=quote, payment_method=payment_method)
            nodes[node.repr] = node

        return nodes

    def get_vexel(self, crypto: bool) -> Dict[str, GenericNode]:
        nodes = {}

        symbols = [VexelFiat.EUR, VexelFiat.USD, VexelFiat.RUB, Stable.USDT, Stable.USDC]
        if crypto: symbols += [Crypto.BTC, Crypto.ETH]

        pairs = list(itertools.combinations(symbols, 2))
        for base, quote in pairs:
            node = Vexel(base=base, quote=quote)
            nodes[node.repr] = node

        return nodes

    def get_vexel_utils(self) -> Dict[str, GenericNode]:
        nodes = [
            FixedRate(base=VexelFiat.RUB, quote=Fiat.RUB, buy_price=None, sell_price=0.98, name="Vexel2Card"),
            FixedRate(base=VexelFiat.EUR, quote=Fiat.EUR, buy_price=1, sell_price=1, name="Vexel SWIFT/SEPA"),
        ]

        return {node.repr: node for node in nodes}

    def get_garantex(self, crypto: bool) -> Dict[str, GenericNode]:
        nodes = [GarantexExchange(base=Stable.USDT, quote=Fiat.RUB),
                 GarantexExchange(base=Stable.DAI, quote=Fiat.RUB),
                 GarantexExchange(base=Stable.USDC, quote=Fiat.RUB),
                 GarantexExchange(base=Stable.USDC, quote=Stable.USDT)]
        if crypto:
            nodes += [
                GarantexExchange(base=Crypto.BTC, quote=Fiat.RUB),
                GarantexExchange(base=Crypto.ETH, quote=Fiat.RUB),
                GarantexExchange(base=Crypto.BTC, quote=Stable.USDT),
                GarantexExchange(base=Crypto.ETH, quote=Crypto.BTC),
                GarantexExchange(base=Crypto.ETH, quote=Stable.USDT),
            ]
        return {node.repr: node for node in nodes}

    def get_moex(self):
        nodes = [MOEX_USDRUB_TOD(), MOEX_EURRUB_TOD()]
        return {node.repr: node for node in nodes}

    def get_kase(self):
        nodes = [KASE_EURKZT(), KASE_EURUSD(), KASE_RUBKZT(), KASE_USDKZT()]
        return {node.repr: node for node in nodes}

    def get_cryptology(self, crypto: bool):
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

        return {node.repr: node for node in nodes}
