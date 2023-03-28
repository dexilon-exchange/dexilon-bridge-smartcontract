from brownie import accounts, reverts
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random
from hexbytes import HexBytes


# START ======================== TESTS BATCH =================================


def test_batch_sign_a_batch_by_all_validators(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    old_locked = dexilon_bridge.getLockedBalance(usdc_token)

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
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
    assert batch_balances[2] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[2]
    )
    assert old_locked == dexilon_bridge.getLockedBalance(usdc_token) + sum(
        batch_balances
    )


def test_batch_revert_only_validator(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 33
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
        {"from": accounts[6]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Only validator!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x332ce75a821c982f9127538858900d87d3ec1f9f737338ad67cad133fa48feff48e6fa0c18abc62e42820f05943e47af3e9fbe306ce74d64094bdf1691ee53e01c"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_value(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0xe742ff452d41413616a5bf43fe15dd88294e983d3d36206c2712f39083d638bde0a0fc89be718fbc1033e1d30d78be1c68081562ed2e97af876f286f3453231d1b"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature 's' value"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_v_00(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be89200"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_v_02(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be89202"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_v_1b(deploy, tokens):

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

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_v_b01(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x331fe75a821c982f9127538858900d87d3ec1f9f737338ad67cad133fa48feff48e6fa0c18abc62e42820f05943e47af3e9fbe306ce74d64094bdf1691ee53e001"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_v_b02(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x331fe75a821c982f9127538858900d87d3ec1f9f737338ad67cad133fa48feff48e6fa0c18abc62e42820f05943e47af3e9fbe306ce74d64094bdf1691ee53e002"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_v_b1c(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [
            HexBytes(
                "0x331fe75a821c982f9127538858900d87d3ec1f9f737338ad67cad133fa48feff48e6fa0c18abc62e42820f05943e47af3e9fbe306ce74d64094bdf1691ee53e01c"
            )
        ],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_length_short(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [HexBytes("0x01234567890")],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature length"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_invalid_signature_length_long(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    tx_data = [
        usdc_token.address,
        [accounts[0].address],
        [1001],
        444,
        [HexBytes("0x" + "01234567890" * 15)],
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature length"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_not_enough_signatures_5_of_10(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 101 + 1
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:5]:
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

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_abusing_one_signature(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 500
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:1]:
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
        signatures * 10,
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_not_enough_signatures_0_of_10(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 101 + 1
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []

    tx_data = [
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_not_enough_signatures_6_of_10(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 101 + 1
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:6]:
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

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_same_batchId(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 101
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:7]:
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

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Batch already recorded!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_wrong_signatures(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 101
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:7]:
        signatures.append(
            w3.eth.account.sign_message(
                encode_defunct(base_message), private_key=pk
            ).signature
        )

    tx_data = [
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId + 1111222,
        signatures,
        {"from": accounts[0]},
    ]
    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough signatures!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_incorrect_lists(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002]
    batchId = 101 + 1
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:7]:
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

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Lists length do not match!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_second_batch_is_added(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address, accounts[2].address]
    batch_balances = [1001, 1002, 1003]
    batchId = 101 + 1
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

    assert 2 * batch_balances[0] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[0]
    )
    assert 2 * batch_balances[1] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[1]
    )
    assert 2 * batch_balances[2] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[2]
    )


def test_batch_one_tx_batch(deploy, tokens):

    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [
        accounts[0].address,
    ]
    batch_balances = [
        1001,
    ]
    batchId = 101 + 2
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

    assert 3 * batch_balances[0] == dexilon_bridge.getAvailableBalance(
        usdc_token.address, batch_users[0]
    )
    assert 2 * 1002 == dexilon_bridge.getAvailableBalance(
        usdc_token.address, accounts[1].address
    )
    assert 2 * 1003 == dexilon_bridge.getAvailableBalance(
        usdc_token.address, accounts[2].address
    )


def test_batch_revert_incorrect_signature(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address]
    batch_balances = [1001, 1002]
    batchId = 77100
    base_message = Web3.solidityKeccak(
        ["bytes32", "address", "address[]", "uint256[]", "uint256"],
        [domainSeparator, usdc_token.address, batch_users, batch_balances, batchId],
    )

    signatures = []
    for pk in private_keys[:7]:
        signatures.append(
            w3.eth.account.sign_message(
                encode_defunct(base_message), private_key=pk
            ).signature
        )
    signatures.append("0x1234")

    tx_data = [
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("ECDSA: invalid signature length"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)


def test_batch_revert_not_enough_locked(deploy, tokens):
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy
    (usdc_token, dxln_token) = tokens

    batch_users = [accounts[0].address, accounts[1].address]
    batch_balances = [10001 * 10 ** 6, 10002 * 10 ** 6]
    batchId = 88100
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

    tx_data = [
        usdc_token.address,
        batch_users,
        batch_balances,
        batchId,
        signatures,
        {"from": accounts[0]},
    ]

    # maintain Anvil and coverage compatibility
    try:
        dexilon_bridge.batchUpdateAvailableBalances(*tx_data)
    except Exception as e:
        print(repr(e))

    with reverts("Not enough locked token!"):
        dexilon_bridge.batchUpdateAvailableBalances.call(*tx_data)
