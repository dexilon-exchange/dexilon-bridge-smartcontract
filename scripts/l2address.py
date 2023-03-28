from brownie import DexilonBridge_v05, Contract, network, config, accounts

from web3 import Web3
import time
import json


def main():

    # account = accounts.add(config["wallets"]["from_key"])
    # l2Address = "cosmos1wtzhzlj4vqjauvzme87m3grj2j53wmfld4x5ht"

    # with open("bridge_v03_abi.json") as f:
    #     abi = json.load(f)
    # dexilon_bridge = Contract.from_abi(
    #     "DexilonBridge_v04", "0x323D10186116a3B1e9230DBA5Abb254d4A7df119", abi
    # )
    # tx = dexilon_bridge.storeL2Address(l2Address, {"from": account})
    # tx.wait(1)
    # print("Address:", account.address)
    # print("L2:", dexilon_bridge.getL2Address(account.address))
    # print("L1:", dexilon_bridge.getL1Address(l2Address))
    # quit()

    account = accounts[0]

    # Deploying Bridge Contract
    dexilon_bridge = DexilonBridge_v05.deploy({"from": account})

    l2Address = "cosmos1wtzhzlj4vqjauvzme87m3grj2j53wmfld4x5ht"
    print("Storing L2 address:", l2Address)
    tx = dexilon_bridge.storeL2Address(l2Address, {"from": account})
    tx.wait(1)
    print("Reading L2 address:")
    print(dexilon_bridge.getL2Address(account))

    l2Address2 = "cosmos1yl6hdjhmkf37639730gffanpzndzdpmhwlkfhr"
    print("Storing another L2 address:", l2Address2)
    tx = dexilon_bridge.storeL2Address(l2Address2, {"from": accounts[1]})
    tx.wait(1)
    print("Reading L2 address 2:")
    print(dexilon_bridge.getL2Address(accounts[1]))

    print("Reading L1 addresses:")
    print(l2Address, dexilon_bridge.getL1Address(l2Address))
    print(l2Address2, dexilon_bridge.getL1Address(l2Address2))

    for i in range(8):
        dexilon_bridge.storeL2Address(l2Address2, {"from": accounts[i + 2]})

    print("Hard reset...")
    tx = dexilon_bridge.stateHardReset({"from": account})
    tx.wait(1)
    print(tx.events)

    print("Reading L2 address 2:")
    print(dexilon_bridge.getL2Address(accounts[1]))

    print("Reading L1 addresses:")
    print(l2Address, dexilon_bridge.getL1Address(l2Address))
    print(l2Address2, dexilon_bridge.getL1Address(l2Address2))


if __name__ == "__main__":
    main()
    # run with
    # brownie run .\scripts\l2address.py --network mumbai
