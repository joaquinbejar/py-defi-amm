#!/usr/bin/env python
from flask import Flask

from defi_amm.models.amm import AMM
from defi_amm.models.risk_management import RiskManagement

app = Flask(__name__)

amm = AMM()
amm.create_pool('ETH', 'USDC', 5000, 5000)

risk_management = RiskManagement(amm)
transaction_history = {}
from defi_amm.routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
