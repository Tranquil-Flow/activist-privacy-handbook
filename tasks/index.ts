import { task } from "hardhat/config";

task("deploy").setAction(async (_args, hre) => {
  console.log("Starting deployment...");
  
  const ProofOfProtest = await hre.ethers.getContractFactory("ProofOfProtest");
  console.log("Contract factory created");
  
  // Get signer
  const [signer] = await hre.ethers.getSigners();
  console.log("Deploying from address:", signer.address);
  
  // Get balance
  const balance = await hre.ethers.provider.getBalance(signer.address);
  console.log("Deployer balance:", hre.ethers.formatEther(balance), "ROSE");
  
  try {
    // Get deployment transaction
    const deployTx = await ProofOfProtest.getDeployTransaction();
    console.log("Deployment transaction created");
    
    // Send transaction manually
    const tx = await signer.sendTransaction({
      ...deployTx,
      gasLimit: 2000000n,
      gasPrice: 200000000000n // 200 Gwei
    });
    
    console.log("Deployment transaction sent:", tx.hash);
    
    // Wait for transaction receipt
    const receipt = await tx.wait();
    if (!receipt) {
      throw new Error("Transaction receipt is null");
    }
    
    console.log("Transaction mined in block:", receipt.blockNumber);
    
    if (!receipt.contractAddress) {
      throw new Error("No contract address in receipt");
    }
    
    console.log(`ProofOfProtest deployed to: ${receipt.contractAddress}`);
    return receipt.contractAddress;
  } catch (error: any) {
    console.error("Deployment failed with error:", error.message);
    if (error.receipt) {
      console.error("Transaction receipt:", error.receipt);
    }
    throw error;
  }
});

task("create-event")
  .addParam("address", "contract address")
  .addParam("name", "event name")
  .addParam("points", "comma-separated location points")
  .addParam("duration", "event duration in hours")
  .setAction(async (args, hre) => {
    const proofOfProtest = await hre.ethers.getContractAt("ProofOfProtest", args.address);
    
    const startTime = Math.floor(Date.now() / 1000);
    const endTime = startTime + (parseInt(args.duration) * 3600);
    const eventId = hre.ethers.keccak256(hre.ethers.toUtf8Bytes(args.name));
    const locationPoints = args.points.split(',').map((point: string) => point.trim());

    try {
      const tx = await proofOfProtest.createEvent(
        eventId,
        args.name,
        locationPoints,
        startTime,
        endTime
      );
      console.log("Creating event:", tx.hash);
      console.log("Event ID:", eventId);
    } catch (e: any) {
      console.error("Failed to create event:", e.message);
      process.exit(1);
    }
  });

task("mint-poap")
  .addParam("address", "contract address")
  .addParam("eventId", "event ID")
  .addParam("attendee", "attendee address")
  .addParam("tokenUri", "token URI")
  .addParam("geoHash", "geolocation hash")
  .setAction(async (args, hre) => {
    const proofOfProtest = await hre.ethers.getContractAt("ProofOfProtest", args.address);

    try {
      const tx = await proofOfProtest.mintPOAP(
        args.attendee,
        args.eventId,
        args.tokenUri,
        args.geoHash
      );
      console.log("Minting POAP:", tx.hash);
    } catch (e: any) {
      console.error("Failed to mint POAP:", e.message);
      process.exit(1);
    }
  });

task("verify-participation")
  .addParam("address", "contract address")
  .addParam("attendee", "attendee address")
  .addParam("eventId", "event ID")
  .setAction(async (args, hre) => {
    const proofOfProtest = await hre.ethers.getContractAt("ProofOfProtest", args.address);

    try {
      const hasPOAP = await proofOfProtest.hasPOAP(args.attendee, args.eventId);
      console.log("Has POAP:", hasPOAP);
    } catch (e: any) {
      console.error("Failed to verify participation:", e.message);
      process.exit(1);
    }
  });

task("full-demo").setAction(async (_args, hre) => {
  await hre.run("compile");

  const address = await hre.run("deploy");
  console.log("Contract deployed at:", address);

  // Create a test event
  await hre.run("create-event", {
    address,
    name: "Climate March",
    points: "Start Point, Mid Point, End Point",
    duration: "24"
  });

  // Get the event ID
  const eventId = hre.ethers.keccak256(hre.ethers.toUtf8Bytes("Climate March"));
  
  // Mint a POAP for a test attendee
  const [owner, attendee] = await hre.ethers.getSigners();
  await hre.run("mint-poap", {
    address,
    eventId,
    attendee: attendee.address,
    tokenUri: "ipfs://test-uri",
    geoHash: "0x1234567890123456789012345678901234567890123456789012345678901234"
  });

  // Verify participation
  await hre.run("verify-participation", {
    address,
    attendee: attendee.address,
    eventId
  });
});
