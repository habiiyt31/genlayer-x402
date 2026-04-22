# Testing X402Metered

Step-by-step testing guide for the X402Metered contract — credit-based pay-per-call API billing with AI summaries.

---

## 📋 About This Contract

**Use case:** Users buy credits with GEN, each API call deducts 1 credit. Contract fetches web data and uses AI (LLM) to summarize on-chain.

**Key features tested:**
- Credit-based pay-per-call billing
- AI-powered response summarization via GenLayer validators
- Max credits cap to prevent abuse
- Owner grant_credits for promo
- Revenue withdrawal

**Total methods:** 15 (8 view + 7 write)

---

## 🏗️ Setup

### Accounts Needed

| Role | Description |
|---|---|
| **Owner** | Deploys, configures URL/price, withdraws |
| **User** | Buys credits, executes queries |

### 1. Get the contract file

```bash
python -c "
import genlayer_x402, os, shutil
src = os.path.dirname(genlayer_x402.__file__)
shutil.copy(f'{src}/x402_metered.py', 'contracts/x402_metered.py')
print('Copied x402_metered.py')
"
```

### 2. Lint before deploying

```bash
genvm-lint check contracts/x402_metered.py
```

### 3. Deploy Parameters

**[Switch to Owner account]**

Load `contracts/x402_metered.py`, deploy with:

| Field | Value | Meaning |
|---|---|---|
| `price_per_call_wei` | `1000000000000000000` | 1 GEN per call |
| `data_url_prefix` | `https://api.coingecko.com/api/v3/simple/price?ids=` | CoinGecko crypto price API |
| `max_credits` | `1000` | Max credits per user (anti-abuse) |

Click **Deploy** → copy contract address.

> 💡 **Why CoinGecko?** Free, no auth, no strict rate limits, small response size, and realistic use case for pay-per-query API billing.

---

## 🧪 Test Sequence

### Part 1: Verify Initial State (8 view methods)

**[Any account]**

| # | Method | Input | Expected |
|---|---|---|---|
| 1 | `get_price_per_call()` | - | `"1000000000000000000"` |
| 2 | `get_max_credits()` | - | `"1000"` |
| 3 | `get_total_calls()` | - | `"0"` |
| 4 | `get_total_revenue()` | - | `"0"` |
| 5 | `get_contract_balance()` | - | `"0"` |
| 6 | `check_credits(user_address)` | User's address | `"0"` |
| 7 | `get_call_count(user_address)` | User's address | `"0"` |
| 8 | `get_402_info()` | - | JSON metadata |

**Expected `get_402_info()`:**
```json
{"price_per_call_wei": 1000000000000000000, "max_credits": 1000, "owner": "0x...", "protocol": "x402-genlayer", "type": "metered"}
```

---

### Part 2: User Buys Credits

**[Switch to User account]**

#### Step 9: `buy_credits()` — payable

- **Method:** `buy_credits`
- **Value (GEN):** `5` (buys 5 credits at 1 GEN each)
- **Expected:** ✅ Transaction success

#### Step 10-12: Verify Credits Added

| # | Method | Input | Expected |
|---|---|---|---|
| 10 | `check_credits(user_address)` | User | `"5"` ✅ |
| 11 | `get_total_revenue()` | - | `"5000000000000000000"` |
| 12 | `get_contract_balance()` | - | `"5000000000000000000"` |

---

### Part 3: Execute Queries (Core AI Feature)

**[Still on User account]**

#### Step 13: `execute_query(query_param)` — First Query

- **Method:** `execute_query`
- **Input:** `query_param`: `bitcoin&vs_currencies=usd`
- **Expected:**
  - Wait **30-90 seconds** (URL fetch + LLM summarize + consensus)
  - Returns: AI-generated summary of Bitcoin price

**Example output:**
```
"Bitcoin is currently trading at approximately $65,432.50 USD, based on 
CoinGecko's aggregated exchange data."
```

> 💡 Open **Node Logs** panel to watch validators fetch the URL, call LLM, and compare summaries for consensus.

#### Step 14-16: Verify Credit Deducted

| # | Method | Input | Expected |
|---|---|---|---|
| 14 | `check_credits(user_address)` | User | `"4"` ✅ (was 5, now 4) |
| 15 | `get_call_count(user_address)` | User | `"1"` |
| 16 | `get_total_calls()` | - | `"1"` |

#### Step 17: More Queries

Repeat `execute_query` with different params:

- `ethereum&vs_currencies=usd` → ETH price
- `solana&vs_currencies=usd,idr` → SOL in USD & IDR
- `bitcoin,ethereum,solana&vs_currencies=usd` → 3 coins at once

Each query deducts 1 credit and increments counters.

---

### Part 4: Owner Methods

#### Step 18: `grant_credits(user_address, amount)` — Free Promo

**[Switch to Owner account]**

