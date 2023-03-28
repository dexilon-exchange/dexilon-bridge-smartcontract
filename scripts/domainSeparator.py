from web3 import Web3


def getDomainSeparator(
    name: str, version: str, chainid: int, contract_address: str
) -> str:
    """getDomainSeparator builds domain separator hash for input parameters

    Args:
        name (str): name of the project
        version (str): version of the project
        chainid (int): chain id of the blockchain
        address (str): address of the contract in the blockchain

    Returns:
        str: hex string of bytes32 hash
    """
    type_hash = Web3.keccak(
        text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    ).hex()
    name_hash = Web3.keccak(text=name).hex()
    version_hash = Web3.keccak(text=version).hex()

    local_abiencode = (
        str(type_hash)
        + str(name_hash).replace("0x", "")
        + str(version_hash).replace("0x", "")
        + str((chainid).to_bytes(32, byteorder="big").hex()).replace("0x", "")
        + "0" * 24
        + contract_address.lower().replace("0x", "")
    )
    domainSeparator = Web3.keccak(hexstr=local_abiencode).hex()

    return str(domainSeparator)


if __name__ == "__main__":
    print(
        "Ganache:",
        getDomainSeparator(
            "Dexilon", "dev2", 1337, "0x99dBE4AEa58E518C50a1c04aE9b48C9F6354612f"
        ),
    )
    print(
        "Mumbai:",
        getDomainSeparator(
            "Dexilon", "dev2", 80001, "0xd13b0091C8CFfC70CEEe9e8174529286965Ceb5B"
        ),
    )
