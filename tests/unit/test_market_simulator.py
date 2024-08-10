import unittest
from unittest.mock import MagicMock, patch

from src.defi_amm.models.amm import AMM
from src.defi_amm.models.risk_management import RiskManagement
from src.defi_amm.simulation.market_simulator import MarketSimulation, run_market_scenarios


class TestMarketSimulation(unittest.TestCase):

    def setUp(self):
        self.amm = MagicMock(spec=AMM)
        self.risk_management = MagicMock(spec=RiskManagement)
        self.initial_prices = {'TokenA': 100, 'TokenB': 1, 'TokenC': 10}
        self.simulation = MarketSimulation(self.amm, self.risk_management, self.initial_prices.copy())

    @patch('random.normalvariate', return_value=0.01)
    def test_simulate_price_change(self, mock_normalvariate):
        self.simulation.simulate_price_change('TokenA', volatility=0.02)
        self.assertAlmostEqual(self.simulation.prices['TokenA'], 101.0)

    def test_simulate_trade_success(self):
        self.amm.swap.return_value = 1000
        success, result = self.simulation.simulate_trade('TokenA', 'TokenB', 100)
        self.assertTrue(success)
        self.assertEqual(result, 1000)
        self.amm.swap.assert_called_once_with('TokenA', 'TokenB', 100)

    def test_simulate_trade_failure(self):
        self.amm.swap.side_effect = Exception("Trade failed")
        success, result = self.simulation.simulate_trade('TokenA', 'TokenB', 100)
        self.assertFalse(success)
        self.assertEqual(result, "Trade failed")

    def test_simulate_liquidity_event_add(self):
        self.amm.add_liquidity.return_value = 100
        success, result = self.simulation.simulate_liquidity_event('TokenA', 'TokenB', 100, 100, is_add=True)
        self.assertTrue(success)
        self.assertEqual(result, 100)
        self.amm.add_liquidity.assert_called_once_with('TokenA', 'TokenB', 100, 100)

    def test_simulate_liquidity_event_remove(self):
        self.amm.remove_liquidity.return_value = (50, 50)
        success, result = self.simulation.simulate_liquidity_event('TokenA', 'TokenB', 50, 0, is_add=False)
        self.assertTrue(success)
        self.assertEqual(result, (50, 50))
        self.amm.remove_liquidity.assert_called_once_with('TokenA', 'TokenB', 50)

    def test_generate_report(self):
        # Manually add history entries
        self.simulation.history = [
            {'step': 1, 'prices': {'TokenA': 101, 'TokenB': 1}, 'event_type': 'trade', 'success': True, 'var': 50.0},
            {'step': 2, 'prices': {'TokenA': 102, 'TokenB': 1.01}, 'event_type': 'liquidity', 'success': True,
             'var': 51.0}
        ]
        report = self.simulation.generate_report()
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0]['step'], 1)
        self.assertEqual(report[1]['step'], 2)

    @patch('src.defi_amm.simulation.market_simulator.MarketSimulation.simulate_trade')
    @patch('src.defi_amm.simulation.market_simulator.MarketSimulation.run_simulation')
    def test_run_market_scenarios(self, mock_run_simulation, mock_simulate_trade):
        stable_report, volatile_report, large_trade_report = run_market_scenarios(self.amm, self.risk_management,
                                                                                  self.initial_prices)

        self.assertEqual(len(stable_report), 0)
        self.assertEqual(len(volatile_report), 0)
        self.assertEqual(len(large_trade_report), 0)
        mock_run_simulation.assert_called()
        mock_simulate_trade.assert_called_once_with('TokenA', 'TokenB', 10000)


if __name__ == '__main__':
    unittest.main()
