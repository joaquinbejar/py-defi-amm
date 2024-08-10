import unittest
from unittest.mock import MagicMock

from src.defi_amm.models.amm import AMM, AMMException
from defi_amm.models.liquidity_pool import LiquidityPool


class TestAMM(unittest.TestCase):
    def setUp(self):
        self.amm = AMM()
        self.amm.create_pool("USDC", "ETH", 1000, 1)

    def test_create_pool(self):
        self.amm.create_pool("DAI", "USDT", 1000, 1000)
        self.assertIn("DAI-USDT", self.amm.pools)

    def test_get_pool(self):
        pool = self.amm.get_pool("USDC", "ETH")
        self.assertIsInstance(pool, LiquidityPool)

    def test_add_liquidity(self):
        lp_tokens = self.amm.add_liquidity("USDC", "ETH", 100, 0.1)
        self.assertAlmostEqual(lp_tokens, 3.162, delta=0.001)

    def test_remove_liquidity(self):
        self.amm.add_liquidity("USDC", "ETH", 100, 0.1)
        usdc, eth = self.amm.remove_liquidity("USDC", "ETH", 5)
        self.assertAlmostEqual(usdc, 158.113, delta=0.001)
        self.assertAlmostEqual(eth, 0.1581, delta=0.0001)

    def test_swap(self):
        eth_received = self.amm.swap("USDC", "ETH", 100)
        self.assertAlmostEqual(eth_received, 990.0695, delta=0.0001)

    def test_get_exchange_rate(self):
        rate = self.amm.get_exchange_rate("USDC", "ETH")
        self.assertAlmostEqual(rate, 0.001, delta=0.0001)

    def test_get_pool_state(self):
        state = self.amm.get_pool_state("USDC", "ETH")
        self.assertIn("token_a_reserve", state)
        self.assertIn("token_b_reserve", state)

    def test_calculate_impermanent_loss(self):
        loss = self.amm.calculate_impermanent_loss("USDC", "ETH", 1.5)
        self.assertAlmostEqual(loss, 0.1010, delta=0.0001)

    def test_get_total_value_locked(self):
        tvl = self.amm.get_total_value_locked()
        self.assertIn("USDC", tvl)
        self.assertIn("ETH", tvl)

    def test_calculate_fees_earned(self):
        self.amm.swap("USDC", "ETH", 100)
        fees = self.amm.calculate_fees_earned()
        self.assertIn("USDC", fees)
        self.assertGreater(fees["USDC"], 0)

    def test_nonexistent_pool(self):
        with self.assertRaises(AMMException):
            self.amm.get_pool("BTC", "LTC")

    def test_duplicate_pool_creation(self):
        with self.assertRaises(AMMException):
            self.amm.create_pool("USDC", "ETH", 1000, 1)


class TestAMMExtend(unittest.TestCase):

    def setUp(self):
        self.amm = AMM()
        self.amm.get_pool = MagicMock()

        self.mock_pool = MagicMock()
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 1000,
            'token_b_reserve': 2000,
            'fee': 0.003
        }
        self.amm.get_pool.return_value = self.mock_pool

    def test_calculate_rebalancing_incentive_balanced_pool(self):
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 1000,
            'token_b_reserve': 1000
        }
        incentive = self.amm.calculate_rebalancing_incentive('token_a', 'token_b', 100, 100)
        self.assertEqual(incentive, 0.0)

    def test_calculate_rebalancing_incentive_unbalanced_pool(self):
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 1000,
            'token_b_reserve': 2000
        }
        incentive = self.amm.calculate_rebalancing_incentive('token_a', 'token_b', 1000, 500)
        self.assertGreater(incentive, 0.0)

    def test_add_liquidity_with_incentive(self):
        self.amm.calculate_rebalancing_incentive = MagicMock(return_value=0.01)
        self.amm.add_liquidity = MagicMock(return_value=100)

        lp_tokens = self.amm.add_liquidity_with_incentive('token_a', 'token_b', 100, 100)
        self.assertEqual(lp_tokens, 101)  # 100 LP tokens + 1% incentive


if __name__ == '__main__':
    unittest.main()
