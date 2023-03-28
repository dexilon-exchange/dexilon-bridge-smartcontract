from brownie import DexilonBridge_v10, Contract, network, config, accounts

from web3 import Web3
import time


def main():

    account = accounts.add(config["wallets"]["from_key"])

    # Deploying Bridge Contract
    project_name = "Dexilon"
    project_version = "dev2"
    dexilon_bridge = DexilonBridge_v10.deploy(
        project_name, project_version, {"from": account}
    )

    # // Test tokens (Mumbai)
    token_usdt = "0x8F54629e7D660871ABAb8a6B4809A839dEd396dE"
    token_dxln = "0x05D174c54bD2b48e99785F888045227fA03D37EE"
    dexilon_bridge.setSupportedToken(token_usdt, True, {"from": account})
    dexilon_bridge.setSupportedToken(token_dxln, True, {"from": account})

    antonkorpusenko_address = "0x90c39B275eBD973DCe691691B034303d09FC855a"

    tx = dexilon_bridge.transferOwnership(antonkorpusenko_address, {"from": account})
    tx.wait(1)


if __name__ == "__main__":
    main()
    # run with
    # brownie run .\scripts\mumbai_deploy.py --network mumbai
