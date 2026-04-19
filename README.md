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
- [Quick Start](#quick-start)
- [Deployment Methods](#deployment-methods)
  - [Method 1: CLI Direct (single contract)](#method-1-cli-direct-deployment)
  - [Method 2: Deploy Script (all contracts at once)](#method-2-deploy-script-batch-all-4)
  - [Method 3: GenLayer Studio (web UI)](#method-3-genlayer-studio-no-cli-needed)
- [Interacting with Contracts](#interacting-with-deployed-contracts)
- [Contract API Reference](#contract-api-reference)
- [Testing & Linting](#testing--linting)
- [Use Case Examples](#use-case-examples)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

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

## Quick Start

### 1. Clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/genlayer-x402.git
cd genlayer-x402
```

### 2. Install dependencies

```bash
# Python dependencies (genlayer-test + genvm-linter)
pip install -r requirements.txt

# GenLayer CLI (global)
npm install -g genlayer

# TypeScript dependencies (for deploy script)
npm install
```

### 3. Start local environment (optional)

If you want to test on your machine first:

```bash
# Initialize GenLayer local environment (one-time)
genlayer init

# Start local GenLayer Studio
genlayer up
# Studio opens at http://localhost:8080
```

### 4. Lint the contracts

```bash
genvm-lint check contracts/x402_paywall.py
genvm-lint check contracts/x402_metered.py
genvm-lint check contracts/x402_subscription.py
genvm-lint check contracts/x402_escrow.py
```

All four should pass with ✓.

### 5. Deploy!

Pick one of the three deployment methods below ⬇

---

## Deployment Methods

GenLayer offers three ways to deploy contracts per the [official deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/deployment-methods):

### Method 1: CLI Direct Deployment

**Best for:** single-contract deployments, quick iteration, testing.

Follows the [CLI Deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/cli-deployment). Syntax:

```bash
genlayer deploy --contract <contractPath>
```

The CLI will **interactively prompt** you for constructor arguments based on the contract's `__init__` signature.

#### Deploy X402Paywall

```bash
genlayer deploy --contract contracts/x402_paywall.py
```

When prompted, enter:
- `price_wei`: `100`
- `data_url`: `https://api.coinbase.com/v2/prices/BTC-USD/spot`

#### Deploy X402Metered

```bash
genlayer deploy --contract contracts/x402_metered.py
```

When prompted, enter:
- `price_per_call_wei`: `10`
- `data_url_prefix`: `https://api.coingecko.com/api/v3/simple/price?ids=`
- `max_credits`: `1000`

#### Deploy X402Subscription

```bash
genlayer deploy --contract contracts/x402_subscription.py
```

When prompted, enter:
- `price_per_period_wei`: `100`
- `calls_per_period`: `50`
- `data_url`: `https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate`

#### Deploy X402Escrow

```bash
genlayer deploy --contract contracts/x402_escrow.py
```

When prompted, enter:
- `brief`: `Build a simple static HTML landing page with hero section and a contact form.`

> ⚠️ The brief must be at least 20 characters long.

#### Deploy to a specific network

Before deploying, set the target network:

```bash
# Switch to testnet Bradbury
genlayer network set testnet-bradbury

# Then deploy as usual
genlayer deploy --contract contracts/x402_paywall.py
```

Or use a custom RPC URL:

```bash
genlayer deploy --contract contracts/x402_paywall.py --rpc http://localhost:4000/api
```

#### Expected output

```
✅ Contract deployed successfully!
Transaction Hash: 0x1234567890abcdef...
Contract Address: 0xabcdef1234567890...
```

Save the contract address — you'll need it to interact with the contract.

---

### Method 2: Deploy Script (batch all 4)

**Best for:** deploying all 4 contracts at once with pre-configured values, CI/CD, repeatable deployments.

This project includes a ready-made deploy script at `deploy/deployScript.ts` that deploys all 4 contracts with sensible defaults.

Run:

```bash
genlayer deploy
```

This command automatically:
1. Detects the `deploy/` folder
2. Runs `deploy/deployScript.ts`
3. Deploys all 4 contracts in sequence
4. Prints addresses for each deployed contract

Expected output:

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
   ...

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

Want to change the default constructor values? Edit the `args` arrays in `deploy/deployScript.ts`.

---

### Method 3: GenLayer Studio (no CLI needed)

**Best for:** beginners, visual exploration, one-off deployments.

Follows the [Studio deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio/deploying-contract).

1. Open [studio.genlayer.com](https://studio.genlayer.com) (hosted) or `http://localhost:8080` (local)
2. Click **Load Contract**
3. Paste the contract code (e.g., from `contracts/x402_paywall.py`)
4. Click **Deploy**
5. Fill in the constructor fields:
   - `price_wei`: `100`
   - `data_url`: `https://api.coinbase.com/v2/prices/BTC-USD/spot`
6. Click **Deploy Contract**
7. Copy the shown transaction hash and contract address

---

## Interacting with Deployed Contracts

Once deployed, you can call contract methods via CLI, Studio, or JavaScript SDK.

### Via CLI

Following the [CLI Contracts API docs](https://docs.genlayer.com/api-references/genlayer-cli/contracts/call):

#### Read methods (free, no transaction)

```bash
# Read price from paywall
genlayer call --address 0xYOUR_PAYWALL_ADDRESS --function get_price

# Check if user has access
genlayer call --address 0xYOUR_PAYWALL_ADDRESS --function has_access --args 0xUSER_ADDRESS

# Get 402 payment info
genlayer call --address 0xYOUR_PAYWALL_ADDRESS --function get_402_info
```

#### Write methods (cost gas, may require value)

```bash
# Pay for access (sends 100 wei with the call)
genlayer write --address 0xYOUR_PAYWALL_ADDRESS --function pay_for_access --value 100

# Fetch protected data (requires prior payment)
genlayer write --address 0xYOUR_PAYWALL_ADDRESS --function get_protected_data

# Buy credits in metered contract (send 100 wei = 10 credits)
genlayer write --address 0xYOUR_METERED_ADDRESS --function buy_credits --value 100

# Subscribe for 1 period
genlayer write --address 0xYOUR_SUB_ADDRESS --function subscribe --args 1 --value 100
```

### Via Studio

1. Open Studio at [studio.genlayer.com](https://studio.genlayer.com) or `http://localhost:8080`
2. Paste your deployed contract address
3. Use the **Read** and **Write** method panels
4. For payable methods, set the `value` field in wei

### Via JavaScript (GenLayerJS SDK)

See [GenLayerJS docs](https://docs.genlayer.com/api-references/genlayer-js):

```javascript
import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const client = createClient({ chain: testnetBradbury });

// Read
const price = await client.readContract({
  address: '0xYOUR_PAYWALL_ADDRESS',
  functionName: 'get_price',
  args: [],
});

// Write with value
const txHash = await client.writeContract({
  address: '0xYOUR_PAYWALL_ADDRESS',
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
| `data_url_prefix` | `str` | URL prefix (query param appended) |
| `max_credits` | `u256` | Max credits per user (anti-abuse) |

**Read methods (free):**

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

**State flow:** `OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED`

**Write methods:**

| Method | Args / Value | Description |
|---|---|---|
| `fund(freelancer)` | value > 0 | Client funds + assigns freelancer |
| `submit_work(url, desc)` | args | Freelancer submits → AI evaluates |
| `release_payment()` | 0 | Release funds to freelancer (if APPROVED) |
| `client_approve()` | 0 | Client override approval |
| `client_cancel()` | 0 | Client refund (if FUNDED, not submitted) |

---

## Testing & Linting

### Direct-mode tests (fast, no server)

```bash
pytest tests/direct/ -v
```

These tests run contracts in-memory without spinning up any GenLayer environment. See [Testing docs](https://docs.genlayer.com/developers/intelligent-contracts/testing).

### Linting

```bash
genvm-lint check contracts/<contract_name>.py
```

The linter catches:
- Forbidden imports (`os`, `sys`, `subprocess`)
- Non-deterministic calls outside equivalence principle blocks
- Invalid storage types (must use `TreeMap` / `DynArray`)
- Missing decorators and return type annotations

---

## Use Case Examples

### Example 1: Paid Bitcoin Price Feed

```bash
# Deploy (as API provider)
genlayer deploy --contract contracts/x402_paywall.py
# price_wei: 100
# data_url: https://api.coinbase.com/v2/prices/BTC-USD/spot

# User pays
genlayer write --address 0xCONTRACT --function pay_for_access --value 100

# User reads live price
genlayer write --address 0xCONTRACT --function get_protected_data
# Returns: {"data":{"amount":"65000.42","currency":"USD"}}
```

### Example 2: Metered AI Query API

```bash
# Deploy
genlayer deploy --contract contracts/x402_metered.py
# price_per_call_wei: 10, data_url_prefix: https://api.coingecko.com/...

# Buy 50 credits (10 wei × 50 = 500 wei)
genlayer write --address 0xCONTRACT --function buy_credits --value 500

# Each query consumes 1 credit, returns AI summary
genlayer write --address 0xCONTRACT --function execute_query --args "bitcoin&vs_currencies=usd"
```

### Example 3: Monthly Data Subscription

```bash
# Deploy with 50 calls per period at 100 wei
genlayer deploy --contract contracts/x402_subscription.py

# Subscribe for 3 periods (3 × 100 = 300 wei → 150 calls)
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

# Freelancer submits work → AI evaluates
genlayer write --address 0xCONTRACT --function submit_work \
  --args "https://github.com/bob/work" "Completed landing page with all sections"

# If AI approves → anyone triggers payment release
genlayer write --address 0xCONTRACT --function release_payment
```

---

## Project Structure

```
genlayer-x402/
│
├── contracts/                       # Intelligent Contracts (Python)
│   ├── x402_paywall.py              #   One-time payment
│   ├── x402_metered.py              #   Per-call billing
│   ├── x402_subscription.py         #   Quota-based access
│   └── x402_escrow.py               #   AI-verified escrow
│
├── tests/
│   └── direct/                      # Fast in-memory tests
│       ├── test_paywall.py
│       ├── test_metered.py
│       ├── test_subscription.py
│       └── test_escrow.py
│
├── deploy/
│   └── deployScript.ts              # Batch deploy all 4 (Method 2)
│
├── gltest.config.yaml               # Network + account config
├── package.json                     # TypeScript deps
├── tsconfig.json
├── requirements.txt                 # Python deps
├── README.md                        # This file
├── LICENSE
└── .gitignore
```

---

## Troubleshooting

### `genvm-lint check` fails with "No contract class found"

Make sure your contract class name is **specific** (e.g., `X402Paywall`), not generic (`Contract`). GenLayer requires named classes per the official examples.

### Lint fails with "gl.nondet.* call not reachable from equivalence principle block"

Your `gl.nondet.web.get()` or `gl.nondet.exec_prompt()` call must be inside a function that's called by `gl.eq_principle.strict_eq()` or `gl.eq_principle.prompt_comparative()`. Example:

```python
def nondet() -> str:
    response = gl.nondet.web.get(url)       # ✓ inside nondet function
    return response.body.decode("utf-8")

return gl.eq_principle.strict_eq(nondet)    # ✓ passed to eq_principle
```

### "Insufficient balance" on testnet deploy

Request test GEN from the [faucet](https://testnet-faucet.genlayer.foundation/) first.

### `gl.block.number` error

GenLayer does not have block numbers in contracts. Use state machines or call counters instead — see `x402_subscription.py` for the quota pattern.

### Deploy script fails on Windows

TypeScript deploys rely on `ts-node`. Make sure you ran `npm install` and have Node.js 18+ installed. Try `npm install` again if `genlayer deploy` doesn't pick up the script.

---

## Resources

- 📖 [GenLayer Docs](https://docs.genlayer.com)
- 📘 [GenLayer SDK Reference](https://sdk.genlayer.com)
- 🎮 [GenLayer Studio (browser)](https://studio.genlayer.com)
- 💧 [Testnet Faucet](https://testnet-faucet.genlayer.foundation/)
- 📜 [x402 Protocol Spec](https://x402.org)
- 🏆 [GenLayer Builder Program](https://portal.genlayer.foundation)
- 💬 [GenLayer Discord](https://discord.gg/genlayer)

---

## Contributing

Issues and pull requests welcome! This library is open-source and community-driven.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-thing`)
3. Commit your changes (`git commit -m 'Add amazing thing'`)
4. Push to the branch (`git push origin feature/amazing-thing`)
5. Open a Pull Request

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

Built for the [GenLayer Builder Program](https://portal.genlayer.foundation) — Tools & Infrastructure category.
