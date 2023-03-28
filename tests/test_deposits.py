from brownie import VerifySignature, accounts, reverts
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random


# START ======================== TESTS DEPOSITS =================================


def test_deposits_supported_tokens_list(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    assert [token.address for token in tokens] == dexilon_bridge.getSupportedTokens()[
        -2:
    ]


def test_deposits_set_already_supported_token(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    supported_tokens_list = dexilon_bridge.getSupportedTokens()

    dexilon_bridge.setSupportedToken(usdc_token, True, {"from": accounts[0]})

    assert supported_tokens_list == dexilon_bridge.getSupportedTokens()


def test_deposits_remove_all_supported_tokens(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    supported_tokens_list = dexilon_bridge.getSupportedTokens()

    for token in supported_tokens_list:
        dexilon_bridge.setSupportedToken(token, False, {"from": accounts[0]})

    assert len(dexilon_bridge.getSupportedTokens()) == 0


def test_deposits_restore_supported_token(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    for token in tokens:
        dexilon_bridge.setSupportedToken(token, True, {"from": accounts[0]})

    assert tokens == dexilon_bridge.getSupportedTokens()


def test_deposits_set_new_supported_token_true(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    prev_number_of_tokens = len(dexilon_bridge.getSupportedTokens())
    dexilon_bridge.setSupportedToken(accounts[7], True, {"from": accounts[0]})

    assert prev_number_of_tokens + 1 == len(dexilon_bridge.getSupportedTokens())
    assert accounts[7] == dexilon_bridge.getSupportedTokens()[-1]


def test_deposits_set_supported_token_false(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    prev_number_of_tokens = len(dexilon_bridge.getSupportedTokens())
    dexilon_bridge.setSupportedToken(accounts[7], False, {"from": accounts[0]})

    assert prev_number_of_tokens - 1 == len(dexilon_bridge.getSupportedTokens())
    assert accounts[7] not in dexilon_bridge.getSupportedTokens()


def test_deposits_set_supported_tokens_revert_only_owner(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens
    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.setSupportedToken(dxln_token, True, {"from": accounts[3]})
    except Exception as e:
        print(repr(e))

    with reverts("Ownable: caller is not the owner"):
        dexilon_bridge.setSupportedToken.call(dxln_token, True, {"from": accounts[3]})


def test_deposits_set_supported_token_true_again(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    prev_number_of_tokens = len(dexilon_bridge.getSupportedTokens())
    dexilon_bridge.setSupportedToken(accounts[7], True, {"from": accounts[0]})

    assert prev_number_of_tokens + 1 == len(dexilon_bridge.getSupportedTokens())
    assert accounts[7] in dexilon_bridge.getSupportedTokens()


def test_deposits_set_supported_token_that_is_already_set(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    prev_number_of_tokens = len(dexilon_bridge.getSupportedTokens())
    dexilon_bridge.setSupportedToken(accounts[7], True, {"from": accounts[0]})

    assert prev_number_of_tokens == len(dexilon_bridge.getSupportedTokens())
    assert accounts[7] in dexilon_bridge.getSupportedTokens()


def test_deposits_remove_unsupported_token_to_no_effect(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    prev_number_of_tokens = len(dexilon_bridge.getSupportedTokens())
    dexilon_bridge.setSupportedToken(accounts[8], False, {"from": accounts[0]})

    assert prev_number_of_tokens == len(dexilon_bridge.getSupportedTokens())
    assert accounts[8] not in dexilon_bridge.getSupportedTokens()


def test_deposits_revert_zero_token(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.setSupportedToken("0x" + "0" * 40, True, {"from": accounts[0]})
    except Exception as e:
        print(repr(e))

    with reverts("Zero token address!"):
        dexilon_bridge.setSupportedToken.call(
            "0x" + "0" * 40, True, {"from": accounts[0]}
        )


def test_deposits_dexilon_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 18
    old_balance = dexilon_bridge.getLockedBalance(dxln_token)

    dxln_token.approve(dexilon_bridge, amount, {"from": accounts[1]})
    tx = dexilon_bridge.deposit(dxln_token, amount, {"from": accounts[1]})
    tx.wait(1)

    assert amount + old_balance == dexilon_bridge.getLockedBalance(dxln_token)


def test_deposits_usdc_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 6
    old_balance = dexilon_bridge.getLockedBalance(usdc_token)

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[1]})
    dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[1]})

    assert amount + old_balance == dexilon_bridge.getLockedBalance(usdc_token)


def test_deposits_revert_no_approve_usdc_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 6

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("ERC20: insufficient allowance"):
        dexilon_bridge.deposit.call(usdc_token, amount, {"from": accounts[1]})


def test_deposits_revert_not_enough_usdc_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 10_000_000 * 10 ** 6

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[5]})

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[5]})
    except Exception as e:
        print(repr(e))

    with reverts("ERC20: transfer amount exceeds balance"):
        dexilon_bridge.deposit.call(usdc_token, amount, {"from": accounts[5]})


def test_deposits_revert_not_valid_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.deposit(accounts[7], 10 ** 6, {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("Address: call to non-contract"):
        dexilon_bridge.deposit.call(accounts[7], 10 ** 6, {"from": accounts[1]})


def test_deposits_usdc_token_again(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 6
    old_balance = dexilon_bridge.getLockedBalance(usdc_token)

    batch_users = [accounts[1].address]
    batch_balances = [amount]
    batchId = 120101
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
    dexilon_bridge.batchUpdateAvailableBalances(
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    )

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[1]})
    dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[1]})

    assert old_balance == dexilon_bridge.getLockedBalance(usdc_token)


def test_deposits_revert_unsupported_token(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.deposit(accounts[3], 1_000 * 10 ** 6, {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("Token not supported!"):
        dexilon_bridge.deposit.call(accounts[3], 1_000 * 10 ** 6, {"from": accounts[1]})


def test_deposits_usdc_token_events(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    old_usdc_locked = dexilon_bridge.getLockedBalance(usdc_token)

    amount = 1_000 * 10 ** 6

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[2]})
    tx = dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[2]})
    tx.wait(1)

    assert old_usdc_locked + amount == dexilon_bridge.getLockedBalance(usdc_token)
    assert tx.events["Deposit"]["depositor"] == accounts[2].address
    assert tx.events["Deposit"]["token"] == usdc_token.address
    assert tx.events["Deposit"]["amount"] == amount
