from defi_amm.main import app, amm, risk_management, transaction_history
from flask import request, jsonify


@app.route('/add_liquidity', methods=['POST'])
def add_liquidity():
    data = request.json
    token_a = data['token_a']
    token_b = data['token_b']
    amount_a = float(data['amount_a'])
    amount_b = float(data['amount_b'])

    try:
        lp_tokens = amm.add_liquidity_with_incentive(token_a, token_b, amount_a, amount_b)
        transaction_history.setdefault(f"{token_a}-{token_b}", []).append({
            "type": "add_liquidity",
            "token_a": token_a,
            "token_b": token_b,
            "amount_a": amount_a,
            "amount_b": amount_b,
            "lp_tokens": lp_tokens
        })
        return jsonify({"success": True, "lp_tokens": lp_tokens}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/remove_liquidity', methods=['POST'])
def remove_liquidity():
    data = request.json
    token_a = data['token_a']
    token_b = data['token_b']
    lp_tokens = float(data['lp_tokens'])

    try:
        amount_a, amount_b = amm.remove_liquidity(token_a, token_b, lp_tokens)
        transaction_history.setdefault(f"{token_a}-{token_b}", []).append({
            "type": "remove_liquidity",
            "token_a": token_a,
            "token_b": token_b,
            "lp_tokens": lp_tokens,
            "amount_a": amount_a,
            "amount_b": amount_b
        })
        return jsonify({"success": True, "amount_a": amount_a, "amount_b": amount_b}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/swap', methods=['POST'])
def swap():
    data = request.json
    token_from = data['token_from']
    token_to = data['token_to']
    amount = float(data['amount'])

    try:
        amount_out = amm.swap(token_from, token_to, amount)
        transaction_history.setdefault(f"{token_from}-{token_to}", []).append({
            "type": "swap",
            "token_from": token_from,
            "token_to": token_to,
            "amount_in": amount,
            "amount_out": amount_out
        })
        return jsonify({"success": True, "amount_out": amount_out}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/pool_state', methods=['GET'])
def get_pool_state():
    token_a = request.args.get('token_a')
    token_b = request.args.get('token_b')

    try:
        state = amm.get_pool_state(token_a, token_b)
        return jsonify({"success": True, "state": state}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/transaction_history', methods=['GET'])
def get_transaction_history():
    token_a = request.args.get('token_a')
    token_b = request.args.get('token_b')

    pool_key = f"{min(token_a, token_b)}-{max(token_a, token_b)}"
    history = transaction_history.get(pool_key, [])
    return jsonify({"success": True, "history": history}), 200


@app.route('/risk_metrics', methods=['GET'])
def get_risk_metrics():
    token_a = request.args.get('token_a')
    token_b = request.args.get('token_b')

    try:
        var = risk_management.calculate_var(token_a, token_b)
        total_fees = risk_management.calculate_total_fees_earned()
        returns = risk_management.calculate_liquidity_returns(token_a, token_b, (1000, 1000), 1.0)  # Example values

        metrics = {
            "value_at_risk": var,
            "total_fees": total_fees,
            "liquidity_returns": returns
        }
        return jsonify({"success": True, "metrics": metrics}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/activate_stop_loss', methods=['POST'])
def activate_stop_loss():
    data = request.json
    token_a = data['token_a']
    token_b = data['token_b']
    stop_loss_percentage = float(data['stop_loss_percentage'])

    try:
        triggered = risk_management.implement_stop_loss(token_a, token_b, stop_loss_percentage)
        return jsonify({"success": True, "stop_loss_triggered": triggered}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/dynamic_position_sizing', methods=['GET'])
def get_dynamic_position_sizing():
    token_a = request.args.get('token_a')
    token_b = request.args.get('token_b')
    risk_factor = float(request.args.get('risk_factor', 0.02))

    try:
        position_a, position_b = risk_management.dynamic_position_sizing(token_a, token_b, risk_factor)
        return jsonify({"success": True, "position_a": position_a, "position_b": position_b}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
