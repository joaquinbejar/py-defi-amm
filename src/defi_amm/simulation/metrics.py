from typing import Dict, List

import matplotlib.pyplot as plt

from defi_amm.models.amm import AMM
from defi_amm.models.liquidity_pool import LiquidityPool


class ProfitabilityMetrics:
    def __init__(self, amm: AMM):
        self.amm = amm
        self.total_fees: Dict[str, List[float]] = {}
        self.lp_returns: Dict[str, List[float]] = {}
        self.impermanent_loss: Dict[str, List[float]] = {}
        self.time_steps: List[int] = []

    def update_metrics(self, step: int):
        """Update all metrics for the current time step."""
        self.time_steps.append(step)
        self._update_total_fees()
        self._update_lp_returns()
        self._update_impermanent_loss()

    def _update_total_fees(self):
        """Update total fees earned for each pool."""
        fees = self.amm.calculate_fees_earned()
        for token, fee in fees.items():
            if token not in self.total_fees:
                self.total_fees[token] = []
            self.total_fees[token].append(fee)

    def _update_lp_returns(self):
        """Update liquidity provider returns for each pool."""
        for pool_key, pool in self.amm.pools.items():
            token_a, token_b = pool_key.split('-')
            returns = self._calculate_lp_returns(pool)
            if pool_key not in self.lp_returns:
                self.lp_returns[pool_key] = []
            self.lp_returns[pool_key].append(returns)

    def _calculate_lp_returns(self, pool: LiquidityPool) -> float:
        """Calculate the current returns for liquidity providers in a pool."""
        # This is a simplified calculation and might need to be adjusted based on your specific AMM model
        total_liquidity = pool.token_a_reserve + pool.token_b_reserve
        total_fees = pool.total_fees_a + pool.total_fees_b
        return (total_liquidity + total_fees) / pool.total_lp_tokens - 1

    def _update_impermanent_loss(self):
        """Update impermanent loss for each pool."""
        for pool_key, pool in self.amm.pools.items():
            token_a, token_b = pool_key.split('-')
            # Assume we have a method to get the current price ratio
            current_price_ratio = pool.get_exchange_rate()
            il = pool.calculate_impermanent_loss(current_price_ratio)
            if pool_key not in self.impermanent_loss:
                self.impermanent_loss[pool_key] = []
            self.impermanent_loss[pool_key].append(il)

    def plot_metrics(self):
        """Plot all metrics over time."""
        self._plot_total_fees()
        self._plot_lp_returns()
        self._plot_impermanent_loss()

    def _plot_total_fees(self):
        """Plot total fees earned over time for each token."""
        plt.figure(figsize=(10, 6))
        for token, fees in self.total_fees.items():
            plt.plot(self.time_steps, fees, label=f'{token} Fees')
        plt.title('Total Fees Earned Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Total Fees')
        plt.legend()
        plt.grid(True)
        plt.show()

    def _plot_lp_returns(self):
        """Plot liquidity provider returns over time for each pool."""
        plt.figure(figsize=(10, 6))
        for pool_key, returns in self.lp_returns.items():
            plt.plot(self.time_steps, returns, label=f'{pool_key} Returns')
        plt.title('Liquidity Provider Returns Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Returns')
        plt.legend()
        plt.grid(True)
        plt.show()

    def _plot_impermanent_loss(self):
        """Plot impermanent loss over time for each pool."""
        plt.figure(figsize=(10, 6))
        for pool_key, loss in self.impermanent_loss.items():
            plt.plot(self.time_steps, loss, label=f'{pool_key} IL')
        plt.title('Impermanent Loss Over Time')
        plt.xlabel('Time Step')
        plt.ylabel('Impermanent Loss')
        plt.legend()
        plt.grid(True)
        plt.show()

    def get_latest_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get the latest values for all metrics."""
        latest_metrics = {
            'total_fees': {token: fees[-1] if fees else 0 for token, fees in self.total_fees.items()},
            'lp_returns': {pool: returns[-1] if returns else 0 for pool, returns in self.lp_returns.items()},
            'impermanent_loss': {pool: loss[-1] if loss else 0 for pool, loss in self.impermanent_loss.items()}
        }
        return latest_metrics
