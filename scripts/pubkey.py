from eth_keys import keys
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY1 = os.getenv("PRIVATE_KEY")[2:]
PRIVATE_KEY2 = os.getenv("PRIVATE_KEY2")[2:]

pk1 = keys.PrivateKey(bytes.fromhex(PRIVATE_KEY1))
pk2 = keys.PrivateKey(bytes.fromhex(PRIVATE_KEY2))

print("Private 1:", pk1)
print("Public  1:", pk1.public_key)
print("Address 1:", pk1.public_key.to_checksum_address())
print("Private 2:", pk2)
print("Public  2:", pk2.public_key)
print("Address 2:", pk2.public_key.to_checksum_address())
# print(Web3.toBytes(hexstr=PRIVATE_KEY2))
