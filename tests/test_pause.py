from brownie import VerifySignature, accounts, reverts
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random

# START ======================== TESTS PAUSE =================================


def test_pause_revert_on_not_owner_pause(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.pause.call({"from": accounts[2]})
    except Exception as e:
        print(repr(e))

    with reverts("Ownable: caller is not the owner"):
        dexilon_bridge.pause.call({"from": accounts[2]})


def test_pause_current_state_unpaused(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    assert dexilon_bridge.paused() == False


def test_pause_revert_unpause_the_unpaused(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.unpause.call({"from": accounts[0]})
    except Exception as e:
        print(repr(e))

    with reverts("Pausable: not paused"):
        dexilon_bridge.unpause.call({"from": accounts[0]})


def test_pause_change_state_to_paused(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    dexilon_bridge.pause({"from": accounts[0]})

    assert dexilon_bridge.paused() == True


def test_pause_revert_on_pause_when_paused(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.pause({"from": accounts[0]})
    except Exception as e:
        print(repr(e))

    with reverts("Pausable: paused"):
        dexilon_bridge.pause.call({"from": accounts[0]})


def test_pause_revert_on_deposit_when_paused(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 100 * 10 ** 18

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.deposit.call(dxln_token, amount, {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("Pausable: paused"):
        dexilon_bridge.deposit.call(dxln_token, amount, {"from": accounts[1]})


def test_pause_revert_on_withdraw_when_paused(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.withdraw.call(dxln_token, {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("Pausable: paused"):
        dexilon_bridge.withdraw.call(dxln_token, {"from": accounts[1]})


def test_pause_change_state_to_unpaused(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    dexilon_bridge.unpause({"from": accounts[0]})

    assert dexilon_bridge.paused() == False
