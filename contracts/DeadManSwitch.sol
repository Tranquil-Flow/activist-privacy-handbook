// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * @title DeadManSwitch
 * @notice On chain dead man's switch built for Oasis Sapphire.
 * @dev This contract allows users to create alerts with a message, group ID, expiry date, and check-in days.
 *      It also allows users to check in on their alerts and trigger them if they haven't checked in within the specified time.
 */
contract DeadManSwitch {
    struct Alert {
        string message;
        string groupId;
        uint256 expiryDate;
        uint256 checkInDays;
        uint256 createdAt;
        uint256 lastCheckIn;
    }

    /// @notice Mapping of user addresses to their alerts.
    mapping(address => mapping(bytes32 => Alert)) public alerts;

    event AlertCreated(address indexed user, bytes32 indexed alertId, string message, string groupId, uint256 expiryDate, uint256 checkInDays);
    event AlertCheckedIn(address indexed user, bytes32 indexed alertId, uint256 lastCheckIn);
    event AlertTriggered(address indexed user, bytes32 indexed alertId, string message);

    /// @notice Create an alert.
    function createAlert(
        bytes32 alertId,
        string memory message,
        string memory groupId,
        uint256 expiryDays,
        uint256 checkInDays
    ) external {
        require(alerts[msg.sender][alertId].createdAt == 0, "Alert already exists");

        uint256 expiryDate = block.timestamp + (expiryDays * 1 days);
        uint256 createdAt = block.timestamp;

        alerts[msg.sender][alertId] = Alert({
            message: message,
            groupId: groupId,
            expiryDate: expiryDate,
            checkInDays: checkInDays,
            createdAt: createdAt,
            lastCheckIn: createdAt
        });

        emit AlertCreated(msg.sender, alertId, message, groupId, expiryDate, checkInDays);
    }

    /// @notice Check in on an alert to prevent it from being triggered.
    function checkIn(bytes32 alertId) external {
        require(alerts[msg.sender][alertId].createdAt != 0, "Alert does not exist");

        alerts[msg.sender][alertId].lastCheckIn = block.timestamp;

        emit AlertCheckedIn(msg.sender, alertId, block.timestamp);
    }

    /// @notice Trigger an alert.
    /// @dev Triggered if a user has not checked in within the specified time OR is manually triggered by user.
    function triggerAlert(bytes32 alertId) external {
        require(alerts[msg.sender][alertId].createdAt != 0, "Alert does not exist");

        Alert memory alert = alerts[msg.sender][alertId];
        require(block.timestamp > alert.expiryDate, "Alert has not expired");

        emit AlertTriggered(msg.sender, alertId, alert.message);

        delete alerts[msg.sender][alertId];
    }
}