from arbitrage_helper.node import *
from arbitrage_helper.route import Route, RouteGenerator


class Arbitrage:
    def __init__(self):
        pass

    def run(self, max_size: int, start_balance: Balance, crypto: bool):
        ################################################################
        # Prep data
        route_gen = RouteGenerator()
        nodes = route_gen.all_nodes(crypto=crypto)
        nodes = route_gen.parse_nodes(nodes=nodes, workers=25)

        routes = []
        for size in range(2, max_size+1):
            routes += list(route_gen.smartgen_loop_routes(nodes=nodes, size=size, currency=start_balance.currency))

        ################################################################
        # Print profitable
        routes.sort(key=lambda r: self.analyze_route(start_balance=start_balance, route=r)[1])
        for route in routes:
            profit, perc = self.analyze_route(start_balance=start_balance, route=route)
            if perc > 0:
                report = self.generate_report(start_balance=start_balance, route=route)
                print("----------------------------------------------------------------")
                print(f"{profit} ({perc:.3f}%)")
                print(report)

    def analyze_route(self, start_balance: Balance, route: Route) -> Tuple[Balance, float]:
        end_balance = route.forward(start_balance)[-1]
        profit = end_balance - start_balance
        perc = (end_balance / start_balance - 1) * 100

        return profit, perc

    def generate_report(self, start_balance: Balance, route: Route) -> str:
        report = ""

        balances = route.forward(start_balance)
        nodes = route.nodes

        for i in range(len(balances)-1):
            b1, b2 = balances[i], balances[i+1]
            report += f"{b1} >>> {b2}, {nodes[i].repr}\n"

        return report
