import random
import time
from typing import Dict, Tuple

from defi_amm.config import BALANCE_MAX_INCENTIVE, VOLUME_THRESHOLD, MAX_IMBALANCE, MAX_FEE
from defi_amm.models.liquidity_pool import LiquidityPool
from defi_amm.utils.logging import logger


class AMMException(ValueError):
    """
    Custom exception for errors related to the Automated Market Maker (AMM) operations.

    This exception is raised when there are issues with pool creation, retrieval,
    or other AMM operations that violate the system's rules or constraints.

    Attributes:
        message (str): Explanation of the error that occurred.
    """

    def __init__(self, message):
        """
        Initializes the AMMException with a given message.

        Args:
            message (str): The error message to be logged and stored in the exception.
        """
        super().__init__(message)
        logger.critical(f"AMMException: {message}")


class AMM:
    """
    Represents an Automated Market Maker (AMM) system that manages multiple liquidity pools.

    This class handles the creation of liquidity pools, liquidity management (adding/removing),
    token swaps, and retrieval of pool states and metrics.

    Attributes:
        pools (Dict[str, LiquidityPool]): A dictionary mapping pool keys to LiquidityPool instances.
    """

    def __init__(self):
        """
        Initializes the AMM with an empty dictionary of liquidity pools.
        """
        self.pools: Dict[str, LiquidityPool] = {}

        self.last_trade_time = {}
        self.last_trade_volume = {}

    def calculate_recent_volume(self, token_a: str, token_b: str, time_window: int) -> float:
        """
        Simulates the calculation of recent trading volume for a given token pair.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.
            time_window (int): The time window in seconds to consider for recent volume.

        Returns:
            float: The simulated trading volume in the specified time window.
        """
        pool_key = self._get_pool_key(token_a, token_b)
        current_time = time.time()

        # If this is the first trade for this pool, initialize it
        if pool_key not in self.last_trade_time:
            self.last_trade_time[pool_key] = current_time
            self.last_trade_volume[pool_key] = 0

        # Calculate time elapsed since last trade
        time_elapsed = current_time - self.last_trade_time[pool_key]

        # If the elapsed time is greater than our window, reset the volume
        if time_elapsed > time_window:
            self.last_trade_volume[pool_key] = 0

        # Generate a random volume for this trade
        # We'll assume the volume is between 1000 and 100000 units
        this_trade_volume = random.uniform(1000, 100000)

        # Add this volume to our running total
        self.last_trade_volume[pool_key] += this_trade_volume

        # Update the last trade time
        self.last_trade_time[pool_key] = current_time

        # If the elapsed time is less than our window, scale the volume
        if time_elapsed < time_window:
            scaling_factor = time_window / time_elapsed
            return self.last_trade_volume[pool_key] * scaling_factor
        else:
            return self.last_trade_volume[pool_key]

    def create_pool(self, token_a: str, token_b: str, initial_a: float, initial_b: float) -> None:
        """
        Creates a new liquidity pool for the given token pair with initial reserves.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.
            initial_a (float): The initial reserve of token A.
            initial_b (float): The initial reserve of token B.

        Raises:
            AMMException: If a pool for the given token pair already exists.
        """
        pool_key = self._get_pool_key(token_a, token_b)
        if pool_key in self.pools:
            raise AMMException("Pool already exists")
        self.pools[pool_key] = LiquidityPool(initial_a, initial_b)

    def get_pool(self, token_a: str, token_b: str) -> LiquidityPool:
        """
        Retrieves the liquidity pool for the specified token pair.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.

        Returns:
            LiquidityPool: The liquidity pool instance for the specified token pair.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool_key = self._get_pool_key(token_a, token_b)
        pool = self.pools.get(pool_key)
        if not pool:
            raise AMMException("Pool not found")
        return pool

    def add_liquidity(self, token_a: str, token_b: str, amount_a: float, amount_b: float) -> float:
        """
        Adds liquidity to the specified token pair's pool.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.
            amount_a (float): The amount of token A to add.
            amount_b (float): The amount of token B to add.

        Returns:
            float: The amount of LP tokens minted as a result of adding liquidity.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool = self.get_pool(token_a, token_b)
        return pool.add_liquidity(amount_a, amount_b)

    def remove_liquidity(self, token_a: str, token_b: str, lp_tokens: float) -> Tuple[float, float]:
        """
        Removes liquidity from the specified token pair's pool.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.
            lp_tokens (float): The amount of LP tokens to redeem for liquidity.

        Returns:
            Tuple[float, float]: The amounts of token A and token B returned to the liquidity provider.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool = self.get_pool(token_a, token_b)
        return pool.remove_liquidity(lp_tokens)

    def swap(self, token_from: str, token_to: str, amount: float) -> float:
        """
        Swaps a specified amount of one token for another within a pool.

        Args:
            token_from (str): The symbol of the token being swapped out.
            token_to (str): The symbol of the token being swapped in.
            amount (float): The amount of the `token_from` to swap.

        Returns:
            float: The amount of `token_to` received in the swap.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool = self.get_pool(token_from, token_to)
        if token_from < token_to:
            return pool.swap_a_to_b(amount)
        else:
            return pool.swap_b_to_a(amount)

    def get_exchange_rate(self, token_a: str, token_b: str) -> float:
        """
        Retrieves the current exchange rate between two tokens in a pool.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.

        Returns:
            float: The exchange rate defined as the ratio of token B to token A reserves.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool = self.get_pool(token_a, token_b)
        return pool.get_exchange_rate()

    def get_pool_state(self, token_a: str, token_b: str) -> Dict[str, float]:
        """
        Retrieves the current state of a specified token pair's liquidity pool.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.

        Returns:
            Dict[str, float]: A dictionary containing the current reserves, fees, and total LP tokens.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool = self.get_pool(token_a, token_b)
        return pool.get_pool_state()

    def calculate_impermanent_loss(self, token_a: str, token_b: str, price_ratio_change: float) -> float:
        """
        Calculates the impermanent loss for a specified token pair's pool based on a change
        in the price ratio.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.
            price_ratio_change (float): The ratio of the new price to the original price.

        Returns:
            float: The calculated impermanent loss as a decimal value.

        Raises:
            AMMException: If the pool for the given token pair does not exist.
        """
        pool = self.get_pool(token_a, token_b)
        return pool.calculate_impermanent_loss(price_ratio_change)

    @staticmethod
    def _get_pool_key(token_a: str, token_b: str) -> str:
        """
        Generates a unique key for identifying a pool based on the token pair.

        Args:
            token_a (str): The symbol for token A.
            token_b (str): The symbol for token B.

        Returns:
            str: A string key that uniquely identifies the pool for the token pair.
        """
        return f"{min(token_a, token_b)}-{max(token_a, token_b)}"

    def get_total_value_locked(self) -> Dict[str, float]:
        """
        Calculates the total value locked (TVL) in the AMM across all pools.

        Returns:
            Dict[str, float]: A dictionary where the keys are token symbols and the values
            are the total amounts of those tokens locked in the AMM's pools.
        """
        tvl = {}
        for pool_key, pool in self.pools.items():
            token_a, token_b = pool_key.split('-')
            tvl[token_a] = tvl.get(token_a, 0) + pool.token_a_reserve
            tvl[token_b] = tvl.get(token_b, 0) + pool.token_b_reserve
        return tvl

    def calculate_fees_earned(self) -> Dict[str, float]:
        """
        Calculates the total fees earned across all pools in the AMM.

        Returns:
            Dict[str, float]: A dictionary where the keys are token symbols and the values
            are the total fees earned in those tokens across all of the AMM's pools.
        """
        fees = {}
        for pool_key, pool in self.pools.items():
            token_a, token_b = pool_key.split('-')
            fees[token_a] = fees.get(token_a, 0) + pool.total_fees_a
            fees[token_b] = fees.get(token_b, 0) + pool.total_fees_b
        return fees

    def calculate_rebalancing_incentive(self, token_a: str, token_b: str, amount_a: float, amount_b: float) -> float:
        """
        :param token_a: The symbol or identifier of the first token in the pool.
        :param token_b: The symbol or identifier of the second token in the pool.
        :param amount_a: The amount of token A to be added to the pool.
        :param amount_b: The amount of token B to be added to the pool.
        :return: The rebalancing incentive, which is a float value representing the bonus incentive for adding liquidity to the pool.

        This method calculates the rebalancing incentive for adding liquidity to a pool. It takes in the symbols or identifiers of the two tokens in the pool, as well as the amounts of token A and token B to be added. It returns a float value representing the bonus incentive for adding liquidity.

        The method first obtains the pool object using the `get_pool` method, passing in the token symbols. It then retrieves the current state of the pool using the `get_pool_state` method.

        The current ratio of token A reserve to token B reserve is calculated by dividing `state['token_a_reserve']` by `state['token_b_reserve']`. Similarly, the new ratio after adding the specified amounts of token A and token B is calculated.

        The method then calculates the difference between the current ratio and the perfect balance ratio of 1, both for the current state and the new state.

        The improvement in balance is obtained by subtracting the new imbalance from the current imbalance.

        If the balance improvement is greater than 0, it means the new liquidity helps balance the pool. The incentive is calculated based on the degree of improvement, with a maximum bonus of 2%. The incentive is then capped at the maximum value.

        If the balance improvement is not greater than 0, indicating that the new liquidity does not improve the balance, the method returns 0.0 as the rebalancing incentive.
        """
        pool = self.get_pool(token_a, token_b)
        state = pool.get_pool_state()

        current_ratio = state['token_a_reserve'] / state['token_b_reserve']
        new_ratio = (state['token_a_reserve'] + amount_a) / (state['token_b_reserve'] + amount_b)

        current_imbalance = abs(current_ratio - 1)
        new_imbalance = abs(new_ratio - 1)
        balance_improvement = current_imbalance - new_imbalance

        if balance_improvement > 0:
            max_incentive = BALANCE_MAX_INCENTIVE  # Maximum 2% bonus
            incentive = max_incentive * (balance_improvement / current_imbalance)

            return min(incentive, max_incentive)
        else:
            return 0.0

    def add_liquidity_with_incentive(self, token_a: str, token_b: str, amount_a: float, amount_b: float) -> float:
        """

        :param token_a: The first token in the liquidity pool.
        :param token_b: The second token in the liquidity pool.
        :param amount_a: The amount of token A to be used for liquidity.
        :param amount_b: The amount of token B to be used for liquidity.
        :return: The amount of LP (Liquidity Provider) tokens received after adding liquidity with incentive.

        """
        incentive = self.calculate_rebalancing_incentive(token_a, token_b, amount_a, amount_b)
        lp_tokens = self.add_liquidity(token_a, token_b, amount_a, amount_b)
        return lp_tokens * (1 + incentive)

    def adjust_fee(self, token_a: str, token_b: str) -> None:
        """
        :param token_a: A string representing the first token in the trading pair.
        :param token_b: A string representing the second token in the trading pair.
        :return: None

        Adjusts the fee for the given trading pair based on the trading volume and pool imbalance.

        The trading pair is identified by the tokens represented by `token_a` and `token_b`. The method calculates the trading volume in the last hour using the `calculate_recent_volume` method and adjusts the fee based on the volume and pool imbalance. The adjusted fee is then applied to the pool.

        The trading volume is calculated using the `calculate_recent_volume` method with a time window of 3600 seconds (1 hour). The volume factor is calculated by dividing the recent volume by the `VOLUME_THRESHOLD` constant. If the volume factor exceeds 1, it is capped at 1.

        The pool imbalance is calculated by comparing the ratio of token A reserves to token B reserves in the pool state. The imbalance factor is calculated by dividing the imbalance by the `MAX_IMBALANCE` constant. If the imbalance factor exceeds 1, it is capped at 1.

        The new fee is calculated by multiplying the current fee by (1 + volume factor) and (1 + imbalance factor). If the new fee exceeds the `MAX_FEE` constant, it is capped at `MAX_FEE`.

        Finally, the new fee is applied to the pool by updating the `fee` property of the pool object.

        Example usage:
            adjust_fee("token_A", "token_B")
        """
        pool = self.get_pool(token_a, token_b)
        state = pool.get_pool_state()

        # Calculate trading volume in the last hour
        recent_volume = self.calculate_recent_volume(token_a, token_b, time_window=3600)

        # Adjust fee based on trading volume
        volume_factor = min(recent_volume / VOLUME_THRESHOLD, 1)

        # Calculate pool imbalance
        imbalance = abs(state['token_a_reserve'] / state['token_b_reserve'] - 1)
        imbalance_factor = min(imbalance / MAX_IMBALANCE, 1)

        # Calculate new fee
        new_fee = pool.fee * (1 + volume_factor) * (1 + imbalance_factor)
        new_fee = min(new_fee, MAX_FEE)

        pool.fee = new_fee
