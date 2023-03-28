from brownie import VerifySignature, accounts, reverts
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random


# START ======================== TESTS WITHDRAW =================================


def test_withdraw_deposit_usdc_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 6
    old_locked = dexilon_bridge.getLockedBalance(usdc_token)

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[1]})
    dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[1]})

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[2]})
    dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[2]})

    assert old_locked + amount * 2 == dexilon_bridge.getLockedBalance(usdc_token)


def test_withdraw_deposit_dxln_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 18
    old_locked = dexilon_bridge.getLockedBalance(dxln_token)

    dxln_token.approve(dexilon_bridge, amount, {"from": accounts[1]})
    dexilon_bridge.deposit(dxln_token, amount, {"from": accounts[1]})

    dxln_token.approve(dexilon_bridge, amount, {"from": accounts[2]})
    dexilon_bridge.deposit(dxln_token, amount, {"from": accounts[2]})

    assert old_locked + amount * 2 == dexilon_bridge.getLockedBalance(dxln_token)


def test_withdraw_batch_add_available_usdc(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 500 * 10 ** 6
    initial_locked = dexilon_bridge.getLockedBalance(usdc_token)

    batch_users = [
        accounts[1].address,
        accounts[2].address,
    ]
    batch_balances = [
        amount,
        amount,
    ]
    batchId = 100_123
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:8]:
        signatures.append(
            w3.eth.account.sign_message(
                encode_defunct(base_message), private_key=pk
            ).signature
        )
    dexilon_bridge.batchUpdateAvailableBalances(
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    )

    assert batch_balances[0] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[0]
    )
    assert batch_balances[1] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[1]
    )
    assert initial_locked == 2 * amount + dexilon_bridge.getLockedBalance(usdc_token)


def test_withdraw_batch_add_available_dxln(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 500 * 10 ** 18
    initial_locked = dexilon_bridge.getLockedBalance(dxln_token)

    batch_users = [
        accounts[1].address,
        accounts[2].address,
    ]
    batch_balances = [
        amount,
        amount,
    ]
    batchId = 100_123
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, dxln_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:8]:
        signatures.append(
            w3.eth.account.sign_message(
                encode_defunct(base_message), private_key=pk
            ).signature
        )
    dexilon_bridge.batchUpdateAvailableBalances(
        dxln_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    )

    assert batch_balances[0] == dexilon_bridge.getAvailableBalance(
        dxln_token.address, batch_users[0]
    )
    assert batch_balances[1] == dexilon_bridge.getAvailableBalance(
        dxln_token.address, batch_users[1]
    )
    assert initial_locked == 2 * amount + dexilon_bridge.getLockedBalance(dxln_token)


def test_withdraw_revert_wrong_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    wrong_token = accounts[5].address

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.withdraw(wrong_token, {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("No balance!"):
        dexilon_bridge.withdraw.call(wrong_token, {"from": accounts[1]})


def test_withdraw_revert_no_balance(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.withdraw(dxln_token, {"from": accounts[3]})
    except Exception as e:
        print(repr(e))

    with reverts("No balance!"):
        dexilon_bridge.withdraw.call(dxln_token, {"from": accounts[3]})


def test_withdraw_initiate_withdraw_usdc(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    balance1_before = usdc_token.balanceOf(accounts[1])
    balance2_before = usdc_token.balanceOf(accounts[2])

    dexilon_bridge.withdraw(usdc_token, {"from": accounts[1]})
    dexilon_bridge.withdraw(usdc_token, {"from": accounts[2]})

    balance1_after = usdc_token.balanceOf(accounts[1])
    balance2_after = usdc_token.balanceOf(accounts[2])

    assert balance1_after > 0
    assert balance2_after > 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[1]) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[2]) == 0


def test_withdraw_initiate_withdraw_dxln(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    balance1_before = dxln_token.balanceOf(accounts[1])
    balance2_before = dxln_token.balanceOf(accounts[2])

    dexilon_bridge.withdraw(dxln_token, {"from": accounts[1]})
    dexilon_bridge.withdraw(dxln_token, {"from": accounts[2]})

    balance1_after = dxln_token.balanceOf(accounts[1])
    balance2_after = dxln_token.balanceOf(accounts[2])

    assert balance1_after > 0
    assert balance2_after > 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[1]) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[2]) == 0
