from brownie import accounts, reverts
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random
from hexbytes import HexBytes


# START ======================== TESTS VALIDATORS =================================


def test_validators_check_validators(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    assert dexilon_bridge.getActiveValidators() == pk_accounts


def test_validators_available_balance_before_deposit(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[0].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[1].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[2].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[3].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[4].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[0].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[1].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[2].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[3].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[4].address) == 0


def test_validators_deposit_usdc_token(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    amount = 1_000 * 10 ** 6
    old_balance = dexilon_bridge.getLockedBalance(usdc_token)

    usdc_token.approve(dexilon_bridge, amount, {"from": accounts[1]})
    dexilon_bridge.deposit(usdc_token, amount, {"from": accounts[1]})

    assert amount + old_balance == dexilon_bridge.getLockedBalance(usdc_token)


def test_validators_available_balance_after_deposit(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[0].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[1].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[2].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[3].address) == 0
    assert dexilon_bridge.getAvailableBalance(usdc_token, accounts[4].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[0].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[1].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[2].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[3].address) == 0
    assert dexilon_bridge.getAvailableBalance(dxln_token, accounts[4].address) == 0


def test_validators_remove_validators(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    dexilon_bridge.removeValidators(pk_accounts[:-1], {"from": accounts[0]})

    assert dexilon_bridge.getActiveValidators() == pk_accounts[-1:]


def test_validators_revert_not_enough_validators(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be8921b"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough validators!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_validators_add_again_validators(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    dexilon_bridge.addValidators(pk_accounts[:-1], {"from": accounts[0]})

    assert sorted(dexilon_bridge.getActiveValidators()) == sorted(
        [acc.address for acc in pk_accounts]
    )


def test_validators_add_same_validator(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    dexilon_bridge.addValidators(
        [pk_accounts[0], pk_accounts[0], pk_accounts[0]], {"from": accounts[0]}
    )

    assert sorted(dexilon_bridge.getActiveValidators()) == sorted(
        [acc.address for acc in pk_accounts]
    )


def test_validators_remove_and_add_same_validator(deploy):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    dexilon_bridge.removeValidators([pk_accounts[0]], {"from": accounts[0]})
    dexilon_bridge.addValidators([pk_accounts[0]], {"from": accounts[0]})

    assert sorted(dexilon_bridge.getActiveValidators()) == sorted(
        [acc.address for acc in pk_accounts]
    )


def test_validators_revert_add_unauthorized_validator(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.addValidators([accounts[1]], {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("Ownable: caller is not the owner"):
        dexilon_bridge.addValidators.call([accounts[1]], {"from": accounts[1]})


def test_validators_revert_remove_unauthorized_validator(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.removeValidators([pk_accounts[0]], {"from": accounts[1]})
    except Exception as e:
        print(repr(e))

    with reverts("Ownable: caller is not the owner"):
        dexilon_bridge.removeValidators.call([pk_accounts[0]], {"from": accounts[1]})


def test_validators_revert_add_zero_validator(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.addValidators(
            [accounts[1], "0x" + "0" * 40], {"from": accounts[0]}
        )
    except Exception as e:
        print(repr(e))

    with reverts("Cannot be zero address!"):
        dexilon_bridge.addValidators.call(
            [accounts[1], "0x" + "0" * 40], {"from": accounts[0]}
        )


def test_validators_remove_unexisting_validator(deploy):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    dexilon_bridge.removeValidators([accounts[7]], {"from": accounts[0]})

    assert sorted(dexilon_bridge.getActiveValidators()) == sorted(
        [acc.address for acc in pk_accounts]
    )
