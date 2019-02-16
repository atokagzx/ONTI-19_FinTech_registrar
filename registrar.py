#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from json import load

web3 = Web3(HTTPProvider('https://sokol.poa.network'))

with open('account.json') as file:
    account_config = load(file)

with open('database.json') as file:
    database = load(file)

### Put your code below this comment ###
