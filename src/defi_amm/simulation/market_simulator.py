import random
from typing import List, Dict

from defi_amm.models.amm import AMM
from defi_amm.models.risk_management import RiskManagement
from defi_amm.simulation.metrics import ProfitabilityMetrics


class MarketSimulation:
    def __init__(self, amm: AMM, risk_management: RiskManagement, initial_prices: dict):
        self.amm = amm
        self.risk_management = risk_management
        self.prices = initial_prices
        self.history = []
        self.metrics = ProfitabilityMetrics(amm)

    def simulate_price_change(self, token: str, volatility: float):
        """Simulate a price change for a given token."""
        change = random.normalvariate(0, volatility)
        self.prices[token] *= (1 + change)

    def simulate_trade(self, token_in: str, token_out: str, amount: float):
        """Simulate a trade between two tokens."""
        try:
            amount_out = self.amm.swap(token_in, token_out, amount)
            return True, amount_out
        except Exception as e:
            return False, str(e)

    def simulate_liquidity_event(self, token_a: str, token_b: str, amount_a: float, amount_b: float, is_add: bool):
        """Simulate adding or removing liquidity."""
        try:
            if is_add:
                lp_tokens = self.amm.add_liquidity(token_a, token_b, amount_a, amount_b)
                return True, lp_tokens
            else:
                amount_a, amount_b = self.amm.remove_liquidity(token_a, token_b, amount_a)
                return True, (amount_a, amount_b)
        except Exception as e:
            return False, str(e)

    def run_simulation(self, num_steps: int, volatility: float):
        """Run a simulation for a given number of steps."""
        for step in range(num_steps):
            # Simulate price changes
            for token in self.prices:
                self.simulate_price_change(token, volatility)

            # Simulate a random event (trade or liquidity event)
            event_type = random.choice(['trade', 'liquidity'])
            token_a, token_b = random.sample(list(self.prices.keys()), 2)
            if event_type == 'trade':
                amount = random.uniform(1, 1000)
                success, result = self.simulate_trade(token_a, token_b, amount)
            else:
                amount_a, amount_b = random.uniform(1, 1000), random.uniform(1, 1000)
                is_add = random.choice([True, False])
                success, result = self.simulate_liquidity_event(token_a, token_b, amount_a, amount_b, is_add)

            # Update profitability metrics
            self.metrics.update_metrics(step)

            # Calculate risk metrics
            var = self.risk_management.calculate_var(token_a, token_b)

            # Record the event and its outcome
            self.history.append({
                'step': step + 1,
                'prices': self.prices.copy(),
                'event_type': event_type,
                'success': success,
                'result': result,
                'var': var
            })

        # After simulation, plot metrics
        self.metrics.plot_metrics()

        # Include latest metrics in the final report
        latest_metrics = self.metrics.get_latest_metrics()
        self.history.append({
            'step': num_steps,
            'final_metrics': latest_metrics
        })

    def generate_report(self) -> List[Dict]:
        """Generate a report of the simulation results."""
        report = []
        for step in self.history:
            report_step = {
                'step': step['step']
            }

            # Add prices if available
            if 'prices' in step:
                report_step['prices'] = step['prices']

            # Add event type and success if available
            if 'event_type' in step:
                report_step['event_type'] = step['event_type']
                report_step['success'] = step['success']

            # Add VaR if available
            if 'var' in step:
                report_step['var'] = step['var']

            # Add final metrics if available
            if 'final_metrics' in step:
                report_step['final_metrics'] = step['final_metrics']

            report.append(report_step)
        return report


def run_market_scenarios(amm: AMM, risk_management: RiskManagement, initial_prices: dict):
    """Run different market scenarios and return the results."""
    # Scenario 1: Stable market
    stable_sim = MarketSimulation(amm, risk_management, initial_prices.copy())
    stable_sim.run_simulation(num_steps=100, volatility=0.01)
    stable_report = stable_sim.generate_report()

    # Scenario 2: High volatility market
    volatile_sim = MarketSimulation(amm, risk_management, initial_prices.copy())
    volatile_sim.run_simulation(num_steps=100, volatility=0.05)
    volatile_report = volatile_sim.generate_report()

    # Scenario 3: Market with sudden large trades
    large_trade_sim = MarketSimulation(amm, risk_management, initial_prices.copy())
    large_trade_sim.run_simulation(num_steps=100, volatility=0.02)
    # Inject a large trade at step 50
    large_trade_sim.simulate_trade('TokenA', 'TokenB', 10000)
    large_trade_report = large_trade_sim.generate_report()

    return stable_report, volatile_report, large_trade_report
