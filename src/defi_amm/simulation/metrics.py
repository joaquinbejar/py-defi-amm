from typing import Dict, List

import matplotlib.pyplot as plt
from defi_amm.models.amm import AMM
from defi_amm.models.liquidity_pool import LiquidityPool


class ProfitabilityMetrics:
    """
    ProfitabilityMetrics

    A class for calculating and plotting profitability metrics of an Automated Market Maker (AMM) system.

    Attributes:
        amm (AMM): The AMM object to calculate metrics for.
        total_fees (Dict[str, List[float]]): A dictionary mapping each token to a list of accumulated fees over time.
        lp_returns (Dict[str, List[float]]): A dictionary mapping each pool to a list of liquidity provider returns over time.
        impermanent_loss (Dict[str, List[float]]): A dictionary mapping each pool to a list of impermanent losses over time.
        time_steps (List[int]): A list of time steps.

    Methods:
        update_metrics(step: int)
            Update all metrics for the current time step.

        _update_total_fees()
            Update total fees earned for each pool.

        _update_lp_returns()
            Update liquidity provider returns for each pool.

        _calculate_lp_returns(pool: LiquidityPool) -> float
            Calculate the current returns for liquidity providers in a pool.

        _update_impermanent_loss()
            Update impermanent loss for each pool.

        plot_metrics()
            Plot all metrics over time.

        _plot_total_fees()
            Plot total fees earned over time for each token.

        _plot_lp_returns()
            Plot liquidity provider returns over time for each pool.

        _plot_impermanent_loss()
            Plot impermanent loss over time for each pool.

        get_latest_metrics() -> Dict[str, Dict[str, float]]
            Get the latest values for all metrics.
    """
    def __init__(self, amm: AMM):
        self.amm = amm
        self.total_fees: Dict[str, List[float]] = {}
        self.lp_returns: Dict[str, List[float]] = {}
        self.impermanent_loss: Dict[str, List[float]] = {}
        self.time_steps: List[int] = []

    def update_metrics(self, step: int):
        """
        Update metrics for the given step.

        :param step: The current step number.
        :type step: int
        :return: None
        """
        self.time_steps.append(step)
        self._update_total_fees()
        self._update_lp_returns()
        self._update_impermanent_loss()

    def _update_total_fees(self):
        """
        Update the total fees earned for each token.

        :return: None
        """
        fees = self.amm.calculate_fees_earned()
        for token, fee in fees.items():
            if token not in self.total_fees:
                self.total_fees[token] = []
            self.total_fees[token].append(fee)

    def _update_lp_returns(self):
        """
        Updates the LP returns for each pool in the AMM.

        :return: None
        """
        for pool_key, pool in self.amm.pools.items():
            token_a, token_b = pool_key.split('-')
            returns = self._calculate_lp_returns(pool)
            if pool_key not in self.lp_returns:
                self.lp_returns[pool_key] = []
            self.lp_returns[pool_key].append(returns)

    def _calculate_lp_returns(self, pool: LiquidityPool) -> float:
        """

        :param pool: The liquidity pool object containing the reserves and fees.
        :type pool: LiquidityPool
        :return: The calculated LP returns as a float.
        :rtype: float

        """
        # This is a simplified calculation and might need to be adjusted based on your specific AMM model
        total_liquidity = pool.token_a_reserve + pool.token_b_reserve
        total_fees = pool.total_fees_a + pool.total_fees_b
        return (total_liquidity + total_fees) / pool.total_lp_tokens - 1

    def _update_impermanent_loss(self):
        """
        Updates the impermanent loss for each pool in the AMM.

        :return: None
        """
        for pool_key, pool in self.amm.pools.items():
            token_a, token_b = pool_key.split('-')
            # Assume we have a method to get the current price ratio
            current_price_ratio = pool.get_exchange_rate()
            il = pool.calculate_impermanent_loss(current_price_ratio)
            if pool_key not in self.impermanent_loss:
                self.impermanent_loss[pool_key] = []
            self.impermanent_loss[pool_key].append(il)

    def plot_metrics(self):
        """
        This method plots various metrics related to total fees, LP returns, and impermanent loss.

        :return: None
        """
        self._plot_total_fees()
        self._plot_lp_returns()
        self._plot_impermanent_loss()

    def _plot_total_fees(self):
        """
        Plot the total fees earned over time.

        :return: None
        """
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
        """
        Plot the liquidity provider returns over time.

        :return: None
        """
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
        """
        Plot the impermanent loss over time for each pool.

        :return: None
        """
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
        """

        Method Name: get_latest_metrics

        Parameters:
            - self: The self keyword refers to the instance of the class. It is used to access methods and attributes within the class.

        :return: A dictionary containing the latest metrics of the application. The dictionary has the following structure:

            {
                'total_fees': {
                    token: fee,
                    ...
                },
                'lp_returns': {
                    pool: return,
                    ...
                },
                'impermanent_loss': {
                    pool: loss,
                    ...
                }
            }

            Each sub-dictionary contains key-value pairs where the key represents the token/pool name, and the value represents
            the latest metric value. If there are no metrics available for a particular token/pool, the value will be 0.

        """
        latest_metrics = {
            'total_fees': {token: fees[-1] if fees else 0 for token, fees in self.total_fees.items()},
            'lp_returns': {pool: returns[-1] if returns else 0 for pool, returns in self.lp_returns.items()},
            'impermanent_loss': {pool: loss[-1] if loss else 0 for pool, loss in self.impermanent_loss.items()}
        }
        return latest_metrics
