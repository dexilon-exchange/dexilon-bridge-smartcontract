from brownie import DexilonBridge_v10, Contract, network, config, accounts

from web3 import Web3
import time
import os


def main():

    PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

    account = accounts.add(PRIVATE_KEY)

    # Deploying Bridge Contract
    project_name = os.getenv("PROJECT_NAME")
    project_version = os.getenv("VERSION_NAME")
    dexilon_bridge = DexilonBridge_v10.deploy(
        project_name, project_version, {"from": account}
    )

    # // Test tokens (Mumbai)
    token_usdt = os.getenv("TOKEN_USDT")
    token_dxln = os.getenv("TOKEN_DXLN")
    tx = dexilon_bridge.setSupportedToken(token_usdt, True, {"from": account})
    tx = dexilon_bridge.setSupportedToken(token_dxln, True, {"from": account})

    new_owner = os.getenv("FINAL_OWNER_ADDRESS")

    tx = dexilon_bridge.transferOwnership(new_owner, {"from": account})
    tx.wait(1)

    print(f"Dexilon Bridge smart contract deployed at the address: {dexilon_bridge.address}")


if __name__ == "__main__":
    main()
