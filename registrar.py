#!/usr/bin/env python

from web3 import Web3, HTTPProvider
from json import load, dump, loads
import sys
import requests

web3 = Web3(HTTPProvider('https://sokol.poa.network'))
url = "https://gasprice.poa.network"

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
	url = "https://gasprice.poa.network"
	headers = {"accept": "application/json"}
	data = requests.get(url, headers = headers)
	gas_price = int(data.json()["fast"] * 1000000000)
	tx_c = contract.constructor().buildTransaction({
		"from" : account.address,
		"nonce" : web3.eth.getTransactionCount(account.address),
		"gas" : 1000000,
		"gasPrice" : gas_price
		})
	signed = account.signTransaction(tx_c)
	tx_hash = web3.eth.sendRawTransaction(signed.rawTransaction)
	tx = web3.eth.waitForTransactionReceipt(tx_hash)
	with open('database.json', 'w') as file:
		dump({"registrar" : tx["contractAddress"], "startBlock" : tx["blockNumber"]}, file)
	print("Contract address: {}".format(tx["contractAddress"]))

def add(name):
	account = web3.eth.account.privateKeyToAccount(private_key)
	url = "https://gasprice.poa.network"
	headers = {"accept": "application/json"}
	data = requests.get(url, headers = headers)
	gas_price = int(data.json()["fast"] * 1000000000)
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
			"gasPrice" : gas_price
			})
		signed_tx_add = account.signTransaction(tx_add)
		tx_add_id = web3.eth.sendRawTransaction(signed_tx_add.rawTransaction)
		tx_add_receipt = web3.eth.waitForTransactionReceipt(tx_add_id)
		print("Successfully added by {}".format(tx_add_receipt["transactionHash"].hex()))
	else:
		print("One account must correspond one name")

def delete():
	account = web3.eth.account.privateKeyToAccount(private_key)
	url = "https://gasprice.poa.network"
	headers = {"accept": "application/json"}
	data = requests.get(url, headers = headers)
	gas_price = int(data.json()["fast"] * 1000000000)
	if web3.eth.getBalance(account.address) < gas_price * 400000:
		print("No enough funds to delete name")
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
		print("No name found for your account")
	else:
		tx_add = contract.functions.dl().buildTransaction({
			"from" : account.address,
			"nonce" : web3.eth.getTransactionCount(account.address),
			"gas" : 400000,
			"gasPrice" : gas_price
			})
		signed_tx_add = account.signTransaction(tx_add)
		tx_add_id = web3.eth.sendRawTransaction(signed_tx_add.rawTransaction)
		tx_add_receipt = web3.eth.waitForTransactionReceipt(tx_add_id)
		print("Successfully deleted by {}".format(tx_add_receipt["transactionHash"].hex()))

def get_account(name):
	with open("database.json") as database:
		data = load(database)
		contract_address = data["registrar"] 
	with open("registrar.abi") as abi_file:
		abi = loads(abi_file.read())
	contract = web3.eth.contract(address = contract_address, abi = abi)
	try:
		contract.functions.getacc("{}".format(name)).call()
	except:
		print("No account registered for this name")
	else:
		ls = contract.functions.getacc("{}".format(name)).call()
		same_names = []
		for addr in ls:
			if addr == "0x0000000000000000000000000000000000000000":
				continue
			same_names.append(addr)
		if len(same_names) > 1:
			print("Registered accounts are:")
			for x in same_names:
				print(x)
		else:
			if len(same_names) == 0:
				print("No account registered for this name")
			else:
				print("Registered account is {}".format(same_names[0]))

def get_name(address):
	with open("database.json") as database:
		data = load(database)
		contract_address = data["registrar"] 
	with open("registrar.abi") as abi_file:
		abi = loads(abi_file.read())
	contract = web3.eth.contract(address = contract_address, abi = abi)
	try:
		contract.functions.getname(address).call()
	except:
		print("No name registered for this account")
	else:
		print("Registered account is \"{}\"".format(contract.functions.getname(address).call()))

def get_list():
	with open("database.json") as database:
		data = load(database)
		contract_address = data["registrar"] 
	with open("registrar.abi") as abi_file:
		abi = loads(abi_file.read())
	contract = web3.eth.contract(address = contract_address, abi = abi)
	ls = set(contract.functions.get_list().call())
	for addr in ls:
		try:
			contract.functions.getname(addr).call()
		except:
			pass
		else:
			print("\"{}\": {}".format(contract.functions.getname(addr).call(), addr))


if sys.argv[1] == "--deploy":
	deploy(private_key)
elif sys.argv[1] == "--add":
	name = sys.argv[2]
	add(name)
elif sys.argv[1] == "--del":
	delete()
elif sys.argv[1] == "--getacc":
	name = sys.argv[2]
	get_account(name)
elif sys.argv[1] == "--getname":
	address = sys.argv[2]
	get_name(address)
elif sys.argv[1] == "--list":
	get_list()
