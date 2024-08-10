from src.defi_amm import logger
from src.defi_amm.models.amm import AMM
from src.defi_amm.models.risk_management import RiskManagement
from src.defi_amm.simulation.market_simulator import run_market_scenarios

if __name__ == '__main__':
    initial_prices = {'TokenA': 100, 'TokenB': 1, 'TokenC': 10}
    amm = AMM()
    amm.create_pool('TokenA', 'TokenB', 1000, 2000)
    amm.create_pool('TokenB', 'TokenC', 100, 1000)
    amm.create_pool('TokenA', 'TokenC', 500, 500)
    risk_management = RiskManagement(amm)
    stable, volatile, large_trade = run_market_scenarios(amm, risk_management, initial_prices)
    # stable, volatile, large_trade = run_market_scenarios(amm, risk_management, initial_prices)

    logger.info("Stable market report:")
    for step in stable:
        logger.info(step)

    logger.info("High volatility market report:")
    for step in volatile:
        logger.info(step)

    logger.info("Large trade market report:")
    for step in large_trade:
        logger.info(step)

