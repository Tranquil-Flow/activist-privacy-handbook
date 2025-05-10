# ProofOfProtest

A privacy-preserving POAP (Proof of Attendance Protocol) system built on Oasis Sapphire for protest events. This system allows event organizers to mint verifiable attendance tokens while maintaining participant privacy.

## Features

- Privacy-preserving event registration
- Geolocation-based attendance verification
- Multi-event support
- Time-window based event validation
- Secure POAP minting and verification

## Prerequisites

- Node.js (v18 or later recommended)
- npm or yarn
- A wallet with ROSE tokens (for Sapphire testnet)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd activist-privacy-handbook
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory:
```
PRIVATE_KEY=your_private_key_here
```

## Usage

### Deployment

Deploy the contract to Sapphire testnet:
```bash
npx hardhat deploy --network sapphire-testnet
```

### Creating an Event

Create a new protest event:
```bash
npx hardhat create-event \
  --address <contract-address> \
  --name "Climate March" \
  --points "Start Point, Mid Point, End Point" \
  --duration 24
```

### Minting POAPs

Mint a POAP for an attendee:
```bash
npx hardhat mint-poap \
  --address <contract-address> \
  --eventId <event-id> \
  --attendee <attendee-address> \
  --tokenUri "ipfs://..." \
  --geoHash <geo-hash>
```

### Verifying Participation

Check if an address has a POAP for a specific event:
```bash
npx hardhat verify-participation \
  --address <contract-address> \
  --attendee <attendee-address> \
  --eventId <event-id>
```

### Full Demo

Run a complete demonstration of all features:
```bash
npx hardhat full-demo --network sapphire-testnet
```

## Contract Features

### Event Management
- Create events with custom time windows
- Define multiple location points for route verification
- Event status tracking (active/inactive)

### POAP System
- Privacy-preserving attendance verification
- Geolocation hash verification
- Unique token minting per event
- Token URI support for metadata

### Security Features
- Owner-only event creation and POAP minting
- Time-window validation
- Duplicate claim prevention
- POAP revocation capability

## Development

### Compile Contracts
```bash
npx hardhat compile
```

### Run Tests
```bash
npx hardhat test
```

### Clean Build
```bash
npx hardhat clean
```

## Network Configuration

The project is configured for three networks:
- `sapphire`: Oasis Sapphire mainnet
- `sapphire-testnet`: Oasis Sapphire testnet
- `sapphire-localnet`: Local development network

## Security Considerations

- Private keys should never be committed to the repository
- Always use environment variables for sensitive data
- Test thoroughly on testnet before mainnet deployment
- Consider gas costs and limits for all operations

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on Oasis Sapphire for privacy-preserving smart contracts
- Inspired by the need for privacy in protest movements
- Uses OpenZeppelin contracts for security
