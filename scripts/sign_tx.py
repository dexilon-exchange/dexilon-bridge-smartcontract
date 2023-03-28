from brownie import DexilonBridge_v02, VerifySignature, accounts
from eth_keys import keys
from web3 import Web3
from web3.auto import w3
from eth_account.messages import encode_defunct, _hash_eip191_message
import os
from dotenv import load_dotenv


def sign_one_tx():

    load_dotenv()
    PRIVATE_KEY1 = os.getenv("PRIVATE_KEY")[2:]
    pk1 = keys.PrivateKey(bytes.fromhex(PRIVATE_KEY1))

    # account = accounts.add(config["wallets"]["from_key"])
    account = accounts.add(pk1)

    user_address = account
    new_balance = 1_000

    verify_contract = VerifySignature.deploy({"from": account})
    dexilon_bridge = DexilonBridge_v02.deploy({"from": account})

    print("===Tx hash:")
    tx_hash = verify_contract.getMessageHash(user_address, new_balance, "")
    tx_hash = str(tx_hash)
    print(tx_hash)
    print(dexilon_bridge.getHash(user_address, new_balance))
    base_message = Web3.soliditySha3(
        ["address", "uint256"],
        [Web3.toChecksumAddress(user_address.address), new_balance],
    )
    print(base_message.hex())

    print("===Getting signature:")
    signed = account.sign_defunct_message(tx_hash)
    sign_hex = signed.signature.hex()
    print(sign_hex)
    signed_message = w3.eth.account.sign_message(
        encode_defunct(text=tx_hash), private_key=pk1
    )
    signature = signed_message.signature.hex()
    print(signature)
    print(w3.eth.account.sign_message(encode_defunct(base_message), private_key=pk1))
    # WORKING SIGNATURE
    signature = w3.eth.account.sign_message(
        encode_defunct(base_message), private_key=pk1
    ).signature

    print("===Signed hash:")
    # eth-style hash
    tx_signed_hash = signed_message.messageHash.hex()
    tx_eth_hash = str(dexilon_bridge.getEthHash(base_message))
    print(tx_signed_hash)
    print(tx_eth_hash)
    print(dexilon_bridge.getEthHashFromTx(user_address, new_balance))
    print(dexilon_bridge.getEthSignedMessageHash(base_message))
    print(Web3.toHex(_hash_eip191_message(encode_defunct(base_message))))

    print("===From web3:")
    print(
        w3.eth.account.recover_message(
            encode_defunct(base_message), signature=signature
        )
    )
    print("===From dexilon:")
    print(dexilon_bridge.recoverAddress(tx_signed_hash, signature))
    print(dexilon_bridge.recoverAddress(tx_hash, signature))
    print(dexilon_bridge.recoverAddress(tx_eth_hash, signature))

    # signature = pk1.sign_msg(tx_hash.encode("utf-8"))
    # print(signature)

    tx = verify_contract.verify(
        account,
        user_address,
        new_balance,
        "",
        signature,
    )
    print("===Verified:", tx)

    print("===Real Address:", user_address)
    # print(" from public:", pk1.public_key.to_checksum_address())
    print(w3.eth.account.recoverHash(tx_hash, signature=signature))
    print(w3.eth.account.recoverHash(tx_eth_hash, signature=signature))
    print(w3.eth.account.recoverHash(tx_signed_hash, signature=signature))
    print(
        "===   recovered:",
        verify_contract.recoverSigner(
            tx_eth_hash,
            signature,
        ),
    )

    quit()

    # Deploying Bridge Contract
    dexilon_bridge = DexilonBridge_v02.deploy({"from": account})

    # tx = dexilon_bridge.storePublicKey(
    #     "0x1e0251778915fc6a6afe52ee54a1d81c00e1f2e577281d8440b1ffce00662a54796ef645406342fa4231d01f6eeb7cedd383d68274739a1e6607502b93f81248",
    #     {"from": account},
    # )
    # tx.wait(1)

    print(dexilon_bridge.getPublicKey(account))

    # Trading balance change
    print("Account trading balance:", dexilon_bridge.usersTradingBalances(account))

    user_address = account
    new_balance = 1_000

    tx_hash = dexilon_bridge.getHash(user_address, new_balance)
    tx_hash = str(tx_hash)
    print(tx_hash)
    signed = account.sign_defunct_message(tx_hash)
    sign_hex = signed.signature.hex()
    print(sign_hex, len(sign_hex))

    print(user_address)
    print(dexilon_bridge.recoverAddress(tx_hash, sign_hex))

    # tx = dexilon_bridge.updateTradingBalance(
    #     user_address, new_balance, sign_hex, user_address
    # )
    # tx.wait(1)

    # print('Account trading balance:', dexilon_bridge.usersTradingBalances(account))


def batch_sign():

    load_dotenv()
    PRIVATE_KEY1 = os.getenv("PRIVATE_KEY")[2:]
    pk1 = keys.PrivateKey(bytes.fromhex(PRIVATE_KEY1))

    account = accounts.add(pk1)

    user_address = Web3.toChecksumAddress(account.address)
    new_balance_1 = 1_000
    new_balance_2 = 2_000
    new_balance_3 = 3_000

    dexilon_bridge = DexilonBridge_v02.deploy({"from": account})

    users_array = [user_address, user_address, user_address]
    balances_array = [new_balance_1, new_balance_2, new_balance_3]

    print("Off-chain batch hash:")
    base_message = Web3.solidityKeccak(
        ["address[]", "uint256[]"],
        [
            users_array,
            balances_array,
        ],
    )
    print(base_message.hex())
    print("On-chain batch hash:")
    print(
        dexilon_bridge.getHashForBatch(
            users_array,
            balances_array,
        )
    )

    # WORKING SIGNATURE
    signature = w3.eth.account.sign_message(
        encode_defunct(base_message), private_key=pk1
    ).signature
    print("Real address:")
    print(account)
    print("Recovered address from contract:")
    print(dexilon_bridge.recoverAddressForBatch(users_array, balances_array, signature))


def main():

    # sign_one_tx()

    batch_sign()


if __name__ == "__main__":
    main()
