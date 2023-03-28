from brownie import TetherUSD, Contract, network, config, accounts

from web3 import Web3
import time


def main():

    account = accounts.add(config["wallets"]["from_key"])

    # Deploying USDT
    usdt = TetherUSD.deploy({"from": account})

    print(f"USDT address: {usdt.address}")

    time.sleep(1)


if __name__ == "__main__":
    main()
    # run with
    # brownie run .\scripts\usdt_deploy.py --network mumbai
