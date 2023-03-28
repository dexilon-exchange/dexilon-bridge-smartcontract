require('@primitivefi/hardhat-dodoc');
require('solidity-coverage');
require('@nomicfoundation/hardhat-toolbox');
require("@nomicfoundation/hardhat-chai-matchers");
require("@nomiclabs/hardhat-ethers");

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.8.16",
  networks: {
    hardhat: {
      chainId: 1337,
    },
    mumbai: {
      url: `https://polygon-mumbai.g.alchemy.com/v2/YSB9dpzl-6DQcXynxssJXUHJQIAvIk5r`,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY],
      gas: 6000000
    }
  }
};
