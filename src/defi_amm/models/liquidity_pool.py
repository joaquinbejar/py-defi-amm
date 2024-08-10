from typing import Dict, Tuple

import math

from defi_amm.utils.logging import logger


class LiquidityPoolException(ValueError):
    """
    Custom exception for errors related to the LiquidityPool operations.

    This exception is raised when there are issues with liquidity provision, removal,
    or swap operations that violate the pool's rules or constraints.

    Attributes:
        message (str): Explanation of the error that occurred.
    """

    def __init__(self, message):
        """
        Initializes the LiquidityPoolException with a given message.

        Args:
            message (str): The error message to be logged and stored in the exception.
        """
        super().__init__(message)
        logger.warning(f"LiquidityPoolException: {message}")


class LiquidityPool:
    """
    Represents a decentralized finance (DeFi) automated market maker (AMM) liquidity pool.

    This class handles the core operations of an AMM-based liquidity pool, including
    adding/removing liquidity, swapping tokens, and calculating metrics like exchange
    rates and impermanent loss.

    Attributes:
        token_a_reserve (float): The current reserve of token A in the pool.
        token_b_reserve (float): The current reserve of token B in the pool.
        k (float): The constant product of the reserves, which must remain constant during swaps.
        fee (float): The fee charged on swaps, expressed as a decimal fraction (e.g., 0.003 for 0.3%).
        total_fees_a (float): The total fees collected in token A.
        total_fees_b (float): The total fees collected in token B.
        total_lp_tokens (float): The total amount of liquidity provider (LP) tokens minted.
    """

    def __init__(self, token_a_reserve: float, token_b_reserve: float, fee: float = 0.003):
        """
        Initializes a LiquidityPool with given reserves and a swap fee.

        Args:
            token_a_reserve (float): Initial reserve of token A.
            token_b_reserve (float): Initial reserve of token B.
            fee (float): Swap fee as a decimal (default is 0.003, representing 0.3%).

        Raises:
            LiquidityPoolException: If the initial reserves are invalid (e.g., non-positive).
        """
        self.token_a_reserve = token_a_reserve
        self.token_b_reserve = token_b_reserve
        self.k = token_a_reserve * token_b_reserve
        self.fee = fee
        self.total_fees_a = 0
        self.total_fees_b = 0
        self.total_lp_tokens = math.sqrt(token_a_reserve * token_b_reserve)

    def add_liquidity(self, token_a_amount: float, token_b_amount: float, tolerance: float = 1e-3) -> float:
        """
        Adds liquidity to the pool in proportion to the current reserves.

        Args:
            token_a_amount (float): The amount of token A to add to the pool.
            token_b_amount (float): The amount of token B to add to the pool.
            tolerance (float): The tolerance for the ratio check (default is 1e-3).
        Returns:
            float: The amount of LP tokens minted as a result of adding liquidity.

        Raises:
            LiquidityPoolException: If the provided liquidity is not in the current reserve ratio.
        """
        ratio = self.token_b_reserve / self.token_a_reserve
        logger.debug(f"Current ratio: {ratio:.4f}")
        if not math.isclose(token_b_amount / token_a_amount, ratio, rel_tol=tolerance):
            raise LiquidityPoolException(
                f"Liquidity must be added in the current ratio {token_b_amount / token_a_amount:.4f} != {ratio:.4f}")

        lp_tokens_minted = (token_a_amount / self.token_a_reserve) * self.total_lp_tokens

        self.token_a_reserve += token_a_amount
        self.token_b_reserve += token_b_amount
        self.k = self.token_a_reserve * self.token_b_reserve
        self.total_lp_tokens += lp_tokens_minted

        return lp_tokens_minted

    def remove_liquidity(self, lp_tokens: float) -> Tuple[float, float]:
        """
        Removes liquidity from the pool and returns the corresponding amounts of token A and token B.

        Args:
            lp_tokens (float): The amount of LP tokens to redeem for liquidity.

        Returns:
            Tuple[float, float]: The amounts of token A and token B returned to the liquidity provider.

        Raises:
            LiquidityPoolException: If there are insufficient LP tokens for the removal.
        """
        if lp_tokens > self.total_lp_tokens:
            raise LiquidityPoolException("Insufficient LP tokens")

        share = lp_tokens / self.total_lp_tokens
        token_a_amount = share * self.token_a_reserve
        token_b_amount = share * self.token_b_reserve

        self.token_a_reserve -= token_a_amount
        self.token_b_reserve -= token_b_amount
        self.k = self.token_a_reserve * self.token_b_reserve
        self.total_lp_tokens -= lp_tokens

        return token_a_amount, token_b_amount

    def swap_a_to_b(self, token_a_amount: float) -> float:
        """
        Swaps a specified amount of token A for token B.

        Args:
            token_a_amount (float): The amount of token A to swap.

        Returns:
            float: The amount of token B received in the swap.

        Raises:
            LiquidityPoolException: If the pool has insufficient liquidity for the swap.
        """
        token_a_amount_with_fee = token_a_amount * (1 - self.fee)
        token_b_amount = self.token_b_reserve - (self.k / (self.token_a_reserve + token_a_amount_with_fee))

        if token_b_amount <= 0:
            raise LiquidityPoolException("Insufficient liquidity for this trade")

        self.token_a_reserve += token_a_amount
        self.token_b_reserve -= token_b_amount
        self.total_fees_a += token_a_amount * self.fee

        return token_b_amount

    def swap_b_to_a(self, token_b_amount: float) -> float:
        """
        Swaps a specified amount of token B for token A.

        Args:
            token_b_amount (float): The amount of token B to swap.

        Returns:
            float: The amount of token A received in the swap.

        Raises:
            LiquidityPoolException: If the pool has insufficient liquidity for the swap.
        """
        token_b_amount_with_fee = token_b_amount * (1 - self.fee)
        token_a_amount = self.token_a_reserve - (self.k / (self.token_b_reserve + token_b_amount_with_fee))

        if token_a_amount <= 0:
            raise LiquidityPoolException("Insufficient liquidity for this trade")

        self.token_b_reserve += token_b_amount
        self.token_a_reserve -= token_a_amount
        self.total_fees_b += token_b_amount * self.fee

        return token_a_amount

    def get_exchange_rate(self) -> float:
        """
        Returns the current exchange rate between token A and token B.

        Returns:
            float: The exchange rate defined as the ratio of token B to token A reserves.
        """
        return self.token_b_reserve / self.token_a_reserve

    def get_pool_state(self) -> Dict[str, float]:
        """
        Retrieves the current state of the liquidity pool.

        Returns:
            Dict[str, float]: A dictionary containing the current reserves, fees, and total LP tokens.
        """
        return {
            "token_a_reserve": self.token_a_reserve,
            "token_b_reserve": self.token_b_reserve,
            "k": self.k,
            "total_fees_a": self.total_fees_a,
            "total_fees_b": self.total_fees_b,
            "total_lp_tokens": self.total_lp_tokens
        }

    # TODO: This formula assumes a 50/50 pool as in Uniswap v2.
    # TODO: For pools with different weights or multiple assets, the formula becomes more complex.
    # TODO: Commission earnings are not included in this calculation and should be considered separately.
    @staticmethod
    def calculate_impermanent_loss(price_ratio_change: float) -> float:
        """
        Calculates the impermanent loss based on a change in the price ratio of token A to token B.

        Impermanent loss occurs when the value of tokens in the pool is compared to the value
        if they were simply held outside the pool, due to changes in the relative prices of the tokens.

        Args:
            price_ratio_change (float): The ratio of the new price to the original price.

        Returns:
            float: The calculated impermanent loss as a decimal value.
        """
        sqrt_price_ratio = math.sqrt(price_ratio_change)
        impermanent_loss = 2 * (sqrt_price_ratio / (1 + sqrt_price_ratio)) - 1
        return impermanent_loss
