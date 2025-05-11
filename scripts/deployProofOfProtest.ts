import { ethers } from 'hardhat';

async function main() {
  const [deployer] = await ethers.getSigners();
  const admin = deployer.address;
  const ProofOfProtest = await ethers.getContractFactory('ProofOfProtest');
  const proofOfProtest = await ProofOfProtest.deploy();
  await proofOfProtest.waitForDeployment();
  console.log('ProofOfProtest deployed to:', await proofOfProtest.getAddress());
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});