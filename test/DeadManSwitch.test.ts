import { expect } from "chai";
import { ethers, keccak256, toUtf8Bytes } from "ethers";
import { ethers as hardhatEthers } from "hardhat";

describe("DeadManSwitch", function () {
  let deadManSwitch: any;
  let owner: any;
  let user: any;

  beforeEach(async function () {
    // Get signers
    [owner, user] = await hardhatEthers.getSigners();

    // Deploy the contract
    const DeadManSwitch = await hardhatEthers.getContractFactory("DeadManSwitch");
    deadManSwitch = await DeadManSwitch.deploy();
    // No need to call deadManSwitch.deployed() in recent Hardhat/Ethers versions
  });

  it("should create an alert", async function () {
    const alertId = keccak256(toUtf8Bytes("test-alert"));
    const message = "Test alert message";
    const groupId = "test-group";
    const expiryDays = 7;
    const checkInDays = 1;

    await deadManSwitch.createAlert(alertId, message, groupId, expiryDays, checkInDays);

    const alert = await deadManSwitch.alerts(owner.address, alertId);
    expect(alert.message).to.equal(message);
    expect(alert.groupId).to.equal(groupId);
  });

  it("should check in on an alert", async function () {
    const alertId = keccak256(toUtf8Bytes("test-alert"));
    const message = "Test alert message";
    const groupId = "test-group";
    const expiryDays = 7;
    const checkInDays = 1;

    await deadManSwitch.createAlert(alertId, message, groupId, expiryDays, checkInDays);
    await deadManSwitch.checkIn(alertId);

    const alert = await deadManSwitch.alerts(owner.address, alertId);
    expect(alert.lastCheckIn).to.be.gt(0);
  });

  it("should trigger an alert", async function () {
    const alertId = keccak256(toUtf8Bytes("test-alert"));
    const message = "Test alert message";
    const groupId = "test-group";
    const expiryDays = 1;
    const checkInDays = 1;

    await deadManSwitch.createAlert(alertId, message, groupId, expiryDays, checkInDays);

    // Fast forward time to trigger the alert
    await hardhatEthers.provider.send("evm_increaseTime", [86400]); // 1 day
    await hardhatEthers.provider.send("evm_mine");

    await deadManSwitch.triggerAlert(alertId);

    const alert = await deadManSwitch.alerts(owner.address, alertId);
    expect(alert.message).to.equal("");
  });
}); 