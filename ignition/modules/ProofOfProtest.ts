import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("ProofOfProtest", (m) => {
  const proofOfProtest = m.contract("ProofOfProtest");

  return { proofOfProtest };
}); 