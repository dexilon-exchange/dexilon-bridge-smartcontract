from brownie import DexilonBridge_v08, ERC20Mock, VerifySignature, accounts, network
from eth_keys import keys
from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct, _hash_eip191_message
import os
from dotenv import load_dotenv
import random
import time
from uuid import uuid4


def main():
    network.priority_fee("1 gwei")
    network.max_fee("10 gwei")
    network.gas_limit(12_000_000)

    token_usdc = "0x7592A72A46D3165Dcc7BF0802D70812Af19471B3"

    # Deploy contracts for test module
    dexilon_bridge = DexilonBridge_v08.deploy({"from": accounts[0]})

    tx = dexilon_bridge.init1_1(token_usdc, accounts[1], accounts[2])
    tx = dexilon_bridge.init1_2(token_usdc, accounts[3], accounts[4])
    tx = dexilon_bridge.changeBalance_1(token_usdc, accounts[1], accounts[2], 100)
    tx = dexilon_bridge.changeBalance_2(token_usdc, accounts[3], accounts[4], 100)

    time.sleep(1)
