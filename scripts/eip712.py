from brownie import EIP712Mock, accounts, network
from eth_keys import keys
from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct, _hash_eip191_message
import os
from dotenv import load_dotenv
import random
from uuid import uuid4
import time


def main():
    network.priority_fee("1 gwei")
    network.max_fee("10 gwei")
    network.gas_limit(12_000_000)

    eip712mock = EIP712Mock.deploy("Dexilon", "dev2", {"from": accounts[0]})

    contract_name_hash = eip712mock.expose_name_hash.call()
    local_name_hash = Web3.keccak(text="Dexilon").hex()
    print("Name hash from contract:", contract_name_hash)
    print(
        "Name hash from python  :",
        local_name_hash,
        local_name_hash == contract_name_hash,
    )

    version_hash = Web3.keccak(text="dev2").hex()
    contract_version_hash = eip712mock.expose_version_hash.call()
    print("Name version from contract:", contract_version_hash)
    print(
        "Name version from python  :",
        version_hash,
        contract_version_hash == version_hash,
    )

    type_hash = Web3.keccak(
        text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    ).hex()
    contract_type_hash = eip712mock.expose_type_hash.call()
    print("Name typehash from contract:", contract_type_hash)
    print(
        "Name typehash from python  :",
        type_hash,
        contract_type_hash == type_hash,
    )

    print(
        "Chainid:",
        eip712mock.expose_chainid.call(),
        eip712mock.expose_chainid.call() == 1337,
    )
    print(
        "Chainid Abi:",
        eip712mock.expose_chainid_abi.call(),
    )
    print(
        "Address:",
        eip712mock.expose_address.call(),
        eip712mock.expose_address.call() == eip712mock.address,
    )

    contract_abiencode = eip712mock.expose_abiencode.call()
    print(
        "Contract abi.encode:",
        contract_abiencode,
    )

    local_abiencode = (
        str(type_hash)
        + str(local_name_hash).replace("0x", "")
        + str(version_hash).replace("0x", "")
        + str((1337).to_bytes(32, byteorder="big").hex()).replace("0x", "")
        + "0" * 24
        + str(eip712mock.address).lower().replace("0x", "")
    )
    print(
        "Local abi.encode    :", local_abiencode, local_abiencode == contract_abiencode
    )

    local_domainSeparator = Web3.keccak(hexstr=local_abiencode).hex()
    contract_domainSeparator = eip712mock.expose_domainSeparatorV4.call()
    print("Contract Domain Separator:", contract_domainSeparator)
    print("Contract Cached Domain   :", eip712mock.expose_cached_domain.call())
    print(
        "   Local Domain Separator:",
        local_domainSeparator,
        contract_domainSeparator == local_domainSeparator,
    )
