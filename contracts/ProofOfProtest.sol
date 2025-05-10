// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ProofOfProtest
 * @notice Multi-event POAPs with hashed event IDs and geolocation proof.
 * @dev Built for Oasis Sapphire (private-by-default contract state)
 */
contract ProofOfProtest is ERC721URIStorage, Ownable {
    uint256 public nextTokenId;

    struct ProtestEvent {
        string name;
        uint256 startTime;
        uint256 endTime;
        bool active;
        string[] locationPoints; // List of points to trace the journey
    }

    struct POAP {
        bytes32 eventId;
        address attendee;
        uint256 timestamp;
        bytes32 geoHash;
    }

    // eventId (bytes32) => ProtestEvent metadata
    mapping(bytes32 => ProtestEvent) public events;

    // tokenId => POAP metadata
    mapping(uint256 => POAP) public poaps;

    // attendee => eventId => claimed
    mapping(address => mapping(bytes32 => bool)) public claimed;

    event EventCreated(bytes32 indexed eventId, string name);
    event ProtestPOAPMinted(address indexed attendee, uint256 indexed tokenId, bytes32 indexed eventId, bytes32 geoHash);

    constructor() ERC721("ProofOfProtest", "POP") Ownable(msg.sender) {}

    /**
     * @notice Register a new event using a pre-hashed event ID
     */
    function createEvent(
        bytes32 eventId,
        string memory name,
        string[] memory points,
        uint256 startTime,
        uint256 endTime
    ) external onlyOwner {
        require(events[eventId].startTime == 0, "Event already exists");
        require(endTime > startTime, "Invalid time range");

        events[eventId] = ProtestEvent({
            name: name,
            startTime: startTime,
            endTime: endTime,
            active: true,
            locationPoints: points
        });

        emit EventCreated(eventId, name);
    }

    /**
     * @notice Mint a POAP for a protest event
     */
    function mintPOAP(
        address to,
        bytes32 eventId,
        string memory tokenURI,
        bytes32 geoHash
    ) external onlyOwner {
        ProtestEvent memory ev = events[eventId];
        require(ev.active, "Event not active");
        require(block.timestamp >= ev.startTime && block.timestamp <= ev.endTime, "Outside event window");
        require(!claimed[to][eventId], "Already claimed");

        uint256 tokenId = ++nextTokenId;

        _mint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);

        poaps[tokenId] = POAP({
            eventId: eventId,
            attendee: to,
            timestamp: block.timestamp,
            geoHash: geoHash
        });

        claimed[to][eventId] = true;

        emit ProtestPOAPMinted(to, tokenId, eventId, geoHash);
    }

    // Read methods
    function hasPOAP(address user, bytes32 eventId) external view returns (bool) {
        return claimed[user][eventId];
    }

    function getProtestEvent(bytes32 eventId) external view returns (ProtestEvent memory) {
        return events[eventId];
    }

    function getGeoHash(uint256 tokenId) external view returns (bytes32) {
        return poaps[tokenId].geoHash;
    }

    function getEventId(uint256 tokenId) external view returns (bytes32) {
        return poaps[tokenId].eventId;
    }

    function getMintTimestamp(uint256 tokenId) external view returns (uint256) {
        return poaps[tokenId].timestamp;
    }

    /**
     * @notice Verify if a geolocation hash matches the stored hash for a POAP
     * @param tokenId The ID of the POAP to verify
     * @param geoHash The geolocation hash to verify
     * @return bool True if the hash matches, false otherwise
     */
    function verifyGeoHash(uint256 tokenId, bytes32 geoHash) external view returns (bool) {
        return poaps[tokenId].geoHash == geoHash;
    }

    /**
     * @notice Revoke a POAP (only callable by the contract owner)
     * @param tokenId The ID of the POAP to revoke
     */
    function revokePOAP(uint256 tokenId) external onlyOwner {
        address attendee = poaps[tokenId].attendee;
        bytes32 eventId = poaps[tokenId].eventId;
        _burn(tokenId);
        delete poaps[tokenId];
        claimed[attendee][eventId] = false;
    }
}
