// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import { Subcall } from "@oasisprotocol/sapphire-contracts/contracts/Subcall.sol";

/*
 * @title DeadManSwitch
 * @notice On chain dead man's switch built for Oasis Sapphire.
 * @dev This contract allows users to create alerts with a message, group ID, expiry date, and check-in days.
 *      It also allows users to check in on their alerts and trigger them if they haven't checked in within the specified time.
 */
contract DeadManSwitch {
    struct Alert {
        address user;  // The user who owns this alert
        string message;
        string groupId;
        uint256 expiryDate;
        uint256 checkInDays;
        uint256 createdAt;
        uint256 lastCheckIn;
    }

    /// @notice Mapping of alert IDs to their alerts.
    mapping(bytes32 => Alert) public alerts;

    address public admin;
    bytes21 public roflAppID;

    event AlertCreated(bytes32 indexed alertId, address indexed user, string message, string groupId, uint256 expiryDate, uint256 checkInDays);
    event AlertCheckedIn(bytes32 indexed alertId, address indexed user, uint256 lastCheckIn);
    event AlertTriggered(bytes32 indexed alertId, address indexed user, string message);
    event RoflAppIDUpdated(bytes21 oldRoflAppID, bytes21 newRoflAppID);

    constructor(address _admin) {
        admin = _admin;
    }

    /// @notice Update the ROFL app ID (admin only).
    function setRoflAppID(bytes21 _newRoflAppID) external {
        require(msg.sender == admin, "Not admin");
        bytes21 oldRoflAppID = roflAppID;
        roflAppID = _newRoflAppID;
        emit RoflAppIDUpdated(oldRoflAppID, _newRoflAppID);
    }

    /// @notice Create an alert.
    function createAlert(
        bytes32 alertId,
        string memory message,
        string memory groupId,
        uint256 expiryDays,
        uint256 checkInDays
    ) external {
        require(alerts[alertId].createdAt == 0, "Alert already exists");

        uint256 expiryDate = block.timestamp + (expiryDays * 1 days);
        uint256 createdAt = block.timestamp;

        alerts[alertId] = Alert({
            user: msg.sender,
            message: message,
            groupId: groupId,
            expiryDate: expiryDate,
            checkInDays: checkInDays,
            createdAt: createdAt,
            lastCheckIn: createdAt
        });

        emit AlertCreated(alertId, msg.sender, message, groupId, expiryDate, checkInDays);
    }

    /// @notice Check in on an alert to prevent it from being triggered.
    function checkIn(bytes32 alertId) external {
        require(alerts[alertId].createdAt != 0, "Alert does not exist");
        require(alerts[alertId].user == msg.sender, "Not the alert owner");

        alerts[alertId].lastCheckIn = block.timestamp;

        emit AlertCheckedIn(alertId, msg.sender, block.timestamp);
    }

    /// @notice Trigger an alert (ROFL TEE only).
    function triggerAlertByROFL(bytes32 alertId) external {
        Subcall.roflEnsureAuthorizedOrigin(roflAppID);
        _triggerAlert(alertId);
    }

    /// @notice Trigger an alert (admin only).
    function triggerAlertByAdmin(bytes32 alertId) external {
        require(msg.sender == admin, "Not admin");
        _triggerAlert(alertId);
    }

    function _triggerAlert(bytes32 alertId) internal {
        require(alerts[alertId].createdAt != 0, "Alert does not exist");
        Alert memory alert = alerts[alertId];
        emit AlertTriggered(alertId, msg.sender, alert.message);
        delete alerts[alertId];
    }
}