from brownie import accounts, reverts

from web3 import Web3
from web3.auto import w3
import pytest


# START ======================== TESTS OWNERSHIP =================================


def test_ownership_transfer_ownership_to_another_account(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    dexilon_bridge.transferOwnership(accounts[1], {"from": accounts[0]})
    assert dexilon_bridge.owner() == accounts[1]


def test_ownership_transfer_ownership_back(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    dexilon_bridge.transferOwnership(accounts[0], {"from": accounts[1]})
    assert dexilon_bridge.owner() == accounts[0]


def test_ownership_transfer_ownership_revert_zero_address(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.transferOwnership("0x" + "0" * 40, {"from": accounts[0]})
    except Exception as e:
        print(repr(e))

    with reverts("Ownable: new owner is the zero address"):
        dexilon_bridge.transferOwnership.call("0x" + "0" * 40, {"from": accounts[0]})


def test_ownership_transfer_ownership_revert_only_owner(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    with reverts("Ownable: caller is not the owner"):
        dexilon_bridge.transferOwnership.call(accounts[1], {"from": accounts[1]})
