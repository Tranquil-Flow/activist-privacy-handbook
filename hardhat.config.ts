import { HardhatUserConfig } from "hardhat/config";
import "@oasisprotocol/sapphire-hardhat";
import "@nomicfoundation/hardhat-toolbox";

const accounts = process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : undefined;

const config: HardhatUserConfig = {
  solidity: "0.8.28",
  networks: {
    sapphire: {
      url: "https://sapphire.oasis.io",
      chainId: 0x5afe,
      accounts,
    },
    "sapphire-testnet": {
      url: "https://testnet.sapphire.oasis.io",
      accounts,
      chainId: 0x5aff,
    },
    "sapphire-localnet": {
      // docker run -it -p8544-8548:8544-8548 ghcr.io/oasisprotocol/sapphire-localnet:latest-2025-05-03-gitf89e5f0@sha256:48f4c859d8cd8c10d0f5df0f43a47704c08377ce57259971ff214a5fcf95cc20
      url: "http://localhost:8545",
      chainId: 0x5afd,
      accounts,
    },
  }
};

export default config;