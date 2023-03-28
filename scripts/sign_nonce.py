from web3.auto import w3
from eth_account.messages import encode_defunct
from eth_keys import keys

nonce = 1

pk1 = keys.PrivateKey(bytes.fromhex("12345678" * 8))

print("Your real address:", pk1.public_key.to_checksum_address())

# signing response
signature = w3.eth.account.sign_message(
    encode_defunct(nonce), private_key=pk1
).signature

# checking if you really signed it
print(
    "   From signature:",
    w3.eth.account.recover_message(encode_defunct(nonce), signature=signature),
)
