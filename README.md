# DeFi AMM (Automated Market Maker) Project v0.1.0

## Table of Contents
1. [Introduction](#introduction)
2. [Model Assumptions](#model-assumptions)
3. [Simulation Structure](#simulation-structure)
4. [Summary of Findings](#summary-of-findings)
5. [Setup Instructions](#setup-instructions)
6. [Running the Model and API](#running-the-model-and-api)
7. [API Endpoints](#api-endpoints)
8. [API Usage Examples](#api-usage-examples)
9. [Testing](#testing)

## Introduction

This project implements a Decentralized Finance (DeFi) Automated Market Maker (AMM) model. It includes a basic AMM implementation, risk management features, and a simulation environment to test the model under various market conditions.

## Model Assumptions

1. **Constant Product Formula**: The AMM uses the constant product formula (x * y = k) for pricing and liquidity provision.
2. **Fee Structure**: A base fee of 0.3% is applied to all trades, which can be adjusted based on market conditions up to a maximum of 1%.
3. **Impermanent Loss**: The model accounts for impermanent loss in liquidity provision.
4. **Risk Management**: Includes Value at Risk (VaR) calculation, stop-loss mechanisms, and dynamic position sizing.
5. **Market Simulation**: Assumes normally distributed price changes for simulating market movements.
6. **Liquidity Incentives**: Implements a rebalancing incentive mechanism to encourage liquidity provision that balances the pool.

## Simulation Structure

The simulation is structured as follows:

1. **AMM Model** (`amm.py`): Core AMM functionality including pool creation, swaps, and liquidity management.
2. **Liquidity Pool** (`liquidity_pool.py`): Represents individual liquidity pools and handles token reserves.
3. **Risk Management** (`risk_management.py`): Implements risk assessment and mitigation strategies.
4. **Market Simulator** (`market_simulator.py`): Simulates various market conditions to test the AMM model.
5. **Metrics** (`metrics.py`): Calculates and tracks performance metrics during simulations.

The simulation runs through the following steps:
1. Initialize AMM with liquidity pools
2. Run multiple scenarios (stable market, high volatility, large trades)
3. For each step in a scenario:
   - Simulate price changes
   - Execute random trades or liquidity events
   - Update metrics
   - Apply risk management strategies
4. Generate reports for each scenario

## Summary of Findings

Initial simulations suggest:

1. The AMM model performs stably under normal market conditions.
2. High volatility scenarios lead to increased impermanent loss for liquidity providers.
3. Large trades can significantly impact pool balances, triggering rebalancing incentives.
4. Risk management strategies, particularly dynamic fee adjustment and stop-loss mechanisms, help mitigate extreme market movements.
5. The rebalancing incentive mechanism encourages more balanced liquidity provision over time.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/joaquinbejar/py-defi-amm.git
   cd py-defi-amm
   ```

2. Create and activate a virtual environment:
   ```
   make create-venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   make install-dep
   ```


## Running the Model and API

1. To run the simulation:
   ```
   python src/defi_amm/simulator_runner.py
   ```

2. To start the API:
   ```
   export FLASK_APP=src/defi_amm/main.py
   flask run
   ```

   The API will be available at `http://127.0.0.1:5000/`.

3. To build and run the API using Docker:

   Build the Docker image:
   ```
   make docker-build
   ```

   Run the Docker container:
   ```
   make docker-run
   ```

   This will build the Docker image using the Dockerfile in the Docker directory, tag it as "defi_amm:latest", and then run the container, mapping port 5000 from the container to port 5000 on your host machine.

   The API will be available at `http://localhost:5000/` when running through Docker.

## API Endpoints

- POST `/add_liquidity`: Add liquidity to a pool
- POST `/remove_liquidity`: Remove liquidity from a pool
- POST `/swap`: Perform a token swap
- GET `/pool_state`: Get the current state of a pool
- GET `/transaction_history`: Retrieve transaction history for a pool
- GET `/risk_metrics`: Get risk metrics for a pool
- POST `/activate_stop_loss`: Activate stop-loss for a pool
- GET `/dynamic_position_sizing`: Get suggested position sizes based on risk

## API Usage Examples

Here are examples of how to interact with the DeFi AMM API using curl commands:

### Add Liquidity

```bash
curl -X POST http://127.0.0.1:5000/add_liquidity \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "ETH",
    "token_b": "USDC",
    "amount_a": 1.0,
    "amount_b": 1.0002
  }'
```

### Remove Liquidity

```bash
curl -X POST http://127.0.0.1:5000/remove_liquidity \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "ETH",
    "token_b": "USDC",
    "lp_tokens": 44.72135954999579
  }'
```

### Perform Token Swap

```bash
curl -X POST http://127.0.0.1:5000/swap \
  -H "Content-Type: application/json" \
  -d '{
    "token_from": "ETH",
    "token_to": "USDC",
    "amount": 0.1
  }'
```

### Get Pool State

```bash
curl -X GET "http://127.0.0.1:5000/pool_state?token_a=ETH&token_b=USDC"
```

### Get Transaction History

```bash
curl -X GET "http://127.0.0.1:5000/transaction_history?token_a=ETH&token_b=USDC"
```

### Get Risk Metrics

```bash
curl -X GET "http://127.0.0.1:5000/risk_metrics?token_a=ETH&token_b=USDC"
```

### Activate Stop Loss

```bash
curl -X POST http://127.0.0.1:5000/activate_stop_loss \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "ETH",
    "token_b": "USDC",
    "stop_loss_percentage": 0.1
  }'
```

### Get Dynamic Position Sizing

```bash
curl -X GET "http://127.0.0.1:5000/dynamic_position_sizing?token_a=ETH&token_b=USDC&risk_factor=0.02"
```

## Testing

To run unit tests:
```
make test
```

To run tests with coverage:
```
make run-unit-test-coverage
```

---

For more detailed information about the project structure and implementation details, please refer to the individual source files and their documentation.