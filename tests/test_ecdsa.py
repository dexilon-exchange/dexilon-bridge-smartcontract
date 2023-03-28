from brownie import accounts, reverts
from eth_keys import keys
from eth_account.messages import encode_defunct, _hash_eip191_message
from brownie.network.state import Chain

from web3 import Web3
from web3.auto import w3
import pytest
import random
from hexbytes import HexBytes


# START ======================== TESTS ECDSA =================================

TEST_MESSAGE = Web3.keccak(text="OpenZeppelin").hex()
WRONG_MESSAGE = Web3.keccak(text="Nope").hex()
NON_HASH_MESSAGE = "0x" + "abcd".encode().hex()


def test_ecdsa_revert_short_signature(other_mocks):

    (ecdsa, address) = other_mocks

    with reverts("ECDSA: invalid signature length"):
        ecdsa.recover(TEST_MESSAGE, "0x1234")


def test_ecdsa_revert_long_signature(other_mocks):

    (ecdsa, address) = other_mocks

    with reverts("ECDSA: invalid signature length"):
        ecdsa.recover(TEST_MESSAGE, "0x" + "0123456789" * 10)


def test_ecsda_returns_signer_address_with_correct_signature(other_mocks, deploy):

    (ecdsa, address) = other_mocks
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    signature = w3.eth.account.sign_message(
        encode_defunct(hexstr=TEST_MESSAGE), private_key=private_keys[0]
    ).signature

    assert (
        ecdsa.recover(
            _hash_eip191_message(encode_defunct(hexstr=TEST_MESSAGE)), signature
        )
    ) == (pk_accounts[0].address)


def test_ecdsa_returns_different_address(other_mocks, deploy):

    (ecdsa, address) = other_mocks
    (dexilon_bridge, pk_accounts, private_keys, domainSeparator) = deploy

    signature = w3.eth.account.sign_message(
        encode_defunct(hexstr=TEST_MESSAGE), private_key=private_keys[0]
    ).signature

    assert (
        ecdsa.recover(
            _hash_eip191_message(encode_defunct(hexstr=WRONG_MESSAGE)), signature
        )
    ) != (pk_accounts[0].address)


def test_ecdsa_reverts_with_invalid_signature(other_mocks):

    (ecdsa, address) = other_mocks

    signature = "0x332ce75a821c982f9127538858900d87d3ec1f9f737338ad67cad133fa48feff48e6fa0c18abc62e42820f05943e47af3e9fbe306ce74d64094bdf1691ee53e01c"

    with reverts("ECDSA: invalid signature"):
        ecdsa.recover(TEST_MESSAGE, signature)


def test_ecdsa_reverts_version_00(other_mocks):

    (ecdsa, address) = other_mocks

    signature = "0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be892"
    version = "00"
    signature = signature + version

    with reverts("ECDSA: invalid signature"):
        ecdsa.recover(TEST_MESSAGE, signature)


def test_ecdsa_works_with_version_1b(other_mocks):

    (ecdsa, address) = other_mocks
    signer = "0x2cc1166f6212628A0deEf2B33BEFB2187D35b86c"
    signature = "0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be892"
    version = "1b"
    signature = signature + version

    assert ecdsa.recover(TEST_MESSAGE, signature) == signer


def test_ecdsa_reverts_version_02(other_mocks):

    (ecdsa, address) = other_mocks

    signature = "0x5d99b6f7f6d1f73d1a26497f2b1c89b24c0993913f86e9a2d02cd69887d9c94f3c880358579d811b21dd1b7fd9bb01c1d81d10e69f0384e675c32b39643be892"
    version = "02"
    signature = signature + version

    with reverts("ECDSA: invalid signature"):
        ecdsa.recover(TEST_MESSAGE, signature)


def test_ecdsa_reverts_s_value(other_mocks):

    (ecdsa, address) = other_mocks

    message = "0xb94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    highSSignature = "0xe742ff452d41413616a5bf43fe15dd88294e983d3d36206c2712f39083d638bde0a0fc89be718fbc1033e1d30d78be1c68081562ed2e97af876f286f3453231d1b"

    with reverts("ECDSA: invalid signature 's' value"):
        ecdsa.recover(message, highSSignature)
