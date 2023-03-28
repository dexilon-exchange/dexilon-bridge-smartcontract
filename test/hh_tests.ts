import hre from 'hardhat'
import { ethers, Wallet } from "ethers";
import '@nomiclabs/hardhat-ethers'
import { time, loadFixture } from "@nomicfoundation/hardhat-network-helpers";
import { expect } from "chai";
import { keccak256 as solidityKeccak256 } from "@ethersproject/solidity";
const ethSigUtil = require('eth-sig-util');


const EIP712Domain = [
    { name: 'name', type: 'string' },
    { name: 'version', type: 'string' },
    { name: 'chainId', type: 'uint256' },
    { name: 'verifyingContract', type: 'address' },
];

async function domainSeparator(name, version, chainId, verifyingContract) {
    return '0x' + ethSigUtil.TypedDataUtils.hashStruct(
        'EIP712Domain',
        { name, version, chainId, verifyingContract },
        { EIP712Domain },
    ).toString('hex');
}


async function getSignature(wallet: Wallet, data: any): Promise<string> {
    // domainSeparator, token, addresses, amounts, id 
    const dataStructure = ["bytes32", "address", "address[]", "uint256[]", "uint256"];
    const solidityKeccak256Hash = solidityKeccak256(dataStructure, data);
    // console.log({ solidityKeccak256Hash });

    const messageHash = solidityKeccak256Hash;
    // console.log({ messageHash });
    let messageHashBytes = ethers.utils.arrayify(messageHash);

    const sign = await wallet.signMessage(messageHashBytes);
    // console.log({ sign, messageHash, data });

    return sign;
}

describe("Bridge contract", function () {

    let dexilonBridge;
    let usdt;
    let owner;
    let alice;
    let bob;
    let validatorsAddresses;
    let validatorsKeys;

    beforeEach(async function setTestingEnvironment() {

        [owner, alice, bob] = await hre.ethers.getSigners();

        const Token = await hre.ethers.getContractFactory("contracts/Mocks/USDT.sol:TetherUSD");
        usdt = await Token.deploy();

        const Bridge = await hre.ethers.getContractFactory("contracts/bridge.sol:DexilonBridge_v10");
        dexilonBridge = await Bridge.deploy("Dexilon", "test");
        await dexilonBridge.setSupportedToken(usdt.address, true);

        validatorsAddresses = [
            "0x627306090abab3a6e1400e9345bc60c78a8bef57",
            "0xf17f52151ebef6c7334fad080c5704d77216b732",
            "0xc5fdf4076b8f3a5357c5e395ab970b5b54098fef",
            "0x821aea9a577a9b44299b9c15c88cf3087f3b5544",
            "0x0d1d4e623d10f9fba5db95830f7d3839406c6af2",
            "0x2932b7a2355d6fecc4b5c0b6bd44cc31df247a2e",
            "0x2191ef87e392377ec08e7c08eb105ef5448eced5",
            "0x0f4f2ac550a1b4e2280d04c21cea7ebd822934b5",
            "0x6330a553fc93768f612722bb8c2ec78ac90b3bbc",
            "0x5aeda56215b167893e80b4fe645ba6d5bab767de",
            String(owner.address),
        ]
        // convert addresses to checksum addresses
        validatorsAddresses.forEach((name: string, index: number) => validatorsAddresses[index] = ethers.utils.getAddress(name));

        validatorsKeys = [
            "c87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3",
            "ae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f",
            "0dbbe8e4ae425a6d2687f1a7e3ba17bc98c673636790f1b8ad91193c05875ef1",
            "c88b703fb08cbea894b6aeff5a544fb92e78a18e19814cd85da83b71f772aa6c",
            "388c684f0ba1ef5017716adb5d21a053ea8e90277d0868337519f97bede61418",
            "659cbb0e2411a44db63778987b1e22153c086a95eb6b18bdf89de078917abc63",
            "82d052c865f5763aad42add438569276c00d3d88a2d062d36b2bae914d58b8c8",
            "aa3680d5d48a8283413f7a108367c7299ca73f553735860a87b08f39395618b7",
            "0f62d96d6675f32685bbdb8ac13cda7c23436f63efbb9d07700d8669ff12b7c4",
            "8d5366123cb560bb606379f90a0bfd4769eecc0557f1b362dcae9012b548b1e5",
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80", // hardhat owner key
        ];

        await dexilonBridge.addValidators(validatorsAddresses);

        await usdt.approve(dexilonBridge.address, 100_000_000_000)
        await dexilonBridge.deposit(usdt.address, 100_000_000_000)
    });


    describe("Deployment tests", function () {

        it("Deployment should assign the owner", async function () {
            expect(await dexilonBridge.owner()).to.equal(owner.address);
        });

        it("USDT must be the supported token", async function () {
            expect(String(await dexilonBridge.getSupportedTokens())).to.equal(usdt.address);
        });

        it("USDT must be already locked in the contract", async function () {
            expect(await dexilonBridge.getLockedBalance(usdt.address)).to.equal(100_000_000_000);
        });

        it("Available balance should be zero", async function () {
            expect(await dexilonBridge.getAvailableBalance(usdt.address, owner.address)).to.equal(0);
            expect(await dexilonBridge.getAvailableBalance(usdt.address, alice.address)).to.equal(0);
            expect(await dexilonBridge.getAvailableBalance(usdt.address, bob.address)).to.equal(0);
        });
    });

    describe("Only owner tests", function () {

        it("Should not allow set tokens", async function () {
            await expect(dexilonBridge.connect(bob).setSupportedToken(bob.address, true)).to.be.revertedWith(
                "Ownable: caller is not the owner"
            );
        });

        it("Should not allow add validators", async function () {
            await expect(dexilonBridge.connect(bob).addValidators([bob.address])).to.be.revertedWith(
                "Ownable: caller is not the owner"
            );
        });

        it("Should not allow remove validators", async function () {
            await expect(dexilonBridge.connect(bob).removeValidators([owner.address])).to.be.revertedWith(
                "Ownable: caller is not the owner"
            );
        });

        it("Should not allow pause", async function () {
            await expect(dexilonBridge.connect(bob).pause()).to.be.revertedWith(
                "Ownable: caller is not the owner"
            );
        });

        it("Should not allow unpause", async function () {
            await dexilonBridge.pause()
            await expect(dexilonBridge.connect(bob).unpause()).to.be.revertedWith(
                "Ownable: caller is not the owner"
            );
        });

    });

    describe("Validators tests", function () {

        it("All validators must be set", async function () {
            expect(await dexilonBridge.getActiveValidators()).to.deep.equal(validatorsAddresses);
        });

        it("Add new validator", async function () {
            await dexilonBridge.addValidators([alice.address]);
            const activeValidators = await dexilonBridge.getActiveValidators();
            expect(activeValidators[activeValidators.length - 1]).to.equal(alice.address);
        });

        it("Remove new validator", async function () {
            await dexilonBridge.addValidators([alice.address]);
            await dexilonBridge.removeValidators([alice.address]);
            const activeValidators = await dexilonBridge.getActiveValidators();
            expect(activeValidators[activeValidators.length - 1]).to.equal(owner.address);
        });

        it("Add existing validator to no effect", async function () {
            await dexilonBridge.addValidators([owner.address]);
            expect(await dexilonBridge.getActiveValidators()).to.deep.equal(validatorsAddresses);
        });

        it("Remove unexisting validator to no effect", async function () {
            await dexilonBridge.removeValidators([alice.address]);
            expect(await dexilonBridge.getActiveValidators()).to.deep.equal(validatorsAddresses);
        });

        it("Should revert add validator address(0)", async function () {
            await expect(dexilonBridge.addValidators([ethers.constants.AddressZero])).to.be.revertedWith(
                "Cannot be zero address!"
            );
        });

    });

    describe("Set supported tokens tests", function () {

        it("Should not allow zero address token", async function () {
            await expect(dexilonBridge.setSupportedToken(ethers.constants.AddressZero, true)).to.be.revertedWith(
                "Zero token address!"
            );
        });

        it("Should add existing token to no effect", async function () {
            expect(String(await dexilonBridge.getSupportedTokens())).to.equal(usdt.address);
            await dexilonBridge.setSupportedToken(usdt.address, true);
            expect(String(await dexilonBridge.getSupportedTokens())).to.equal(usdt.address);
        });

        it("Should turn off the only one supported token", async function () {
            await dexilonBridge.setSupportedToken(usdt.address, false);
            expect(String(await dexilonBridge.getSupportedTokens())).to.equal("");
        });

        it("Should add tokens and return a valid list", async function () {
            await dexilonBridge.setSupportedToken(usdt.address, true);
            await dexilonBridge.setSupportedToken(alice.address, true);
            await dexilonBridge.setSupportedToken(bob.address, true);
            expect(await dexilonBridge.getSupportedTokens()).to.deep.equal([usdt.address, alice.address, bob.address]);
        });

        it("Should turn off just one supported token", async function () {
            await dexilonBridge.setSupportedToken(alice.address, true);
            await dexilonBridge.setSupportedToken(bob.address, true);
            await dexilonBridge.setSupportedToken(bob.address, false);
            expect(await dexilonBridge.getSupportedTokens()).to.have.members([usdt.address, alice.address]);
        });

    });


    describe("Deposit tests", function () {
        it("Should not allow not supported tokens", async function () {
            await expect(dexilonBridge.deposit(bob.address, 1000)).to.be.rejectedWith("Token not supported!");
        });
        it("Make another owner deposit", async function () {
            await usdt.approve(dexilonBridge.address, 100_000_000_000);
            await dexilonBridge.deposit(usdt.address, 100_000_000_000);
            expect(await dexilonBridge.getAvailableBalance(usdt.address, owner.address)).to.equal(0);
        });
        it("Should not allow deposit when paused", async function () {
            await dexilonBridge.pause();
            await expect(dexilonBridge.deposit(bob.address, 1000)).to.be.rejectedWith("Pausable: paused");
        });
    });

    describe("Batch tests", function () {

        it("Should only allow validators", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, usdt.address, [bob.address], [1000], 69];
            var signatures = new Array();
            signatures.push(await getSignature(bob, data));
            await expect(dexilonBridge.connect(bob).batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Only validator!");
        });

        it("Should be more than 2 validators set", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, usdt.address, [bob.address], [1000], 69];
            var signatures = new Array();
            for (const validator of validatorsKeys) {
                const wallet = new Wallet(
                    validator, hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }

            await dexilonBridge.removeValidators(validatorsAddresses.slice(0, -2));

            await expect(dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Not enough validators!");
        });

        it("Should not accept same batch id", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, usdt.address, [bob.address], [1000], 69];
            var signatures = new Array();
            for (const validator of validatorsKeys) {
                const wallet = new Wallet(
                    validator, hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }

            await dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            );

            await expect(dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Batch already recorded!");
        });

        it("Should not accept wrong lists in a batch", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, usdt.address, [bob.address, alice.address], [1000], 69];
            var signatures = new Array();
            for (const validator of validatorsKeys) {
                const wallet = new Wallet(
                    validator, hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }

            await expect(dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Lists length do not match!");
        });

        it("Should not accept copies of the same signature", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, usdt.address, [bob.address], [1000], 69];
            var signatures = new Array();
            for (const validator of validatorsKeys) {
                const wallet = new Wallet(
                    validatorsKeys[0], hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }

            await expect(dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Not enough signatures!");
        });

        it("Should not accept wrong signatures", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, usdt.address, [bob.address], [1000], 69];
            var signatures = new Array();
            for (const validator of validatorsKeys.slice(0, 7)) {
                const wallet = new Wallet(
                    validatorsKeys[0], hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }
            signatures.push(await getSignature(alice, data))
            signatures.push(await getSignature(bob, data))

            await expect(dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Not enough signatures!");
        });

        it("Should be enough locked token in the contract", async function () {
            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);
            const data = [domain, alice.address, [bob.address], [1000], 69];
            var signatures = new Array();
            for (const validator of validatorsKeys) {
                const wallet = new Wallet(
                    validator, hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }

            await expect(dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            )).to.be.rejectedWith("Not enough locked token!");
        });

        it("Sign a batch by all validators", async function () {

            const domain = await domainSeparator("Dexilon", "test", 1337, dexilonBridge.address);

            // batch data
            const data = [domain, usdt.address, ["0x61a21F7D18DFB4CB16f132c0D330536705c34068"], [1000], 69];

            var signatures = new Array();
            for (const validator of validatorsKeys) {
                const wallet = new Wallet(
                    validator, hre.ethers.provider
                );
                signatures.push(await getSignature(wallet, data));
            }

            await dexilonBridge.batchUpdateAvailableBalances(
                data[1], data[2], data[3], data[4], signatures
            );

            expect(await dexilonBridge.getAvailableBalance(usdt.address, "0x61a21F7D18DFB4CB16f132c0D330536705c34068"
            )).to.equal(999);
        });
    });
});