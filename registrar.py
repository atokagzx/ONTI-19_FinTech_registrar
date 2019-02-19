#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from json import load, dump, loads
import sys

web3 = Web3(HTTPProvider('https://sokol.poa.network'))

with open('account.json') as file:
    account_config = load(file)

### Put your code below this comment ###

private_key = account_config["account"]

def deploy(private_key):
	account = web3.eth.account.privateKeyToAccount(private_key)
	with open("registar.bin") as bin_file:
		bytecode = bin_file.read()
	with open("registar.abi") as abi_file:
		abi = loads(abi_file.read())
	contract = web3.eth.contract(abi = abi, bytecode = bytecode)
	tx_c = contract.constructor().buildTransaction({
		"from" : account.address,
		"nonce" : web3.eth.getTransactionCount(account.address),
		"gas" : 400000,
		"gasPrice" : web3.eth.gasPrice
		})
	signed = account.signTransaction(tx_c)
	tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)
	tx = web3.eth.waitForTransactionReceipt(tx_hash)
	with open('database.json', 'w') as file:
		dump({"registar" : tx["contractAddress"], "startBlock" : tx["blockNumber"]}, file)
	print("Contract address: {}".format(tx["contractAddress"]))
	return tx, abi

if sys.arvg[1] == "--deploy":
	deploy(private_key)