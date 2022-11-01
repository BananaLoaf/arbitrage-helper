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
