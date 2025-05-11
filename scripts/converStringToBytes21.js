const bech32 = require("bech32");

const roflAppID = "rofl1qrtv4yv5arlxuxqwly6m3cawqcn0qj6dmut6cvwa";

const { prefix, words } = bech32.decode(roflAppID);
if (prefix !== "rofl") {
  throw new Error(`Malformed ROFL app identifier: ${roflAppID}`);
}
const rawAppID = new Uint8Array(bech32.fromWords(words));
console.log(rawAppID);
console.log("0x" + Buffer.from(rawAppID).slice(0, 21).toString("hex"));