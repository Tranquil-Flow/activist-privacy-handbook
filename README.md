# 🛡️ Activist Toolkit  
**Protect the protest. Preserve the proof.**

A decentralized, privacy-first protocol to empower activists, protect their identities, and preserve immutable proof of protest — even under repressive regimes. Built using Oasis Sapphire and ROFL, Activist Toolkit provides censorship-resistant infrastructure to **verify presence**, **coordinate emergency alerts**, and **resist digital erasure** without exposing user identities.

---

![Image](https://github.com/user-attachments/assets/be302641-5583-4d67-8bbb-b33987c9df80)

---

## ✊ Why Activist Toolkit?

**Activist Toolkit** is a secure, censorship-resistant system for modern human rights defenders.

In the face of growing authoritarianism and digital surveillance, activists around the world are risking their lives — but often have **no way to verify their actions**, protect their communications, or prove their contributions.

Conventional digital tools like photos or chat logs are:
- Easily manipulated  
- Can be incriminating to share  
- Frequently dismissed in legal or asylum proceedings  

**Blockchain isn't just useful — it's essential.**  
It's the **only infrastructure** that makes proof tamper-proof, decentralized, and permanent.

---

## 🔍 What It Does

- **✅ Proof of Protest**  
  Anonymous, geolocation-based, timestamped credentials that verify protest participation — without revealing personal identity.

- **🔴 Dead Man Switch (Red Alert)**  
  A failsafe timer that triggers alerts to trusted contacts if an activist goes silent or is detained.

- **🧾 Peer Attestation System**  
  A decentralized verification process where trusted members vouch for presence, preventing fake participation or infiltration.

---

## 🔑 Feature Examples

### ✅ Proof of Protest  
> _Anonymous, verifiable presence — without needing to reveal your face or contacts._

**Sidika** is applying for asylum in the Netherlands. As a gender rights activist from Turkey, she must prove her involvement in protests — but she never appeared in photos and won't share private chats.  
Using Activist Toolkit, she receives an **immutable, peer-attested credential**: she was present at X protest, on Y date, verified by trusted witnesses.

Now she has verifiable proof — **without compromising herself or others**.

---

### 🔴 Dead Man Switch  
> _Secure fallback for detained activists or those crossing danger zones._

**Abdul** is helping his sister cross a border into Germany. He sets a **6-hour timer** in the toolkit.  
If he doesn't cancel in time, the app automatically sends a **prewritten message** to his Telegram group of legal and support contacts.

This feature can **trigger help when silence becomes danger**.

---

## ⚙️ How It Works  
`[INSERT TECH STACK DIAGRAM HERE]`

### 🔧 Tech Overview

- **Oasis Sapphire** – Confidential EVM for encrypted smart contracts and private on-chain logic.  
- **Oasis ROFL** – Secure TEE environment for off-chain logic (e.g. red alerts, proof validation).  
- **ZK Identity Tools (e.g. Semaphore)** – To enable anonymity and unlinkable attestations.  
- **Smart Contracts** – For soulbound credentials, timers, and proof mechanisms.  
- **IPFS** *(optional)* – For decentralized metadata and document storage.

> ✅ We use `roflEnsureAuthorizedOrigin` to guarantee only verified, secure TEE-originated data is accepted on-chain.  
> 🔧 _Note: Link to code implementation will be added soon._

---

## 🚧 Roadmap: Work in Progress
We truly believe in the long-term existence of this project. We would aspire to continue improving the current features as well as adding more like: 

- **🪙 Anonymous Fundraising**  
  Create and contribute to activist campaigns privately via blockchain-native donations.

- **💬 Activist Education Chatbot**  
  A conversational AI assistant trained on global activist handbooks for real-time, context-aware guidance.

- **🌐 Global Network Expansion**  
  Develop tools for collective resource sharing and decentralized reputation systems across movements.

---

## 🏆 Hackathon Bounties

This project qualifies for:

- **Privacy Track** — Leveraging Sapphire to encrypt user activity and on-chain protest proofs.  
- **Security Track** — Secure fallback alerts, identity protection, and tamper-proof attestations via ROFL.

### ✅ Judging Criteria Checkpoints:

- **Potential Impact**: Enables global activist safety and verification at scale.  
- **Confidentiality**: Data never leaves ROFL unencrypted; Sapphire encrypts smart contract state.  
- **UX**: Designed for non-crypto-native users with a clean, simple, safe experience.  
- **Innovation**: Uses geolocation-based protest proofs and peer attestations — a novel combination on Sapphire.  
- **Implementation Quality**: Core features functional and tested with Oasis stack.  
- **Bonus**: Integrated `roflEnsureAuthorizedOrigin` for verified confidential origin in smart contracts.

---

## 🌐 Deployments

* GitHub
* VIDEO DEMO
* WEBSITE
* PRESENTATION
* UX/UI

---

## Testing

Running Tests

To run the test suite (including DeadManSwitch.test.ts and ProofOfProtest.test.ts), execute the following command in your terminal (from the project root):

```bash
npx hardhat test
```

If you wish to run a specific test file, for example, run DeadManSwitch tests or ProofOfProtest tests, use:

```bash
npx hardhat test test/DeadManSwitch.test.ts
# or
npx hardhat test test/ProofOfProtest.test.ts
```

Note: The tests are written in TypeScript and use Chai (expect) and ethers (from hardhat) for assertions and contract interaction.

---

## 🧠 Team

Toufik Airane | Evi Nova | 1uiz | Migle


---

> _Built during ETHDam III, 2025 — for activists everywhere who defend freedom, dignity, and truth._
