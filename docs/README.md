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
- [Security Features](#security-features)
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
- **Revenue withdrawal** — owners can withdraw accumulated revenue to their wallet anytime
- **Immutable access** — once a user pays, price changes never revoke their access
- **Anti-lockup safeguards** — escrow has arbiter + timeout mechanisms to prevent stuck funds

Perfect for: paid data APIs, AI inference billing, premium content gates, freelance milestone payments, and any pay-per-request use case.

---

## The 4 Contracts

| Contract | Pattern | Best For |
|---|---|---|
| `x402_paywall.py` | One-time payment → permanent access | Premium reports, data dumps, gated docs |
| `x402_metered.py` | Buy credits, deducted per call | AI inference, per-query analytics |
| `x402_subscription.py` | N calls per period, renewable | Streaming feeds, quota-based plans |
| `x402_escrow.py` | AI-verified milestone payment | Freelance work, deliverable contracts |

All 4 contracts support **owner revenue withdrawal** via `withdraw()` and `withdraw_all()` methods.

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

This reads `package.json` and installs `genlayer-js` and related packages.

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

GenLayer offers three ways to deploy contracts per the [official deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/deployment-methods).

### Understanding Wei and GEN Units

Per the [official Value Transfers docs](https://docs.genlayer.com/developers/intelligent-contracts/features/value-transfers), GenLayer uses **GEN** as its native token, and **values are denominated in wei**:

> **1 GEN = 10¹⁸ wei = 1,000,000,000,000,000,000 wei**

All contract fields suffixed `_wei` store values in wei. When deploying, you must enter amounts in wei, not GEN.

**Conversion cheat sheet:**

| Amount in GEN | Amount in Wei (what to enter) |
|---|---|
| 0.001 GEN | `1000000000000000` |
| 0.01 GEN | `10000000000000000` |
| 0.1 GEN | `100000000000000000` |
| **1 GEN** | **`1000000000000000000`** (18 zeros) |
| 5 GEN | `5000000000000000000` |
| 10 GEN | `10000000000000000000` |
| 1000 GEN | `1000000000000000000000` |

> 💡 In the GenLayer Studio, when you send value via payable methods (like `pay_for_access`), the Studio UI automatically converts your input by multiplying with 10¹⁸. So typing `1` in the Value field sends 1 GEN = 10¹⁸ wei. However, **constructor arguments** are read as-is, so you must type the full wei value there.

---

### Method 1: CLI Direct (Per Contract)

**Best for:** deploying one contract at a time, quick iteration, testing.

Follows the [CLI Deployment docs](https://docs.genlayer.com/developers/intelligent-contracts/deploying/cli-deployment). The CLI will interactively prompt you for the constructor arguments.

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

| Argument | Value | In GEN |
|---|---|---|
| `price_wei` | `1000000000000000000` | 1 GEN |
| `data_url` | `https://api.github.com/users/octocat` | - |

#### Deploy X402Metered

```bash
genlayer deploy --contract contracts/x402_metered.py
```

When prompted, enter:

| Argument | Value | In GEN |
|---|---|---|
| `price_per_call_wei` | `1000000000000000000` | 1 GEN per call |
| `data_url_prefix` | `https://api.github.com/users/` | - |
| `max_credits` | `1000` | - |

#### Deploy X402Subscription

```bash
genlayer deploy --contract contracts/x402_subscription.py
```

When prompted, enter:

| Argument | Value | In GEN |
|---|---|---|
| `price_per_period_wei` | `1000000000000000000` | 1 GEN per period |
| `calls_per_period` | `10` | - |
| `data_url` | `https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate` | - |

#### Deploy X402Escrow

The escrow uses a **structured brief** with 4 fields (each with minimum length) plus an arbiter address and claim attempts limit — this prevents trivial briefs like "make me a website" and prevents permanent lockup if the client goes offline.

```bash
genlayer deploy --contract contracts/x402_escrow.py
```

When prompted, enter:

| Argument | Min length | Example Value |
|---|---|---|
| `brief_title` | 10 chars | `Bitcoin Price Fetcher Python Script` |
| `brief_description` | 80 chars | `Build a Python script that fetches the current Bitcoin price from the CoinGecko API and prints it in formatted output with timestamp and 24h change percentage.` |
| `brief_acceptance_criteria` | 80 chars | `Script must run without errors on Python 3.10+. Must use requests library. Must print price in USD format. Must include error handling for API failures. Code must be PEP8 compliant.` |
| `brief_deliverable_format` | 30 chars | `Single Python file named btc_price.py, committed to a public GitHub repo` |
| `arbiter_addr` | — | `0x0000000000000000000000000000000000000000` (or a real neutral 3rd party address) |
| `max_claim_attempts` | min 3 | `3` |

Total content must be **≥ 200 characters** combined.

#### Expected output

```
✅ Contract deployed successfully!
Transaction Hash: 0x1234567890abcdef...
Contract Address: 0xabcdef1234567890...
```

**Save the contract address** — you'll need it to interact with the contract.

---

### Method 2: Batch Deploy Script (All 4 at Once)

**Best for:** deploying all 4 contracts at once with pre-configured values.

This repo includes `deploy/deployScript.ts` — a TypeScript batch deployer.

```bash
genlayer deploy
```

The CLI detects `deploy/deployScript.ts` and runs it, deploying all 4 contracts in sequence.

To customize constructor values, edit the `args` arrays in `deploy/deployScript.ts`.

---

### Method 3: GenLayer Studio

**Best for:** beginners, visual exploration, no-CLI deployments.

1. Open [studio.genlayer.com](https://studio.genlayer.com) or `http://localhost:8080`
2. Click **Load Contract** → paste contract code
3. Click **Deploy** → fill in constructor fields → confirm
4. Copy the transaction hash and contract address

---

## Interacting with Deployed Contracts

### Via CLI

#### Read methods (free, no transaction)

```bash
# Get the current access price
genlayer call --address 0xYOUR_PAYWALL --function get_price

# Check if user has been granted access (explicit flag — never revoked)
genlayer call --address 0xYOUR_PAYWALL --function has_access --args 0xUSER_ADDRESS

# Get contract balance
genlayer call --address 0xYOUR_PAYWALL --function get_contract_balance

# Get x402 protocol info
genlayer call --address 0xYOUR_PAYWALL --function get_402_info
```

#### Write methods (costs gas, may send value)

```bash
# Pay 100 wei for permanent access
genlayer write --address 0xYOUR_PAYWALL --function pay_for_access --value 100

# Fetch gated data (after paying)
genlayer write --address 0xYOUR_PAYWALL --function get_protected_data

# Owner withdraws specific amount of accumulated revenue
genlayer write --address 0xYOUR_PAYWALL --function withdraw --args 500

# Owner withdraws entire contract balance
genlayer write --address 0xYOUR_PAYWALL --function withdraw_all
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
| `has_access(user)` | `bool` | **True if user has paid (explicit flag, never revoked)** |
| `get_payment(user)` | `u256` | Total amount user has paid |
| `get_total_revenue()` | `u256` | Cumulative revenue |
| `get_contract_balance()` | `u256` | Current GEN held by contract |
| `get_402_info()` | `str` | JSON metadata (x402 spec) |

**Write methods:**

| Method | Value | Description |
|---|---|---|
| `pay_for_access()` | ≥ `price_wei` | Purchase permanent access (sets `access_granted` flag) |
| `get_protected_data()` | 0 | Fetch live data (paid users only) |
| `update_price(new_price)` | 0 | Owner only — does NOT revoke existing buyers |
| `update_data_url(new_url)` | 0 | Owner only |
| `withdraw(amount)` | 0 | Owner only — withdraw specific amount |
| `withdraw_all()` | 0 | Owner only — withdraw entire balance |

---

### X402Metered — Pay Per Call

**Constructor:**

| Parameter | Type | Description |
|---|---|---|
| `price_per_call_wei` | `u256` | Cost per API call |
| `data_url_prefix` | `str` | URL prefix (query param appended) |
| `max_credits` | `u256` | Max credits per user (anti-abuse) |

**Read methods:**

| Method | Returns |
|---|---|
| `get_price_per_call()` | `u256` |
| `check_credits(user)` | `u256` |
| `get_call_count(user)` | `u256` |
| `get_total_calls()` | `u256` |
| `get_total_revenue()` | `u256` |
| `get_contract_balance()` | `u256` |

**Write methods:**

| Method | Args / Value | Description |
|---|---|---|
| `buy_credits()` | value ≥ price | Get `floor(value / price)` credits |
| `execute_query(q)` | string | Consume 1 credit, fetch + AI-summarize |
| `grant_credits(user, n)` | args | Owner only |
| `withdraw(amount)` | 0 | Owner only |
| `withdraw_all()` | 0 | Owner only |

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
| `withdraw(amount)` | 0 | Owner only |
| `withdraw_all()` | 0 | Owner only |

---

### X402Escrow — AI-Verified Payment (Enhanced)

**Constructor:**

| Parameter | Type | Min / Constraint | Description |
|---|---|---|---|
| `brief_title` | `str` | 10 chars | Short work title |
| `brief_description` | `str` | 80 chars | Detailed work description |
| `brief_acceptance_criteria` | `str` | 80 chars | Measurable acceptance criteria |
| `brief_deliverable_format` | `str` | 30 chars | Expected output format |
| `arbiter_addr` | `Address` | — | Neutral 3rd party for dispute resolution |
| `max_claim_attempts` | `u256` | min 3 | Attempts before force_release unlocks |

Total brief content must be **≥ 200 characters** combined.

**State flow:**
```
OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED
```

**Write methods:**

| Method | Args / Value | Who can call | Description |
|---|---|---|---|
| `fund(freelancer)` | value > 0 | Client | Fund escrow + assign freelancer |
| `submit_work(url, desc)` | args | Freelancer | Submit work → AI evaluates |
| `release_payment()` | 0 | Anyone | Pay freelancer (if APPROVED) |
| `client_approve()` | 0 | Client | Override AI verdict |
| `client_cancel()` | 0 | Client | Refund (if still FUNDED) |
| `arbiter_rule(approve)` | bool | Arbiter | Resolve DISPUTED (approve=release, false=refund) |
| `freelancer_claim_attempt()` | 0 | Freelancer | Log attempt in DISPUTED |
| `force_release()` | 0 | Freelancer | Timeout safety: unlock after `max_claim_attempts` |

---

## Security Features

Key security and reliability features built into the library:

### 1. Explicit Access Flag (Paywall)

Access is stored as a boolean flag when users pay, not recomputed from current price. **Owners can raise prices without revoking existing buyers' access.**

```python
access_granted: TreeMap[Address, bool]  # explicit, immutable after set

def has_access(self, user) -> bool:
    return self.access_granted.get(user, False)  # just reads the flag
```

### 2. Revenue Withdrawal (All 3 Payment Contracts)

Paywall, Metered, and Subscription all have `withdraw()` and `withdraw_all()`. Revenue is never stuck in the contract.

```python
def withdraw(self, amount: u256):
    assert gl.message.sender_address == self.owner
    _EOA(self.owner).emit_transfer(value=amount)
```

### 3. Escrow Anti-Lockup

Three mechanisms prevent permanent fund lockup in DISPUTED state:

- **Arbiter rule** — neutral 3rd party can resolve via `arbiter_rule(approve)`
- **Claim attempts counter** — freelancer logs attempts with `freelancer_claim_attempt()`
- **Force release** — after `max_claim_attempts`, freelancer can `force_release()` to unlock

### 4. Structured Brief (Escrow)

Instead of a single 20-char brief, constructor requires 4 separate structured fields with individual minimums totaling 200+ characters. Rejects trivial briefs like "make me a website".

---

## Use Case Examples

### Example 1: Paid Bitcoin Price Feed

```bash
# Deploy
genlayer deploy --contract contracts/x402_paywall.py
# price_wei=100, data_url=https://api.coinbase.com/v2/prices/BTC-USD/spot

# User pays
genlayer write --address 0xCONTRACT --function pay_for_access --value 100

# User fetches live BTC price
genlayer write --address 0xCONTRACT --function get_protected_data

# Even if owner updates price later, user still has access
genlayer write --address 0xCONTRACT --function update_price --args 500
genlayer call --address 0xCONTRACT --function has_access --args 0xUSER
# Returns: true  ← permanent access

# Owner withdraws revenue
genlayer write --address 0xCONTRACT --function withdraw_all
```

### Example 2: Metered AI Query API

```bash
# Deploy + buy 50 credits
genlayer write --address 0xCONTRACT --function buy_credits --value 500

# Each query costs 1 credit
genlayer write --address 0xCONTRACT --function execute_query --args "bitcoin"

# Owner withdraws accumulated revenue
genlayer write --address 0xCONTRACT --function withdraw --args 1000
```

### Example 3: AI-Verified Freelance Escrow

```bash
# 1. Client deploys with structured 200+ char brief
genlayer deploy --contract contracts/x402_escrow.py
# Fill all 6 fields (title, description, criteria, format, arbiter, max_attempts)

# 2. Client funds + assigns freelancer
genlayer write --address 0xCONTRACT --function fund --args 0xFREELANCER --value 500

# 3. Freelancer submits → AI evaluates
genlayer write --address 0xCONTRACT --function submit_work \
  --args "https://github.com/bob/work" "Completed script"

# 4a. If AI approves → release payment
genlayer write --address 0xCONTRACT --function release_payment

# 4b. If DISPUTED and client goes offline → freelancer safety valve:
genlayer write --address 0xCONTRACT --function freelancer_claim_attempt  # x3
genlayer write --address 0xCONTRACT --function force_release             # unlocks!

# 4c. Or arbiter resolves:
genlayer write --address 0xCONTRACT --function arbiter_rule --args true
```

---

## Linting

Before deploying, always lint all contracts:

```bash
genvm-lint check contracts/x402_paywall.py
genvm-lint check contracts/x402_metered.py
genvm-lint check contracts/x402_subscription.py
genvm-lint check contracts/x402_escrow.py
```

See [GenVM Linter docs](https://docs.genlayer.com/api-references/genlayer-linter).

---

## Project Structure

```
genlayer-x402/
│
├── contracts/                      # Intelligent Contracts (Python)
│   ├── x402_paywall.py             # One-time payment + withdraw
│   ├── x402_metered.py             # Per-call billing + withdraw
│   ├── x402_subscription.py        # Quota access + withdraw
│   └── x402_escrow.py              # AI escrow + arbiter + timeout
│
├── deploy/
│   └── deployScript.ts             # Batch deploy all 4 contracts
│
├── docs/                           # Testing guides per contract
│   ├── TESTING.md                  # Overview & general setup
│   ├── test-paywall.md             # X402Paywall step-by-step
│   ├── test-metered.md             # X402Metered step-by-step
│   ├── test-subscription.md        # X402Subscription step-by-step
│   └── test-escrow.md              # X402Escrow step-by-step
│
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
├── gltest.config.yaml
├── package.json
├── requirements.txt
└── tsconfig.json
```

---

## Testing Guides

Each contract has its own detailed step-by-step testing guide in the `docs/` folder:

| Contract | Testing Guide | Est. Time |
|---|---|---|
| Overview + Setup | [docs/TESTING.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/TESTING.md) | 5 min read |
| X402Paywall | [docs/test-paywall.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-paywall.md) | ~20 min |
| X402Metered | [docs/test-metered.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-metered.md) | ~25 min |
| X402Subscription | [docs/test-subscription.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-subscription.md) | ~30 min |
| X402Escrow | [docs/test-escrow.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-escrow.md) | ~40 min |

Each guide includes full workflow, error handling tests, and quick demo scripts.

---

## Troubleshooting

### Lint fails with "No contract class found"

Class name must be specific (e.g., `X402Paywall`), not generic `Contract`.

### Lint fails with "gl.nondet.* call not reachable"

Wrap non-deterministic calls inside `gl.eq_principle.strict_eq()` or `gl.eq_principle.prompt_comparative()`:

```python
def nondet() -> str:
    response = gl.nondet.web.get(url)       # ✓ inside nondet
    return response.body.decode("utf-8")

return gl.eq_principle.strict_eq(nondet)    # ✓
```

### "Brief too short" when deploying escrow

Escrow requires 4 structured fields, each with minimum length, totaling 200+ chars. Expand each field with real acceptance criteria.

### Funds stuck in contract?

Owner can withdraw anytime via `withdraw(amount)` or `withdraw_all()`. If you deployed an older version without these methods, redeploy with the latest contracts.

### Freelancer locked out in escrow DISPUTED state?

Call `freelancer_claim_attempt()` repeatedly until `claim_attempts >= max_claim_attempts`, then call `force_release()` to unlock the funds. This is the timeout safety valve.

### "Insufficient balance" on testnet

Request test GEN from [testnet-faucet.genlayer.foundation](https://testnet-faucet.genlayer.foundation/).

### TypeScript warning in deployScript.ts

Already handled with `as any` and optional chaining. Warning is compile-time only — deploy still works.

### `git push` stuck with CRLF warnings

`node_modules/` accidentally tracked. Fix:
```bash
git rm -r --cached node_modules
git config --global core.autocrlf true
git add .gitignore
git commit -m "chore: remove node_modules from tracking"
git push origin main
```

---

## Resources

- 📖 [GenLayer Docs](https://docs.genlayer.com)
- 📘 [GenLayer SDK Reference](https://sdk.genlayer.com)
- 🎮 [GenLayer Studio](https://studio.genlayer.com)
- 🔧 [GenVM Linter Docs](https://docs.genlayer.com/api-references/genlayer-linter)
- 💧 [Testnet Faucet](https://testnet-faucet.genlayer.foundation/)
- 📜 [x402 Protocol Spec](https://x402.org)
- 🏆 [GenLayer Builder Program](https://portal.genlayer.foundation)

---

## Changelog

See [CHANGELOG.md](https://github.com/habiiyt31/genlayer-x402/blob/main/CHANGELOG.md) for the full version history.

---

## Contributing

Issues and pull requests welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes with clear messages
4. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE).

