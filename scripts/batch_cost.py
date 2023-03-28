from brownie import DexilonBridge_v09, ERC20Mock, VerifySignature, accounts, network
from eth_keys import keys
from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct, _hash_eip191_message
import os
from dotenv import load_dotenv
import random
from uuid import uuid4
import time
from hexbytes import HexBytes


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
    project_name = "Dexilon"
    project_version = "tests"
    dexilon_bridge = DexilonBridge_v09.deploy(
        project_name, project_version, {"from": accounts[0]}
    )
    # Build domain separator
    local_name_hash = Web3.keccak(text=project_name).hex()
    version_hash = Web3.keccak(text=project_version).hex()
    type_hash = Web3.keccak(
        text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    ).hex()
    chainid = 1337
    local_abiencode = (
        str(type_hash)
        + str(local_name_hash).replace("0x", "")
        + str(version_hash).replace("0x", "")
        + str((chainid).to_bytes(32, byteorder="big").hex()).replace("0x", "")
        + "0" * 24
        + str(dexilon_bridge.address).lower().replace("0x", "")
    )
    domainSeparator = Web3.keccak(HexBytes(local_abiencode)).hex()

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

    # 7 Validators
    private_keys = private_keys[:7]
    pk_accounts = []
    for pk in private_keys:
        pk_accounts.append(accounts.add(pk))

    # add another validator without private key
    pk_accounts.append(accounts[0])

    tx = dexilon_bridge.addValidators(pk_accounts, {"from": accounts[0]})

    dexilon_bridge.setSupportedToken(usdc_token.address, True)
    dexilon_bridge.setSupportedToken(dxln_token.address, True)

    usdc_token.approve(dexilon_bridge, 10 ** 12, {"from": accounts[0]})
    dexilon_bridge.deposit(usdc_token, 10 ** 12, {"from": accounts[0]})

    batch_users = []
    batch_balances = []

    for i in range(100):
        temp_account = w3.eth.account.create()
        batch_users.append(temp_account.address)
        batch_balances.append(random.randint(1, 100) * 10 ** 6)

    batch_users[0] = accounts[0].address

    batchId = 101
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys:
        signatures.append(
            w3.eth.account.sign_message(
                encode_defunct(base_message), private_key=pk
            ).signature
        )

    tx_data = [
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    ]

    tx = dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    print("==========Accounts initialized.==========")

    withdraw_test_array = [1, 2, 3, 4, 5, 10, 20, 50, 100]

    gas_results = {}
    for number_of_users in withdraw_test_array:
        batchId = number_of_users
        base_message = Web3.solidityKeccak(
            ["bytes32", "address", "address[]", "uint256[]", "uint256"],
            [
                usdc_token.address,
                batch_users[:number_of_users],
                batch_balances[:number_of_users],
                batchId,
            ],
        )

        signatures = []
        for pk in private_keys:
            signatures.append(
                w3.eth.account.sign_message(
                    encode_defunct(base_message), private_key=pk
                ).signature
            )

        tx_data = [
            usdc_token.address,
            batch_users[:number_of_users],
            batch_balances[:number_of_users],
            batchId,
            signatures,
            {"from": accounts[0]},
        ]

        tx = dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
        gas_results[number_of_users] = tx.gas_used
        print(
            f"Users withdraw: {number_of_users}, gas: {tx.gas_used}, per user: {int(tx.gas_used/number_of_users)}"
        )

    tx = dexilon_bridge.withdraw(usdc_token, {"from": accounts[0]})

    tx.wait(1)
    print(gas_results)
    for users, gas in gas_results.items():
        print(f"{users}:{gas}:{int(gas/users)}")
