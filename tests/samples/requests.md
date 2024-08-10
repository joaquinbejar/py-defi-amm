# DeFi AMM API Usage Examples

This document provides examples of how to interact with our DeFi AMM API using curl commands.

## Add Liquidity

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

## Remove Liquidity

```bash
curl -X POST http://127.0.0.1:5000/remove_liquidity \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "ETH",
    "token_b": "USDC",
    "lp_tokens": 44.72135954999579
  }'
```

## Perform Token Swap

```bash
curl -X POST http://127.0.0.1:5000/swap \
  -H "Content-Type: application/json" \
  -d '{
    "token_from": "ETH",
    "token_to": "USDC",
    "amount": 0.1
  }'
```

## Get Pool State

```bash
curl -X GET "http://127.0.0.1:5000/pool_state?token_a=ETH&token_b=USDC"
```

## Get Transaction History

```bash
curl -X GET "http://127.0.0.1:5000/transaction_history?token_a=ETH&token_b=USDC"
```

## Get Risk Metrics

```bash
curl -X GET "http://127.0.0.1:5000/risk_metrics?token_a=ETH&token_b=USDC"
```

## Activate Stop Loss

```bash
curl -X POST http://127.0.0.1:5000/activate_stop_loss \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "ETH",
    "token_b": "USDC",
    "stop_loss_percentage": 0.1
  }'
```

## Get Dynamic Position Sizing

```bash
curl -X GET "http://127.0.0.1:5000/dynamic_position_sizing?token_a=ETH&token_b=USDC&risk_factor=0.02"
```

These examples assume the API is running on localhost (127.0.0.1) on port 5000. Adjust the URL if your API is hosted elsewhere.