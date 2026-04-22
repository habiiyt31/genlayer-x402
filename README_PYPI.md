# genlayer-x402

> **x402 Payment Protocol for GenLayer Intelligent Contracts**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GenLayer](https://img.shields.io/badge/Built%20on-GenLayer-orange)](https://docs.genlayer.com)
[![x402](https://img.shields.io/badge/Protocol-x402-blue)](https://x402.org)
[![PyPI](https://img.shields.io/pypi/v/genlayer-x402)](https://pypi.org/project/genlayer-x402/)

A library of **4 production-ready Intelligent Contracts** that bring the [HTTP 402 Payment Required](https://x402.org) standard onto the GenLayer blockchain. Gate real-time web data and AI services behind trustless, on-chain payments — without any server, API key, or middleman.

## What is this?

Traditional paid APIs rely on centralized servers with API keys — fragile, censorable, and opaque. `genlayer-x402` moves the payment gate **fully on-chain**:

- **Trustless verification** — payment checked by GenLayer validators, not a central server
- **Real-time web data** — contracts fetch live data via `gl.nondet.web.get()` after payment clears
- **AI-powered judgment** — the escrow contract uses LLM consensus to auto-approve/reject deliverables
- **Revenue withdrawal** — owners can withdraw accumulated revenue to their wallet anytime
- **Immutable access** — once a user pays, price changes never revoke their access
- **Anti-lockup safeguards** — escrow has arbiter + timeout mechanisms to prevent stuck funds

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

GenLayer contracts run as **single Python files**, so you need to copy them into your project before deploying.

### Recommended (CLI)

After installing the package, run:

```bash
genlayer-x402 init
```
This will create a contracts/ folder with all contracts:

contracts/
├── x402_paywall.py
├── x402_metered.py
├── x402_subscription.py
├── x402_escrow.py

### Copy a single contract

```bash
genlayer-x402 paywall
genlayer-x402 metered
genlayer-x402 subscription
genlayer-x402 escrow
```
---
### List available contracts

```bash
genlayer-x402 list
```
---

## 🧰 CLI Usage

| Command | Description |
|--------|------------|
| `genlayer-x402 init` | Copy all contracts |
| `genlayer-x402 paywall` | Copy paywall contract |
| `genlayer-x402 metered` | Copy metered contract |
| `genlayer-x402 subscription` | Copy subscription contract |
| `genlayer-x402 escrow` | Copy escrow contract |
| `genlayer-x402 list` | Show available contracts |


## Testing Guides

Each contract has a detailed step-by-step testing guide in the `docs/` folder:

| Contract | Guide | Est. Time |
|---|---|---|
| Overview + Setup | [docs/TESTING.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/TESTING.md) | 5 min |
| X402Paywall | [docs/test-paywall.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-paywall.md) | ~20 min |
| X402Metered | [docs/test-metered.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-metered.md) | ~25 min |
| X402Subscription | [docs/test-subscription.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-subscription.md) | ~30 min |
| X402Escrow | [docs/test-escrow.md](https://github.com/habiiyt31/genlayer-x402/blob/main/docs/test-escrow.md) | ~40 min |

---

## Contributing

Issues and pull requests welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes with clear messages
4. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE).