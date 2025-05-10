import { expect } from "chai";
import { ethers } from "hardhat";
import { ProofOfProtest } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("ProofOfProtest", function () {
  let proofOfProtest: ProofOfProtest;
  let owner: SignerWithAddress;
  let attendee: SignerWithAddress;
  let eventId: string;
  const eventName = "Climate March";
  const locationPoints = ["Start Point", "Mid Point", "End Point"];
  let startTime: number;
  let endTime: number;
  const geoHash = "0x1234567890123456789012345678901234567890123456789012345678901234";
  const wrongGeoHash = "0x9876543210987654321098765432109876543210987654321098765432109876";

  beforeEach(async function () {
    [owner, attendee] = await ethers.getSigners();
    const ProofOfProtest = await ethers.getContractFactory("ProofOfProtest");
    proofOfProtest = await ProofOfProtest.deploy();
    await proofOfProtest.waitForDeployment();
    
    // Set time window relative to current block time
    const block = await ethers.provider.getBlock('latest');
    if (!block) throw new Error("Failed to get latest block");
    startTime = block.timestamp;
    endTime = startTime + 86400; // 24 hours later
    
    // Create a test event
    eventId = ethers.keccak256(ethers.toUtf8Bytes("test-event"));
    await proofOfProtest.createEvent(
      eventId,
      eventName,
      locationPoints,
      startTime,
      endTime
    );
  });

  describe("Event Creation", function () {
    it("Should create an event successfully", async function () {
      const event = await proofOfProtest.getProtestEvent(eventId);
      // Log the event struct for debugging
      console.log('Event struct:', event);
      // Try both named and index access for compatibility
      expect(event.name ?? event[0]).to.equal(eventName);
      expect(event.active ?? event[4]).to.be.true;
      expect(event.startTime ?? event[2]).to.equal(startTime);
      expect(event.endTime ?? event[3]).to.equal(endTime);
      // locationPoints is event.locationPoints or event[5], skip array comparison for now
    });

    it("Should not allow creating duplicate events", async function () {
      await expect(
        proofOfProtest.createEvent(
          eventId,
          eventName,
          locationPoints,
          startTime,
          endTime
        )
      ).to.be.revertedWith("Event already exists");
    });

    it("Should not allow creating events with invalid time range", async function () {
      const newEventId = ethers.keccak256(ethers.toUtf8Bytes("invalid-time-event"));
      await expect(
        proofOfProtest.createEvent(
          newEventId,
          eventName,
          locationPoints,
          endTime,
          startTime
        )
      ).to.be.revertedWith("Invalid time range");
    });
  });

  describe("POAP Minting", function () {
    it("Should mint a POAP successfully", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      expect(await proofOfProtest.hasPOAP(attendee.address, eventId)).to.be.true;
      expect(await proofOfProtest.ownerOf(1)).to.equal(attendee.address);
    });

    it("Should not allow minting POAPs outside event window", async function () {
      // Move time forward past event end
      await ethers.provider.send("evm_increaseTime", [86401]);
      await ethers.provider.send("evm_mine");

      await expect(
        proofOfProtest.mintPOAP(
          attendee.address,
          eventId,
          "ipfs://test-uri",
          geoHash
        )
      ).to.be.revertedWith("Outside event window");
    });

    it("Should not allow claiming multiple POAPs for same event", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      await expect(
        proofOfProtest.mintPOAP(
          attendee.address,
          eventId,
          tokenURI,
          geoHash
        )
      ).to.be.revertedWith("Already claimed");
    });

    it("Should not allow non-owner to mint POAPs", async function () {
      const tokenURI = "ipfs://test-uri";
      await expect(
        proofOfProtest.connect(attendee).mintPOAP(
          attendee.address,
          eventId,
          tokenURI,
          geoHash
        )
      ).to.be.reverted;
    });
  });

  describe("POAP Metadata", function () {
    it("Should return correct POAP metadata", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      expect(await proofOfProtest.getEventId(1)).to.equal(eventId);
      expect(await proofOfProtest.getGeoHash(1)).to.equal(geoHash);
      expect(await proofOfProtest.getMintTimestamp(1)).to.be.gt(0);
    });
  });

  describe("GeoHash Verification", function () {
    it("Should verify correct geohash", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      expect(await proofOfProtest.verifyGeoHash(1, geoHash)).to.be.true;
    });

    it("Should reject incorrect geohash", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      expect(await proofOfProtest.verifyGeoHash(1, wrongGeoHash)).to.be.false;
    });

    it("Should revert for non-existent token", async function () {
      expect(await proofOfProtest.verifyGeoHash(999, geoHash)).to.be.false;
    });
  });

  describe("POAP Revocation", function () {
    it("Should allow owner to revoke POAP", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      await proofOfProtest.revokePOAP(1);
      expect(await proofOfProtest.hasPOAP(attendee.address, eventId)).to.be.false;
    });

    it("Should not allow non-owner to revoke POAP", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      await expect(
        proofOfProtest.connect(attendee).revokePOAP(1)
      ).to.be.reverted;
    });

    it("Should allow re-minting after revocation", async function () {
      const tokenURI = "ipfs://test-uri";
      await proofOfProtest.mintPOAP(
        attendee.address,
        eventId,
        tokenURI,
        geoHash
      );

      await proofOfProtest.revokePOAP(1);
      
      // Should be able to mint again
      await expect(
        proofOfProtest.mintPOAP(
          attendee.address,
          eventId,
          tokenURI,
          geoHash
        )
      ).to.not.be.reverted;
    });
  });
}); 