# genlayer-x402

> **x402 Payment Protocol for GenLayer Intelligent Contracts**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GenLayer](https://img.shields.io/badge/Built%20on-GenLayer-orange)](https://docs.genlayer.com)
[![x402](https://img.shields.io/badge/Protocol-x402-blue)](https://x402.org)
[![PyPI](https://img.shields.io/pypi/v/genlayer-x402)](https://pypi.org/project/genlayer-x402/)

A library of **4 production-ready Intelligent Contracts** that bring the [HTTP 402 Payment Required](https://x402.org) standard onto the GenLayer blockchain. Gate real-time web data and AI services behind trustless, on-chain payments — without any server, API key, or middleman.

---

## Table of Contents

- [What is this?](#what-is-this)
- [The 4 Contracts](#the-4-contracts)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting the Contract Files](#getting-the-contract-files)
- [Deployment](#deployment)
  - [Method 1: CLI Direct (Per Contract)](#method-1-cli-direct-per-contract)
  - [Method 2: GenLayer Studio](#method-3-genlayer-studio)
- [Interacting with Contracts](#interacting-with-deployed-contracts)
- [Contract API Reference](#contract-api-reference)
- [Use Case Examples](#use-case-examples)
- [Security Features](#security-features)
- [Linting](#linting)
- [Testing Guides](#testing-guides)
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

---

## The 4 Contracts

| Contract | Pattern | Best For |
|---|---|---|
| `x402_paywall.py` | One-time payment → permanent access | Premium reports, data dumps, gated docs |
| `x402_metered.py` | Buy credits, deducted per call | AI inference, per-query analytics |
| `x402_subscription.py` | N calls per period, renewable | Streaming feeds, quota-based plans |
| `x402_escrow.py` | AI-verified milestone payment | Freelance work, deliverable contracts |

All 4 contracts support **owner revenue withdrawal** via `withdraw()` and `withdraw_all()`.

---

## Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/en/download/)
- **Docker 26+** — [Download](https://docs.docker.com/get-docker/) (only if running local Studio)
- **A funded GenLayer account** — Get test GEN from the [testnet faucet](https://testnet-faucet.genlayer.foundation/)

---

## Installation

```bash
pip install genlayer-x402
```

Also install the linter and GenLayer CLI:

```bash
pip install genvm-linter
npm install -g genlayer
```

---

## Getting the Contract Files

Since GenLayer contracts run as **single Python files** in GenVM, you need to copy the contract files to your project before deploying.

### Find where the package is installed

```bash
python -c "import genlayer_x402, os; print(os.path.dirname(genlayer_x402.__file__))"
```

### Copy contracts to your project

```bash
# Copy all contracts at once
python -c "
import genlayer_x402, os, shutil
src = os.path.dirname(genlayer_x402.__file__)
os.makedirs('contracts', exist_ok=True)
for f in ['x402_paywall', 'x402_metered', 'x402_subscription', 'x402_escrow']:
    shutil.copy(f'{src}/{f}.py', f'contracts/{f}.py')
    print(f'Copied {f}.py')
"
```

Or copy individually:

```bash
# Windows (PowerShell)
python -c "import genlayer_x402,os; p=os.path.dirname(genlayer_x402.__file__); print(p)"
# Then: copy <path>\x402_paywall.py contracts\

# macOS/Linux
cp $(python -c "import genlayer_x402,os; print(os.path.dirname(genlayer_x402.__file__))")/x402_paywall.py contracts/
```

> ⚠️ **Important:** Each contract file is self-contained. You only need to copy the contract(s) you want to deploy — no other dependencies required.

---

## Deployment

### Understanding Wei and GEN Units

GenLayer uses **GEN** as its native token, denominated in **wei**:

> **1 GEN = 10¹⁸ wei = 1,000,000,000,000,000,000 wei**

| Amount in GEN | Amount in Wei |
|---|---|
| 0.001 GEN | `1000000000000000` |
| 0.01 GEN | `10000000000000000` |
| 0.1 GEN | `100000000000000000` |
| **1 GEN** | **`1000000000000000000`** |
| 5 GEN | `5000000000000000000` |

> 💡 In GenLayer Studio, the Value field auto-multiplies by 10¹⁸. But **constructor arguments** must be entered as full wei values.

---

### Method 1: CLI Direct (Per Contract)

Set your network first:

```bash
genlayer network set localnet       # local development
genlayer network set testnet-bradbury  # public testnet
```

#### Deploy X402Paywall

```bash
genlayer deploy --contract contracts/x402_paywall.py
```

| Argument | Example Value |
|---|---|
| `price_wei` | `1000000000000000000` (1 GEN) |
| `data_url` | `https://api.github.com/users/octocat` |

#### Deploy X402Metered

```bash
genlayer deploy --contract contracts/x402_metered.py
```

| Argument | Example Value |
|---|---|
| `price_per_call_wei` | `1000000000000000000` (1 GEN per call) |
| `data_url_prefix` | `https://api.github.com/users/` |
| `max_credits` | `1000` |

#### Deploy X402Subscription

```bash
genlayer deploy --contract contracts/x402_subscription.py
```

| Argument | Example Value |
|---|---|
| `price_per_period_wei` | `1000000000000000000` (1 GEN per period) |
| `calls_per_period` | `10` |
| `data_url` | `https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate` |

#### Deploy X402Escrow

```bash
genlayer deploy --contract contracts/x402_escrow.py
```

| Argument | Min Length | Example Value |
|---|---|---|
| `brief_title` | 10 chars | `Bitcoin Price Fetcher Python Script` |
| `brief_description` | 80 chars | `Build a Python script that fetches the current Bitcoin price from CoinGecko API and prints it with timestamp and 24h change percentage.` |
| `brief_acceptance_criteria` | 80 chars | `Script must run without errors on Python 3.10+. Must use requests library. Must print price in USD format. Must include error handling for API failures.` |
| `brief_deliverable_format` | 30 chars | `Single Python file named btc_price.py committed to a public GitHub repo` |
| `arbiter_addr` | — | `0x0000000000000000000000000000000000000000` |
| `max_claim_attempts` | min 3 | `3` |

> Total brief content must be **≥ 200 characters** combined.

---

### Method 2: GenLayer Studio

1. Open [studio.genlayer.com](https://studio.genlayer.com)
2. Click **Load Contract** → paste contract code
3. Click **Deploy** → fill constructor fields → confirm
4. Copy the contract address

---

## Interacting with Deployed Contracts

### Read methods (free)

```bash
genlayer call --address 0xYOUR_CONTRACT --function get_price
genlayer call --address 0xYOUR_CONTRACT --function has_access --args 0xUSER_ADDRESS
genlayer call --address 0xYOUR_CONTRACT --function get_contract_balance
genlayer call --address 0xYOUR_CONTRACT --function get_402_info
```

### Write methods

```bash
# Pay for access
genlayer write --address 0xYOUR_CONTRACT --function pay_for_access --value 1000000000000000000

# Fetch gated data
genlayer write --address 0xYOUR_CONTRACT --function get_protected_data

# Owner withdraws revenue
genlayer write --address 0xYOUR_CONTRACT --function withdraw_all
```

---

## Contract API Reference

### X402Paywall

**Constructor:** `price_wei (u256)`, `data_url (str)`

| Method | Type | Description |
|---|---|---|
| `get_price()` | read | Current access price in wei |
| `has_access(user)` | read | True if user has paid (never revoked) |
| `get_payment(user)` | read | Total amount user has paid |
| `get_total_revenue()` | read | Cumulative revenue |
| `get_contract_balance()` | read | Current GEN held by contract |
| `pay_for_access()` | write payable | Purchase permanent access |
| `get_protected_data()` | write | Fetch live data (paid users only) |
| `update_price(new_price)` | write | Owner only — does NOT revoke existing buyers |
| `update_data_url(new_url)` | write | Owner only |
| `withdraw(amount)` | write | Owner only |
| `withdraw_all()` | write | Owner only |

---

### X402Metered

**Constructor:** `price_per_call_wei (u256)`, `data_url_prefix (str)`, `max_credits (u256)`

| Method | Type | Description |
|---|---|---|
| `check_credits(user)` | read | Remaining credits |
| `get_call_count(user)` | read | Total calls made |
| `get_total_calls()` | read | Global call counter |
| `buy_credits()` | write payable | Get `floor(value / price)` credits |
| `execute_query(q)` | write | Consume 1 credit, fetch + AI-summarize |
| `grant_credits(user, n)` | write | Owner only |
| `withdraw(amount)` | write | Owner only |
| `withdraw_all()` | write | Owner only |

---

### X402Subscription

**Constructor:** `price_per_period_wei (u256)`, `calls_per_period (u256)`, `data_url (str)`

| Method | Type | Description |
|---|---|---|
| `get_remaining_calls(user)` | read | Remaining call quota |
| `is_active(user)` | read | True if quota > 0 |
| `get_subscriber_count()` | read | Total unique subscribers |
| `subscribe(periods)` | write payable | Add `periods × calls_per_period` calls |
| `get_data()` | write | Fetch data, consumes 1 call |
| `grant_access(user, periods)` | write | Owner only |
| `withdraw(amount)` | write | Owner only |
| `withdraw_all()` | write | Owner only |

---

### X402Escrow

**Constructor:** `brief_title`, `brief_description`, `brief_acceptance_criteria`, `brief_deliverable_format`, `arbiter_addr`, `max_claim_attempts`

**State flow:** `OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED`

| Method | Who | Description |
|---|---|---|
| `fund(freelancer)` | Client | Fund escrow + assign freelancer |
| `submit_work(url, desc)` | Freelancer | Submit → AI evaluates |
| `release_payment()` | Anyone | Pay freelancer if APPROVED |
| `client_approve()` | Client | Override AI verdict manually |
| `client_cancel()` | Client | Refund if still FUNDED |
| `arbiter_rule(approve)` | Arbiter | Resolve DISPUTED state |
| `freelancer_claim_attempt()` | Freelancer | Log attempt in DISPUTED |
| `force_release()` | Freelancer | Unlock after max_claim_attempts |

---

## Security Features

- **Explicit access flag** — `has_access` reads a stored flag, not current price. Price changes never revoke existing access.
- **Revenue withdrawal** — funds never stuck in contract, owner withdraws anytime.
- **Escrow anti-lockup** — 3 mechanisms: arbiter rule, claim attempts counter, force release timeout.
- **Structured brief** — escrow rejects trivial briefs with minimum length requirements per field.

---

## Use Case Examples

### Paid Bitcoin Price Feed (Paywall)

```bash
genlayer deploy --contract contracts/x402_paywall.py
# price_wei=1000000000000000000, data_url=https://api.coinbase.com/v2/prices/BTC-USD/spot

genlayer write --address 0xCONTRACT --function pay_for_access --value 1000000000000000000
genlayer write --address 0xCONTRACT --function get_protected_data
genlayer write --address 0xCONTRACT --function withdraw_all
```

### Metered AI Query API

```bash
genlayer write --address 0xCONTRACT --function buy_credits --value 5000000000000000000
genlayer write --address 0xCONTRACT --function execute_query --args "bitcoin"
genlayer write --address 0xCONTRACT --function withdraw --args 1000000000000000000
```

### AI-Verified Freelance Escrow

```bash
# Client funds
genlayer write --address 0xCONTRACT --function fund --args 0xFREELANCER --value 5000000000000000000

# Freelancer submits → AI evaluates
genlayer write --address 0xCONTRACT --function submit_work --args "https://github.com/bob/work" "Completed"

# If approved
genlayer write --address 0xCONTRACT --function release_payment

# If disputed and client offline → freelancer safety valve
genlayer write --address 0xCONTRACT --function freelancer_claim_attempt  # repeat 3x
genlayer write --address 0xCONTRACT --function force_release
```

---

## Linting

Before deploying, lint your contracts:

```bash
genvm-lint check contracts/x402_paywall.py
genvm-lint check contracts/x402_metered.py
genvm-lint check contracts/x402_subscription.py
genvm-lint check contracts/x402_escrow.py
```
---

## Testing Guides

Each contract has a detailed step-by-step testing guide in the `docs/` folder:

| Contract | Guide | Est. Time |
|---|---|---|
| Overview + Setup | [docs/TESTING.md](docs/TESTING.md) | 5 min |
| X402Paywall | [docs/test-paywall.md](docs/test-paywall.md) | ~20 min |
| X402Metered | [docs/test-metered.md](docs/test-metered.md) | ~25 min |
| X402Subscription | [docs/test-subscription.md](docs/test-subscription.md) | ~30 min |
| X402Escrow | [docs/test-escrow.md](docs/test-escrow.md) | ~40 min |

---

## Troubleshooting

**"No contract class found"** — class name must match exactly, e.g. `X402Paywall`.

**"gl.nondet.* call not reachable"** — wrap non-deterministic calls inside `gl.eq_principle.strict_eq()` or `gl.eq_principle.prompt_comparative()`.

**"Brief too short" when deploying escrow** — expand each field to meet minimum length requirements. Total must be ≥ 200 chars.

**Funds stuck in contract** — owner calls `withdraw_all()` anytime.

**Freelancer locked in DISPUTED** — call `freelancer_claim_attempt()` until `claim_attempts >= max_claim_attempts`, then call `force_release()`.

**"Insufficient balance" on testnet** — get test GEN from [testnet-faucet.genlayer.foundation](https://testnet-faucet.genlayer.foundation/).

**Lint fails with relative import error** — contracts must be copied to your local project folder before linting. See [Getting the Contract Files](#getting-the-contract-files).

---

## Resources

- 📖 [GenLayer Docs](https://docs.genlayer.com)
- 📘 [GenLayer SDK Reference](https://sdk.genlayer.com)
- 🎮 [GenLayer Studio](https://studio.genlayer.com)
- 🔧 [GenVM Linter Docs](https://docs.genlayer.com/api-references/genlayer-linter)
- 💧 [Testnet Faucet](https://testnet-faucet.genlayer.foundation/)
- 📜 [x402 Protocol Spec](https://x402.org)

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## Contributing

Issues and pull requests welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes with clear messages
4. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE).