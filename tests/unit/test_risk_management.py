import unittest
from unittest.mock import MagicMock

import numpy as np

from src.defi_amm.models.amm import AMM
from src.defi_amm.models.risk_management import RiskManagement


class TestRiskManagement(unittest.TestCase):

    def setUp(self):
        self.amm = AMM()
        self.risk_manager = RiskManagement(self.amm)

        # Mock the get_pool method of AMM and the get_pool_state method of LiquidityPool
        self.mock_pool = MagicMock()
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 1000,
            'token_b_reserve': 2000,
            'total_lp_tokens': 100
        }
        self.amm.get_pool = MagicMock(return_value=self.mock_pool)

    def test_calculate_total_fees_earned(self):
        # Mock the calculate_fees_earned method of AMM
        self.amm.calculate_fees_earned = MagicMock(return_value={'token_a': 10, 'token_b': 20})

        fees_earned = self.risk_manager.calculate_total_fees_earned()
        self.assertEqual(fees_earned, {'token_a': 10, 'token_b': 20})
        self.amm.calculate_fees_earned.assert_called_once()

    def test_calculate_liquidity_returns(self):
        initial_investment = (500, 1000)
        current_price_ratio = 2.0

        returns = self.risk_manager.calculate_liquidity_returns('token_a', 'token_b', initial_investment,
                                                                current_price_ratio)
        self.assertAlmostEqual(returns, 1314.213, delta=0.001)

    def test_implement_stop_loss_triggered(self):
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 500,
            'token_b_reserve': 1000,
            'total_lp_tokens': 100
        }

        # Simulate an initial higher value, e.g., 2000 (higher than the current 1500)
        stop_loss_triggered = self.risk_manager.implement_stop_loss('token_a', 'token_b', stop_loss_percentage=0.1,
                                                                    initial_value=2000)
        self.assertTrue(stop_loss_triggered)

    def test_implement_stop_loss_not_triggered(self):
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 900,
            'token_b_reserve': 1800,
            'total_lp_tokens': 100
        }

        stop_loss_triggered = self.risk_manager.implement_stop_loss('token_a', 'token_b', stop_loss_percentage=0.1)
        self.assertFalse(stop_loss_triggered)

    def test_dynamic_position_sizing(self):
        position_a, position_b = self.risk_manager.dynamic_position_sizing('token_a', 'token_b', risk_factor=0.02)
        self.assertAlmostEqual(position_a, 20.0)
        self.assertAlmostEqual(position_b, 40.0)


class TestRiskManagementExtended(unittest.TestCase):

    def setUp(self):
        self.amm = AMM()
        self.risk_manager = RiskManagement(self.amm)

        # Mock the get_pool method of AMM and the get_pool_state method of LiquidityPool
        self.mock_pool = MagicMock()
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 1000,
            'token_b_reserve': 2000,
            'total_lp_tokens': 100
        }
        self.amm.get_pool = MagicMock(return_value=self.mock_pool)

    def test_calculate_var(self):
        # Mock the numpy random normal function to return a predictable result
        np.random.normal = MagicMock(return_value=np.array([-0.01, -0.02, -0.03, 0.01, 0.02]))

        var = self.risk_manager.calculate_var('token_a', 'token_b', confidence_level=0.95, num_simulations=5)
        self.assertAlmostEqual(var, 84.0)

    def test_implement_stop_loss_triggered(self):
        self.mock_pool.get_pool_state.return_value = {
            'token_a_reserve': 500,
            'token_b_reserve': 1000,
            'total_lp_tokens': 100
        }

        # Simulate an initial higher value, e.g., 2000 (higher than the current 1500)
        stop_loss_triggered = self.risk_manager.implement_stop_loss('token_a', 'token_b', stop_loss_percentage=0.1,
                                                                    initial_value=2000)
        self.assertTrue(stop_loss_triggered)


if __name__ == '__main__':
    unittest.main()