- **Method:** `grant_credits`
- **Input:** `user_address`: User's address, `amount`: `10`
- **Expected:** ✅ Success

Verify: `check_credits(user_address)` → `"11"` (1 remaining + 10 granted)

#### Step 19: `update_price(new_price)`

- **Method:** `update_price`
- **Input:** `new_price`: `2000000000000000000` (2 GEN per call)
- **Expected:** ✅ Success

Verify: `get_price_per_call()` → `"2000000000000000000"`

#### Step 20: `update_url_prefix(new_url)`

- **Method:** `update_url_prefix`
- **Input:** `new_url`: `https://jsonplaceholder.typicode.com/posts/`
- **Expected:** ✅ Success

#### Step 21: Test with New URL

**[User account]**

- **Method:** `execute_query`
- **Input:** `query_param`: `1`
- **Expected:** AI summary of post #1 from JSONPlaceholder

---

### Part 5: Error Handling

#### Step 22: Buy Credits Below Minimum

**[User account]**

- **Method:** `buy_credits`
- **Value (GEN):** `0`
- **Expected:** ❌ ERROR: `"x402: Minimum is ... wei (1 credit)"`

#### Step 23: Exceed Max Credits

- **Method:** `buy_credits`
- **Value (GEN):** `1001` (would exceed max of 1000)
- **Expected:** ❌ ERROR: `"x402: Would exceed max credits (1000)"`

#### Step 24: Execute Query with 0 Credits

Exhaust credits first, then:

- **Method:** `execute_query`
- **Input:** `query_param`: `anyone`
- **Expected:** ❌ ERROR: `"x402: No credits. Buy via buy_credits()..."`

#### Step 25: Non-owner Tries grant_credits

**[User account]**

- **Method:** `grant_credits`
- **Expected:** ❌ ERROR: `"x402: Only owner"`

#### Step 26: Non-owner Tries update_price

- **Method:** `update_price`
- **Expected:** ❌ ERROR: `"x402: Only owner"`

---

### Part 6: Revenue Withdrawal

**[Owner account]**

#### Step 27: Partial Withdraw

- **Method:** `withdraw`
- **Input:** `amount`: `1000000000000000000` (1 GEN)
- **Expected:** ✅ Success

#### Step 28: Full Withdraw

- **Method:** `withdraw_all`
- **Expected:** ✅ Success

#### Step 29: Verify Empty

- `get_contract_balance()` → `"0"` ✅

---

## 🎯 Quick Demo (8 Minutes)

```
[Owner]
1. Deploy: price=1 GEN, URL prefix=https://api.coingecko.com/api/v3/simple/price?ids=

[User]
2. check_credits(user) → 0
3. buy_credits()  Value: 5 → +5 credits ✅
4. check_credits(user) → 5
5. execute_query("bitcoin&vs_currencies=usd") → wait 60s → AI summary ✅
6. check_credits(user) → 4
7. execute_query("ethereum&vs_currencies=usd,idr") → ETH in USD & IDR
8. get_total_calls() → 2

[Owner]
9. withdraw_all() → 5 GEN to owner wallet
```

**Key talking points:**
- Step 5: "Fetches CoinGecko on-chain, LLM summarizes, validators reach consensus. All trustless."
- Step 6: "Each query automatically deducts 1 credit — transparent billing"
- Step 9: "Owner withdraws revenue anytime. No middleman holding funds."

---

## 🌟 Try Other APIs

| API | URL Prefix | Example Query |
|---|---|---|
| **CoinGecko (default)** | `https://api.coingecko.com/api/v3/simple/price?ids=` | `bitcoin&vs_currencies=usd` |
| **JSONPlaceholder** | `https://jsonplaceholder.typicode.com/posts/` | `1` |
| Dog API | `https://dog.ceo/api/breed/` | `hound/images/random` |
| GitHub Users | `https://api.github.com/users/` | `octocat` |

> 💡 APIs that don't require auth work best. Small JSON responses (<2KB) give better AI summaries.

---

## 📊 Full Test Summary

| Test | Status |
|---|---|
| Deploy succeeds | ✅ |
| Initial state correct (8 view methods) | ✅ |
| User can buy credits | ✅ |
| Credits reflect correctly | ✅ |
| AI-powered query returns summary | ✅ |
| Credits deduct per query | ✅ |
| Call count increments | ✅ |
| Owner can grant free credits | ✅ |
| Owner can update price | ✅ |
| Owner can update URL prefix | ✅ |
| New URL works correctly | ✅ |
| Underpay rejected | ✅ |
| Max credits cap enforced | ✅ |
| No credits → query rejected | ✅ |
| Non-owner admin calls rejected | ✅ |
| Withdraw works | ✅ |

---

## 🔗 Back

← [Testing Overview](./TESTING.md)
← [Main README](../README.md)