import { ethers } from 'hardhat';

async function main() {
  const [deployer] = await ethers.getSigners();
  const admin = deployer.address;
  const roflAppID = "0x000000000000000000000000000000000000000000"; // dummy roflAppID (bytes21)
  const DeadManSwitch = await ethers.getContractFactory('DeadManSwitch');
  const deadManSwitch = await DeadManSwitch.deploy(admin, roflAppID);
  await deadManSwitch.waitForDeployment();
  console.log('DeadManSwitch deployed to:', await deadManSwitch.getAddress());
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});