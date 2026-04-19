# genlayer-x402

> **x402 Payment Protocol for GenLayer Intelligent Contracts**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GenLayer](https://img.shields.io/badge/Built%20on-GenLayer-orange)](https://docs.genlayer.com)
[![x402](https://img.shields.io/badge/Protocol-x402-blue)](https://x402.org)

A library of **4 production-ready Intelligent Contracts** that bring the [HTTP 402 Payment Required](https://x402.org) standard onto the GenLayer blockchain. Gate real-time web data and AI services behind trustless, on-chain payments — without any server, API key, or middleman.

---

## Table of Contents

- [What is this?](#what-is-this)
- [The 4 Contracts](#the-4-contracts)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment](#deployment)
  - [Method 1: CLI Direct (Per Contract)](#method-1-cli-direct-per-contract)
  - [Method 2: Batch Deploy Script](#method-2-batch-deploy-script-all-4-at-once)
  - [Method 3: GenLayer Studio](#method-3-genlayer-studio)
- [Interacting with Contracts](#interacting-with-deployed-contracts)
- [Contract API Reference](#contract-api-reference)
- [Use Case Examples](#use-case-examples)
- [Linting](#linting)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

---

## What is this?

Traditional paid APIs rely on centralized servers with API keys — fragile, censorable, and opaque. `genlayer-x402` moves the payment gate **fully on-chain**:

- **Trustless verification** — payment checked by GenLayer validators, not a central server
- **Real-time web data** — contracts fetch live data via `gl.nondet.web.get()` after payment clears
- **AI-powered judgment** — the escrow contract uses LLM consensus to auto-approve/reject deliverables
- **Zero-trust** — no API keys, no accounts, just a wallet and a transaction

Perfect for: paid data APIs, AI inference billing, premium content gates, freelance milestone payments, and any pay-per-request use case.

---

## The 4 Contracts

| Contract | Pattern | Best For |
|---|---|---|
| `x402_paywall.py` | One-time payment → permanent access | Premium reports, data dumps, gated docs |
| `x402_metered.py` | Buy credits, deducted per call | AI inference, per-query analytics |
| `x402_subscription.py` | N calls per period, renewable | Streaming feeds, quota-based plans |
| `x402_escrow.py` | AI-verified milestone payment | Freelance work, deliverable contracts |

---

## Prerequisites

Following the [official GenLayer setup docs](https://docs.genlayer.com/developers/intelligent-contracts/tooling-setup):

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/en/download/)
- **Docker 26+** — [Download](https://docs.docker.com/get-docker/) (only if running local Studio)
- **A funded GenLayer account** — Get test GEN from the [testnet faucet](https://testnet-faucet.genlayer.foundation/)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/genlayer-x402.git
cd genlayer-x402
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs `genvm-linter` for contract linting.

### 3. Install GenLayer CLI (global)

```bash
npm install -g genlayer
```

### 4. Install TypeScript deploy dependencies

```bash
npm install
```

This reads `package.json` and installs `genlayer-js` and related packages into `node_modules/`.

### 5. Verify installation

```bash
genlayer --version
genvm-lint --version
node --version
python --version
```

All should print versions without errors.

---

## Deployment

GenLayer offers three ways to deploy contracts per the [official deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/deployment-methods). Pick whichever fits your workflow.

### Method 1: CLI Direct (Per Contract)

**Best for:** deploying one contract at a time, quick iteration, testing individual contracts.

This follows the [CLI Deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/cli-deployment). The CLI will **interactively prompt** you for the constructor arguments.

#### Set your target network first

```bash
# For local development (default)
genlayer network set localnet

# For public testnet
genlayer network set testnet-bradbury
```

#### Deploy X402Paywall

```bash
genlayer deploy --contract contracts/x402_paywall.py
```

When prompted, enter:

| Argument | Value |
|---|---|
| `price_wei` | `100` |
| `data_url` | `https://api.coinbase.com/v2/prices/BTC-USD/spot` |

#### Deploy X402Metered

```bash
genlayer deploy --contract contracts/x402_metered.py
```

When prompted, enter:

| Argument | Value |
|---|---|
| `price_per_call_wei` | `10` |
| `data_url_prefix` | `https://api.coingecko.com/api/v3/simple/price?ids=` |
| `max_credits` | `1000` |

#### Deploy X402Subscription

```bash
genlayer deploy --contract contracts/x402_subscription.py
```

When prompted, enter:

| Argument | Value |
|---|---|
| `price_per_period_wei` | `100` |
| `calls_per_period` | `50` |
| `data_url` | `https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate` |

#### Deploy X402Escrow

```bash
genlayer deploy --contract contracts/x402_escrow.py
```

When prompted, enter:

| Argument | Value |
|---|---|
| `brief` | `Build a simple static HTML landing page with hero section and a contact form.` |

> ⚠️ The brief **must be at least 20 characters long** — the contract rejects shorter briefs.

#### Expected deployment output

```
✅ Contract deployed successfully!
Transaction Hash: 0x1234567890abcdef...
Contract Address: 0xabcdef1234567890...
```

**Save the contract address** — you'll need it to interact with the contract.

---

### Method 2: Batch Deploy Script (All 4 at Once)

**Best for:** deploying all 4 contracts in sequence with default values, CI/CD pipelines, repeatable deployments.

This repo includes `deploy/deployScript.ts` — a ready-made TypeScript batch deployer following the [Deploy Scripts docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/deploy-scripts).

Run it with:

```bash
genlayer deploy
```

The CLI auto-detects the `deploy/` folder and executes `deployScript.ts`, deploying all 4 contracts in sequence.

#### Expected output

```
═══════════════════════════════════════════════════
  genlayer-x402 — Deploying all 4 contracts
═══════════════════════════════════════════════════

📦 Deploying X402Paywall...
✅ X402Paywall deployed
   Transaction Hash: 0xabc...
   Contract Address: 0x123...

📦 Deploying X402Metered...
✅ X402Metered deployed
   Transaction Hash: 0xdef...
   Contract Address: 0x456...

📦 Deploying X402Subscription...
✅ X402Subscription deployed
   Transaction Hash: 0x789...
   Contract Address: 0xabc...

📦 Deploying X402Escrow...
✅ X402Escrow deployed
   Transaction Hash: 0xdef...
   Contract Address: 0x789...

═══════════════════════════════════════════════════
  ✅ All 4 contracts deployed successfully!
═══════════════════════════════════════════════════
{
  "X402Paywall":      "0x...",
  "X402Metered":      "0x...",
  "X402Subscription": "0x...",
  "X402Escrow":       "0x..."
}
```

#### Customize constructor values

Want to use different prices or URLs? Edit the `args` arrays in `deploy/deployScript.ts`. For example:

```typescript
const paywallAddress = await deployContract(
  client,
  "X402Paywall",
  "contracts/x402_paywall.py",
  [
    500n,                                 // Change price to 500 wei
    "https://your-custom-api.com/data",   // Change URL
  ],
);
```

---

### Method 3: GenLayer Studio

**Best for:** beginners, visual exploration, one-off deployments without CLI.

Follows the [Studio deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio/deploying-contract).

1. Open [studio.genlayer.com](https://studio.genlayer.com) (hosted) or `http://localhost:8080` (local)
2. Click **Load Contract**
3. Copy-paste the contents of any `contracts/x402_*.py` file
4. Click **Deploy**
5. Fill in the constructor fields (same values as Method 1)
6. Click **Deploy Contract**
7. Copy the transaction hash and contract address

---

## Interacting with Deployed Contracts

### Via CLI

Following the [CLI Contracts API docs](https://docs.genlayer.com/api-references/genlayer-cli/contracts/call):

#### Read methods (free, no transaction)

```bash
# Get the current access price
genlayer call --address 0xYOUR_PAYWALL --function get_price

# Check if user has paid for access
genlayer call --address 0xYOUR_PAYWALL --function has_access --args 0xUSER_ADDRESS

# Get x402 protocol info
genlayer call --address 0xYOUR_PAYWALL --function get_402_info
```

#### Write methods (costs gas, can send value)

```bash
# Pay 100 wei for access
genlayer write --address 0xYOUR_PAYWALL --function pay_for_access --value 100

# Fetch gated data (after paying)
genlayer write --address 0xYOUR_PAYWALL --function get_protected_data

# Buy credits in the metered contract (sends 500 wei = 50 credits)
genlayer write --address 0xYOUR_METERED --function buy_credits --value 500

# Execute a metered query
genlayer write --address 0xYOUR_METERED --function execute_query --args "bitcoin&vs_currencies=usd"

# Subscribe for 1 period (sends 100 wei)
genlayer write --address 0xYOUR_SUB --function subscribe --args 1 --value 100
```

### Via Studio

1. Open Studio → paste deployed contract address in the contract loader
2. Use the **Read** and **Write** method panels
3. For payable methods, set the `value` field (in wei)

### Via JavaScript SDK

See [GenLayerJS docs](https://docs.genlayer.com/api-references/genlayer-js):

```javascript
import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const client = createClient({ chain: testnetBradbury });

// Read example
const price = await client.readContract({
  address: '0xYOUR_PAYWALL',
  functionName: 'get_price',
  args: [],
});

// Write example with GEN value
const txHash = await client.writeContract({
  address: '0xYOUR_PAYWALL',
  functionName: 'pay_for_access',
  args: [],
  value: 100n,
});
```

---

## Contract API Reference

### X402Paywall — One-time Payment

**Constructor:**

| Parameter | Type | Description |
|---|---|---|
| `price_wei` | `u256` | Access price in wei |
| `data_url` | `str` | URL to fetch after payment |

**Read methods (free):**

| Method | Returns | Description |
|---|---|---|
| `get_price()` | `u256` | Current access price |
| `get_owner()` | `str` | Contract owner address |
| `has_access(user)` | `bool` | Whether user has paid |
| `get_payment(user)` | `u256` | Total paid by user |
| `get_total_revenue()` | `u256` | Cumulative revenue |
| `get_402_info()` | `str` | JSON metadata (x402 spec) |

**Write methods:**

| Method | Value | Description |
|---|---|---|
| `pay_for_access()` | ≥ `price_wei` | Purchase permanent access |
| `get_protected_data()` | 0 | Fetch live data (paid users only) |
| `update_price(new_price)` | 0 | Owner only |
| `update_data_url(new_url)` | 0 | Owner only |

---

### X402Metered — Pay Per Call

**Constructor:**

| Parameter | Type | Description |
|---|---|---|
| `price_per_call_wei` | `u256` | Cost per API call |
| `data_url_prefix` | `str` | URL prefix (query param appended per call) |
| `max_credits` | `u256` | Max credits per user (anti-abuse) |

**Read methods:**

| Method | Returns | Description |
|---|---|---|
| `get_price_per_call()` | `u256` | Per-call cost |
| `check_credits(user)` | `u256` | User's remaining credits |
| `get_call_count(user)` | `u256` | User's total calls made |
| `get_total_calls()` | `u256` | Global call count |
| `get_402_info()` | `str` | JSON metadata |

**Write methods:**

| Method | Args / Value | Description |
|---|---|---|
| `buy_credits()` | value ≥ price | Get `floor(value / price)` credits |
| `execute_query(q)` | string arg | Consume 1 credit, fetch + AI-summarize |
| `grant_credits(user, n)` | args | Owner only — grant free credits |

---

### X402Subscription — Periodic Quota

**Constructor:**

| Parameter | Type | Description |
|---|---|---|
| `price_per_period_wei` | `u256` | Cost per subscription period |
| `calls_per_period` | `u256` | Calls granted per period |
| `data_url` | `str` | URL for subscriber data |

**Write methods:**

| Method | Args / Value | Description |
|---|---|---|
| `subscribe(periods)` | value ≥ price×periods | Add `periods × calls_per_period` calls |
| `get_data()` | 0 | Fetch data, consumes 1 call |
| `grant_access(user, periods)` | args | Owner only |

---

### X402Escrow — AI-Verified Payment

**Constructor:**

| Parameter | Type | Description |
|---|---|---|
| `brief` | `str` | Acceptance criteria (min 20 chars) |

**State flow:**
```
OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED
```

**Write methods:**

| Method | Args / Value | Description |
|---|---|---|
| `fund(freelancer)` | value > 0 | Client funds + assigns freelancer |
| `submit_work(url, desc)` | args | Freelancer submits → AI evaluates |
| `release_payment()` | 0 | Release funds (if APPROVED) |
| `client_approve()` | 0 | Client override approval |
| `client_cancel()` | 0 | Client refund (if FUNDED) |

---

## Use Case Examples

### Example 1: Paid Bitcoin Price Feed

```bash
# As API provider — deploy
genlayer deploy --contract contracts/x402_paywall.py
# Enter: price_wei=100, data_url=https://api.coinbase.com/v2/prices/BTC-USD/spot

# As user — pay for access
genlayer write --address 0xCONTRACT --function pay_for_access --value 100

# As user — fetch the live BTC price
genlayer write --address 0xCONTRACT --function get_protected_data
# Returns: {"data":{"amount":"65000.42","currency":"USD"}}
```

### Example 2: Metered AI Query API

```bash
# Deploy
genlayer deploy --contract contracts/x402_metered.py

# User buys 50 credits (10 wei × 50 = 500 wei total)
genlayer write --address 0xCONTRACT --function buy_credits --value 500

# User runs metered query — each call costs 1 credit + AI summary
genlayer write --address 0xCONTRACT --function execute_query --args "bitcoin&vs_currencies=usd"
```

### Example 3: Monthly Data Subscription

```bash
# Deploy with 50 calls per period at 100 wei each
genlayer deploy --contract contracts/x402_subscription.py

# Subscribe for 3 periods (300 wei → 150 total calls)
genlayer write --address 0xCONTRACT --function subscribe --args 3 --value 300

# Each get_data() consumes 1 call from quota
genlayer write --address 0xCONTRACT --function get_data
```

### Example 4: AI-Judged Freelance Escrow

```bash
# Client deploys with detailed brief
genlayer deploy --contract contracts/x402_escrow.py

# Client funds + assigns freelancer (500 wei payment)
genlayer write --address 0xCONTRACT --function fund --args 0xFREELANCER --value 500

# Freelancer submits → GenLayer LLM validators auto-evaluate
genlayer write --address 0xCONTRACT --function submit_work \
  --args "https://github.com/bob/work" "Completed landing page"

# If AI approves → anyone can trigger payout to freelancer
genlayer write --address 0xCONTRACT --function release_payment
```

---

## Linting

Before deploying, always lint your contracts:

```bash
genvm-lint check contracts/x402_paywall.py
genvm-lint check contracts/x402_metered.py
genvm-lint check contracts/x402_subscription.py
genvm-lint check contracts/x402_escrow.py
```

The linter catches:
- Forbidden imports (`os`, `sys`, `subprocess`)
- Non-deterministic calls outside equivalence principle blocks
- Invalid storage types (must use `TreeMap` / `DynArray`)
- Missing decorators and return type annotations

See [GenVM Linter docs](https://docs.genlayer.com/api-references/genlayer-linter) for full reference.

---

## Project Structure

```
genlayer-x402/
│
├── contracts/                   # Intelligent Contracts (Python)
│   ├── x402_paywall.py          #   One-time payment
│   ├── x402_metered.py          #   Per-call billing
│   ├── x402_subscription.py     #   Quota-based access
│   └── x402_escrow.py           #   AI-verified escrow
│
├── deploy/
│   └── deployScript.ts          # Batch deploy all 4 (Method 2)
│
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
├── README.md                    # This file
├── gltest.config.yaml           # GenLayer test config
├── package.json                 # Node.js dependencies
├── requirements.txt             # Python dependencies
└── tsconfig.json                # TypeScript config
```

---

## Troubleshooting

### Lint fails with "No contract class found"

Your contract class name must be **specific** (e.g., `X402Paywall`), not generic (`Contract`). GenLayer requires named classes per the official examples. This is already the case for all contracts in this library.

### Lint fails with "gl.nondet.* call not reachable from equivalence principle block"

Any `gl.nondet.web.get()` or `gl.nondet.exec_prompt()` call must be inside a function that's called by `gl.eq_principle.strict_eq()` or `gl.eq_principle.prompt_comparative()`:

```python
def nondet() -> str:
    response = gl.nondet.web.get(url)       # ✓ inside nondet function
    return response.body.decode("utf-8")

return gl.eq_principle.strict_eq(nondet)    # ✓ passed to eq_principle
```

### "Insufficient balance" when deploying to testnet

Request test GEN from the [testnet faucet](https://testnet-faucet.genlayer.foundation/) first.

### TypeScript error `'receipt.data' is possibly 'undefined'` in deployScript

The script uses optional chaining (`?.`) and type casting (`as any`) to handle this safely. This is a compile-time warning only — the deploy itself will work correctly.

### Deploy script fails: `Cannot find module 'genlayer-js'`

Make sure you ran `npm install` in the project root directory. Check that `node_modules/` exists.

### `git push` takes forever with CRLF warnings

Your `node_modules/` folder was accidentally tracked. Fix it:

```bash
git rm -r --cached node_modules
git config --global core.autocrlf true
git add .gitignore
git commit -m "chore: remove node_modules from tracking"
git push origin main
```

### `gl.block.number` error when deploying

GenLayer does not have block numbers inside contracts. Use state machines or call counters instead. This library uses the quota pattern in `x402_subscription.py` and state machines in `x402_escrow.py`.

---

## Resources

- 📖 [GenLayer Docs](https://docs.genlayer.com)
- 📘 [GenLayer SDK Reference](https://sdk.genlayer.com)
- 🎮 [GenLayer Studio (browser)](https://studio.genlayer.com)
- 🔧 [GenVM Linter Docs](https://docs.genlayer.com/api-references/genlayer-linter)
- 💧 [Testnet Faucet](https://testnet-faucet.genlayer.foundation/)
- 📜 [x402 Protocol Spec](https://x402.org)
- 🏆 [GenLayer Builder Program](https://portal.genlayer.foundation)

---

## Contributing

Issues and pull requests welcome! This library is open-source and community-driven.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-thing`)
3. Commit your changes (`git commit -m 'feat: add amazing thing'`)
4. Push to the branch (`git push origin feature/amazing-thing`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.