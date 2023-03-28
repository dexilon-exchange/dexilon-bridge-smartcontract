from brownie import DexilonBridge_v08, ERC20Mock, VerifySignature, accounts, network
from eth_keys import keys
from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct, _hash_eip191_message
import os
from dotenv import load_dotenv
import random
from uuid import uuid4


def main():
    network.priority_fee("1 gwei")
    network.max_fee("10 gwei")
    network.gas_limit(12_000_000)

    usdc_token = ERC20Mock.deploy(
        "USD Coin", "USDC", accounts[0], int(10 ** 14), {"from": accounts[0]}
    )

    dxln_token = ERC20Mock.deploy(
        "Dexilon Coin", "DXLN", accounts[0], int(10 ** 26), {"from": accounts[0]}
    )

    # Deploy contracts for test module
    dexilon_bridge = DexilonBridge_v08.deploy({"from": accounts[0]})
    # keys from Truffle Develop
    private_keys = [
        "c87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3",
        "ae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f",
        "0dbbe8e4ae425a6d2687f1a7e3ba17bc98c673636790f1b8ad91193c05875ef1",
        "c88b703fb08cbea894b6aeff5a544fb92e78a18e19814cd85da83b71f772aa6c",
        "388c684f0ba1ef5017716adb5d21a053ea8e90277d0868337519f97bede61418",
        "659cbb0e2411a44db63778987b1e22153c086a95eb6b18bdf89de078917abc63",
        "82d052c865f5763aad42add438569276c00d3d88a2d062d36b2bae914d58b8c8",
        "aa3680d5d48a8283413f7a108367c7299ca73f553735860a87b08f39395618b7",
        "0f62d96d6675f32685bbdb8ac13cda7c23436f63efbb9d07700d8669ff12b7c4",
        "8d5366123cb560bb606379f90a0bfd4769eecc0557f1b362dcae9012b548b1e5",
    ]
    # private_keys = private_keys[:7]
    pk_accounts = []
    for pk in private_keys:
        pk_accounts.append(accounts.add(pk))

    # add 11th validator without private key
    pk_accounts.append(accounts[0])

    dexilon_bridge.addValidators(pk_accounts, {"from": accounts[0]})

    dexilon_bridge.setSupportedToken(usdc_token.address, True)
    dexilon_bridge.setSupportedToken(dxln_token.address, True)

    # Deposit USDC
    amount = 50_000 * 10 ** 6
    accounts_list = []
    for i in range(1, 9):
        accounts_list.append(accounts[i].address)
        tx = usdc_token.transfer(
            accounts[i], int(100_000 * 10 ** 6), {"from": accounts[0]}
        )
        tx = dxln_token.transfer(
            accounts[i], int(100_000 * 10 ** 18), {"from": accounts[0]}
        )
        tx = usdc_token.approve(dexilon_bridge, amount, {"from": accounts[i]})
        tx = dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[i]})
    tx.wait(1)

    batch_users = []
    batch_balances = []

    for i in range(1000):
        # temp_account = w3.eth.account.create()
        # batch_users.append(temp_account.address)
        batch_users.append(random.choice(accounts_list))
        batch_balances.append(random.randint(1, 100) * 10 ** 6)

    batchId = random.randint(1, 1000)
    base_message = Web3.solidityKeccak(
        ["uint256", "address", "address[]", "uint256[]", "uint256"],
        [1337, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys:
        signatures.append(
            w3.eth.account.sign_message(
                encode_defunct(base_message), private_key=pk
            ).signature
        )

    accounts[0].transfer(dexilon_bridge.address, "1 ether")

    print("Account  eth balance:", accounts[0].balance())
    print("Contract eth balance:", dexilon_bridge.balance())
    account_old_balance = accounts[0].balance()
    contract_old_balance = dexilon_bridge.balance()

    tx_data = [
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    ]

    tx = dexilon_bridge.batchUpdateAvailableBalances(*tx_data)

    tx.wait(1)

    print("Account  eth balance:", accounts[0].balance())
    print("Account difference:", account_old_balance - accounts[0].balance())
    print("Contract eth balance:", dexilon_bridge.balance())
    print("Contact difference:", contract_old_balance - dexilon_bridge.balance())
