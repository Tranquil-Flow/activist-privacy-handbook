import { expect } from "chai";
import { ethers, keccak256, toUtf8Bytes } from "ethers";
import { ethers as hardhatEthers } from "hardhat";

describe("DeadManSwitch", function () {
  let deadManSwitch: any;
  let owner: any;
  let user: any;

  beforeEach(async function () {
    [owner, user] = await hardhatEthers.getSigners();
    const DeadManSwitch = await hardhatEthers.getContractFactory("DeadManSwitch");
    deadManSwitch = await DeadManSwitch.deploy(owner.address);
  });

  it("should create an alert", async function () {
    const alertId = keccak256(toUtf8Bytes("test-alert"));
    const message = "Test alert message";
    const groupId = "test-group";
    const expirySeconds = 7 * 24 * 60 * 60;
    const checkInSeconds = 1 * 24 * 60 * 60;

    await deadManSwitch.createAlert(alertId, message, groupId, expirySeconds, checkInSeconds);

    const alert = await deadManSwitch.alerts(alertId);
    expect(alert.message).to.equal(message);
    expect(alert.groupId).to.equal(groupId);
  });

  it("should check in on an alert", async function () {
    const alertId = keccak256(toUtf8Bytes("test-alert"));
    const message = "Test alert message";
    const groupId = "test-group";
    const expirySeconds = 7 * 24 * 60 * 60;
    const checkInSeconds = 1 * 24 * 60 * 60;

    await deadManSwitch.createAlert(alertId, message, groupId, expirySeconds, checkInSeconds);
    await deadManSwitch.checkIn(alertId);

    const alert = await deadManSwitch.alerts(alertId);
    expect(alert.lastCheckIn).to.be.gt(0);
  });

  it("should trigger an alert", async function () {
    const alertId = keccak256(toUtf8Bytes("test-alert"));
    const message = "Test alert message";
    const groupId = "test-group";
    const expirySeconds = 1 * 24 * 60 * 60;
    const checkInSeconds = 1 * 24 * 60 * 60;

    await deadManSwitch.createAlert(alertId, message, groupId, expirySeconds, checkInSeconds);

    // Fast forward time to trigger the alert
    await hardhatEthers.provider.send("evm_increaseTime", [86400]); // 1 day
    await hardhatEthers.provider.send("evm_mine");

    await deadManSwitch.triggerAlertByAdmin(alertId);

    const alert = await deadManSwitch.alerts(alertId);
    expect(alert.message).to.equal("");
  });
}); 