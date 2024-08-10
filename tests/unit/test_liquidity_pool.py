import unittest

from src.defi_amm.models.liquidity_pool import LiquidityPool, LiquidityPoolException


class TestLiquidityPool(unittest.TestCase):
    def setUp(self):
        self.pool = LiquidityPool(1000, 1000)

    def test_add_liquidity(self):
        lp_tokens = self.pool.add_liquidity(100, 100)
        self.assertAlmostEqual(lp_tokens, 100, delta=0.01)
        self.assertEqual(self.pool.token_a_reserve, 1100)
        self.assertEqual(self.pool.token_b_reserve, 1100)

    def test_remove_liquidity(self):
        self.pool.add_liquidity(100, 100)
        token_a, token_b = self.pool.remove_liquidity(50)
        self.assertAlmostEqual(token_a, 50, delta=0.01)
        self.assertAlmostEqual(token_b, 50, delta=0.01)

    def test_swap_a_to_b(self):
        token_b_received = self.pool.swap_a_to_b(100)
        self.assertAlmostEqual(token_b_received, 90.661, delta=0.001)

    def test_swap_b_to_a(self):
        token_a_received = self.pool.swap_b_to_a(100)
        self.assertAlmostEqual(token_a_received, 90.661, delta=0.001)

    def test_get_exchange_rate(self):
        rate = self.pool.get_exchange_rate()
        self.assertEqual(rate, 1)

    def test_calculate_impermanent_loss(self):
        loss = self.pool.calculate_impermanent_loss(1.5)
        self.assertAlmostEqual(loss, 0.101, delta=0.001)

    def test_invalid_liquidity_addition(self):
        with self.assertRaises(LiquidityPoolException):
            self.pool.add_liquidity(100, 200)

    def test_insufficient_lp_tokens_removal(self):
        with self.assertRaises(LiquidityPoolException):
            self.pool.remove_liquidity(2000)


if __name__ == '__main__':
    unittest.main()
