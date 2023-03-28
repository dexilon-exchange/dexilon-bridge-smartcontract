from brownie import (
    DexilonBridge_v10,
    accounts,
    network,
    ERC20Mock,
    ECDSAMock,
    AddressImpl,
)
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random


@pytest.fixture(scope="module")
def tokens():

    network.priority_fee("1 gwei")
    network.max_fee("10 gwei")
    network.gas_limit(10_000_000)

    usdc_token = ERC20Mock.deploy(
        "USD Coin", "USDC", accounts[0], int(10 ** 12), {"from": accounts[0]}
    )

    dxln_token = ERC20Mock.deploy(
        "Dexilon Coin", "DXLN", accounts[0], int(10 ** 24), {"from": accounts[0]}
    )

    usdc_token.transfer(accounts[1], int(11_000 * 10 ** 6), {"from": accounts[0]})
    usdc_token.transfer(accounts[2], int(11_000 * 10 ** 6), {"from": accounts[0]})
    dxln_token.transfer(accounts[1], int(11_000 * 10 ** 18), {"from": accounts[0]})
    dxln_token.transfer(accounts[2], int(11_000 * 10 ** 18), {"from": accounts[0]})

    return (usdc_token, dxln_token)


@pytest.fixture(scope="module")
def other_mocks():

    network.priority_fee("1 gwei")
    network.max_fee("10 gwei")
    network.gas_limit(10_000_000)

    ecdsa = ECDSAMock.deploy({"from": accounts[0]})
    address = AddressImpl.deploy({"from": accounts[0]})

    return (ecdsa, address)


@pytest.fixture(scope="module")
def deploy(tokens):

    network.priority_fee("1 gwei")
    network.max_fee("10 gwei")
    network.gas_limit(10_000_000)

    (usdc_token, dxln_token) = tokens

    # Deploy contracts for test module
    project_name = "Dexilon"
    project_version = "tests"
    dexilon_bridge = DexilonBridge_v10.deploy(
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
    domainSeparator = Web3.keccak(hexstr=local_abiencode).hex()

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
    pk_accounts = []
    for pk in private_keys:
        pk_accounts.append(accounts.add(pk))

    # add 11th validator without private key
    pk_accounts.append(accounts[0])

    dexilon_bridge.addValidators(pk_accounts, {"from": accounts[0]})

    dexilon_bridge.setSupportedToken(usdc_token.address, True)
    dexilon_bridge.setSupportedToken(dxln_token.address, True)

    # give contract some ether
    # accounts[0].transfer(dexilon_bridge.address, "10 ether")

    # prepare 3 users with deposits
    for i in range(3):
        usdc_token.approve(dexilon_bridge, int(1_000 * 10 ** 6), {"from": accounts[i]})
        dexilon_bridge.deposit(usdc_token, int(1_000 * 10 ** 6), {"from": accounts[i]})
        dxln_token.approve(dexilon_bridge, int(1_000 * 10 ** 18), {"from": accounts[i]})
        dexilon_bridge.deposit(dxln_token, int(1_000 * 10 ** 18), {"from": accounts[i]})

    return (dexilon_bridge, pk_accounts, private_keys, domainSeparator)
