#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from json import load, dump, loads
import sys

web3 = Web3(HTTPProvider('https://sokol.poa.network'))

with open("account.json") as file:
    account_config = load(file)

### Put your code below this comment ###

private_key = account_config["account"]

def deploy(private_key):
	account = web3.eth.account.privateKeyToAccount(private_key)
	with open("registrar.bin") as bin_file:
		bytecode = bin_file.read()
	with open("registrar.abi") as abi_file:
		abi = loads(abi_file.read())
	contract = web3.eth.contract(abi = abi, bytecode = bytecode)
	tx_c = contract.constructor().buildTransaction({
		"from" : account.address,
		"nonce" : web3.eth.getTransactionCount(account.address),
		"gas" : 1000000,
		"gasPrice" : web3.eth.gasPrice
		})
	signed = account.signTransaction(tx_c)
	tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)
	tx = web3.eth.waitForTransactionReceipt(tx_hash)
	with open('database.json', 'w') as file:
		dump({"registrar" : tx["contractAddress"], "startBlock" : tx["blockNumber"]}, file)
	print("Contract address: {}".format(tx["contractAddress"]))

def add(name):
	account = web3.eth.account.privateKeyToAccount(private_key)
	if web3.eth.getBalance(account.address) < web3.eth.gasPrice * 400000:
		print("No enough funds to add name")
		return
	with open("database.json") as database:
		data = load(database)
		contract_address = data["registrar"] 
	with open("registrar.abi") as abi_file:
		abi = loads(abi_file.read())
	contract = web3.eth.contract(address = contract_address, abi = abi)
	try:
		contract.functions.getname("{}".format(account.address)).call()
	except:
		tx_add = contract.functions.add(name).buildTransaction({
			"from" : account.address,
			"nonce" : web3.eth.getTransactionCount(account.address),
			"gas" : 400000,
			"gasPrice" : web3.eth.gasPrice
			})
		signed_tx_add = account.signTransaction(tx_add)
		tx_add_id = web3.eth.sendRawTransaction(signed_tx_add.rawTransaction)
		tx_add_receipt = web3.eth.waitForTransactionReceipt(tx_add_id)
		print("Successfully added by {}".format(tx_add_receipt["transactionHash"].hex()))
	else:
		print("One account must correspond one name")


if sys.argv[1] == "--deploy":
	deploy(private_key)
elif sys.argv[1] == "--add":
	name = sys.argv[2]
	add(name)