import { ethers } from 'hardhat';

async function main() {
  // Get the contract factory
  const DeadManSwitch = await ethers.getContractFactory('DeadManSwitch');

  // Deploy the contract
  const deadManSwitch = await DeadManSwitch.deploy();

  // Get the deployed contract address
  const address = await deadManSwitch.getAddress();
  console.log('DeadManSwitch deployed to:', address);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}); 