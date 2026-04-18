# genlayer-x402

> x402 Payment Protocol for GenLayer Intelligent Contracts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GenLayer](https://img.shields.io/badge/Built%20on-GenLayer-orange)](https://genlayer.com)
[![x402](https://img.shields.io/badge/Protocol-x402-blue)](https://x402.org)

---

## What is this?

**genlayer-x402** is the first library implementing the [x402 HTTP Payment Protocol](https://x402.org) natively inside [GenLayer Intelligent Contracts](https://docs.genlayer.com).

It bridges two cutting-edge technologies:
- **GenLayer** — AI-powered blockchain where contracts can read the web and reason with LLMs
- **x402** — Open standard for pay-per-request internet payments using USDC/stablecoins

Instead of API keys, subscriptions, or centralized billing, **genlayer-x402** lets you gate any data or service behind a trustless, on-chain payment that settles in under a second.

---

## The 4 Contracts

| Contract | Use Case | Points per request |
|---|---|---|
| `x402_paywall.py` | One-time payment → permanent access | Fixed price |
| `x402_metered.py` | Buy credits, spend per call | Per call |
| `x402_subscription.py` | Pay per period, renew to extend | Per period |
| `x402_escrow.py` | AI-verified freelance payment release | Per job |

---

## Quick Start

### 1. Try in Browser (No Setup)

Open [studio.genlayer.com](https://studio.genlayer.com) and paste any contract from `contracts/`.

### 2. Local Setup

```bash
# Clone this repo
git clone https://github.com/habiiyt31/genlayer-x402.git
cd genlayer-x402

# Start local GenLayer environment
npm install -g genlayer
genlayer init
genlayer up
```

### 3. Deploy

```bash
# Deploy all contracts
python deploy/deploy_all.py

# Deploy specific contract
python deploy/deploy_all.py --contract paywall
```

---

## Contract Details

### x402_paywall — One-Time Access

```
User calls get_protected_data()
  → No payment: Error "x402: Payment required. Price: 100 wei"
  → User calls pay_for_access() with 100 wei
  → User calls get_protected_data() again
  → Contract fetches real URL and returns data ✓
```

```python
# Deploy with price and data URL
contract = X402Paywall(
    price_wei = 100,
    data_url  = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
)

# User flow
contract.get_402_info()          # → {"price_wei": 100, "protocol": "x402-genlayer"}
contract.pay_for_access()        # ← send 100 wei
contract.get_protected_data(user) # → real-time Bitcoin price data
```

---

### x402_metered — Pay Per Call

```
User buys 10 credits (100 wei each = 1000 wei total)
  → Each execute_query() call deducts 1 credit
  → At 0 credits: "x402: No credits remaining. Buy via buy_credits()"
  → User tops up at any time
```

```python
contract = X402Metered(
    price_per_call_wei = 100,
    data_url           = "https://api.coingecko.com/api/v3/simple/price?ids=",
    max_credits        = 50
)

contract.buy_credits()              # ← send 500 wei → get 5 credits
contract.check_credits(user)        # → 5
contract.execute_query("bitcoin")   # → AI-summarized price data, credits → 4
```

---

### x402_subscription — Time-Based Access

```
User subscribes for 1 period (1000 blocks ≈ 33 min)
  → is_active() returns True until block 1000
  → get_data() works while active
  → After expiry: "x402: Subscription expired"
  → User renews by calling subscribe() again
```

```python
contract = X402Subscription(
    price_per_period_wei = 100,
    period_blocks        = 1000,
    data_url             = "https://api.github.com/repos/genlayerlabs/..."
)

contract.subscribe(1)           # ← send 100 wei → active for 1000 blocks
contract.is_active(user)        # → True
contract.get_data(user)         # → live data from URL
```

---

### x402_escrow — AI-Verified Freelance Payment

The most innovative contract: uses **GenLayer's LLM consensus** to automatically judge if work meets the client brief. No human arbitrator needed.

```
1. Client creates escrow with brief + deadline
2. Client funds escrow (GEN held in contract)
3. Freelancer submits work URL
4. GenLayer validators fetch URL + run LLM evaluation
5. If approved → payment auto-released to freelancer
   If disputed → client can override or wait for deadline
```

```python
contract = X402Escrow(
    brief            = "Build a React landing page with Tailwind CSS",
    deadline_blocks  = 500
)

# Client funds, assigns freelancer
contract.fund(freelancer_address)     # ← send 500 wei

# Freelancer submits
contract.submit_work(
    work_url         = "https://github.com/bob/landing-page",
    work_description = "React + Tailwind, fully responsive"
)

# AI evaluates → APPROVED or DISPUTED
contract.get_state()   # → "APPROVED"

# Payment released
contract.release_payment()  # freelancer receives 500 wei
```

---

## Why GenLayer + x402?

Traditional x402 implementations gate HTTP endpoints on a server. **genlayer-x402** moves the gate on-chain:

| Feature | Traditional x402 | genlayer-x402 |
|---|---|---|
| Payment verification | Server-side | On-chain, trustless |
| Data delivery | Centralized server | GenLayer Intelligent Contract |
| AI judgment | Not possible | Built-in via LLM consensus |
| Censorship resistance | Low (server can block) | High (blockchain) |
| Audit trail | Server logs | Immutable on-chain |

---

## Architecture

```
Client Request
     │
     ▼
GenLayer Intelligent Contract
     │
     ├── Check payment status (on-chain state)
     │
     ├── If paid: gl.get_webpage(data_url)  ← fetch real data
     │                │
     │                ▼
     │           gl.eq_principle_strict_eq()
     │           (5 validators reach consensus)
     │                │
     └── Return data to client
```

---

## Running on Testnet Bradbury

1. Get testnet GEN from [testnet-faucet.genlayer.foundation](https://testnet-faucet.genlayer.foundation/)
2. Export your private key
3. Set in environment:
   ```bash
   export ACCOUNT_PRIVATE_KEY_1=0x...
   ```
4. Deploy:
   ```bash
   genlayer network set testnet_bradbury
   python deploy/deploy_all.py
   ```

---

## Contributing

Issues and PRs welcome. This library is a contribution to the GenLayer ecosystem.

## License

MIT — see [LICENSE](LICENSE)

---

Built for the [GenLayer Builder Program](https://portal.genlayer.foundation) 🧠⚡
