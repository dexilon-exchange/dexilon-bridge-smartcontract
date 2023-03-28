import { ethers } from "hardhat";

async function main() {

    const USDT_ADDRESS = process.env.TOKEN_USDT;
    const DXLN_ADDRESS = process.env.TOKEN_DXLN;

    console.log(`Deployment in progress...`);

    const DexilonBridge = await ethers.getContractFactory("DexilonBridge_v10");
    const dexilonBridge = await DexilonBridge.deploy(process.env.PROJECT_NAME, process.env.VERSION_NAME);
    console.log(`  Contract deployed.`);

    await dexilonBridge.setSupportedToken(USDT_ADDRESS, true);
    await dexilonBridge.setSupportedToken(DXLN_ADDRESS, true);
    console.log(`  Supported tokens set.`);

    await dexilonBridge.transferOwnership(process.env.FINAL_OWNER_ADDRESS);
    console.log(`  Ownership transferred.`);

    console.log(`Deployment complete.`);
    console.log(`Dexilon Bridge smart contract deployed at the address: ${dexilonBridge.address}`);

}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});