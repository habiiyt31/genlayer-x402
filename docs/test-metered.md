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

### Deploy Parameters

**[Switch to Owner account]**

Load `x402_metered.py`, deploy with:

| Field | Value | Meaning |
|---|---|---|
| `price_per_call_wei` | `1000000000000000000` | 1 GEN per call |
| `data_url_prefix` | `https://api.github.com/users/` | URL prefix (query param appended) |
| `max_credits` | `1000` | Max credits per user (anti-abuse) |

Click **Deploy** → copy contract address.

---

## 🧪 Test Sequence

### Part 1: Verify Initial State (8 view methods)

**[Any account]**

| # | Method | Input | Expected |
|---|---|---|---|
| 1 | `get_price_per_call()` | - | `"1000000000000000000"` (1 GEN) |
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
| 11 | `get_total_revenue()` | - | `"5000000000000000000"` (5 GEN) |
| 12 | `get_contract_balance()` | - | `"5000000000000000000"` |

---

### Part 3: Execute Queries (Core AI Feature)

**[Still on User account]**

#### Step 13: `execute_query(query_param)` — First Query

- **Method:** `execute_query`
- **Input:** `query_param`: `octocat`
- **Expected:**
  - Wait **30-90 seconds** (URL fetch + LLM summarize + consensus)
  - Returns: AI-generated summary of GitHub API response

**Example output:**
```
"The GitHub user 'octocat' (named 'The Octocat') has been a member since 
January 2011. The profile shows public contributions at @github and is 
based in San Francisco."
```

**Important:** Open **Node Logs** panel to watch:
- Validators fetch URL: `https://api.github.com/users/octocat`
- Each validator calls LLM with prompt
- Consensus comparison: do summaries convey same info?

#### Step 14-16: Verify Credit Deducted

| # | Method | Input | Expected |
|---|---|---|---|
| 14 | `check_credits(user_address)` | User | `"4"` ✅ (was 5, now 4) |
| 15 | `get_call_count(user_address)` | User | `"1"` |
| 16 | `get_total_calls()` | - | `"1"` |

#### Step 17: More Queries

Repeat `execute_query` with different params:

- `query_param`: `torvalds` → get Linus Torvalds data
- `query_param`: `gvanrossum` → get Guido van Rossum data
- `query_param`: `vitalik-buterin` → get Vitalik Buterin data

Each query:
- ✅ Returns AI summary
- Deducts 1 credit
- Increments `call_count` for user and `total_calls` globally

After 3 more queries, `check_credits(user)` → `"1"` (started at 5, used 4).

---

### Part 4: Owner Methods

#### Step 18: `grant_credits(user_address, amount)` — Free Promo

**[Switch to Owner account]**

- **Method:** `grant_credits`
- **Input:**
  - `user_address`: User's address
  - `amount`: `10`
- **Expected:** ✅ Success (owner gifts 10 free credits)

#### Step 19: Verify Grant

- `check_credits(user_address)` → `"11"` (1 remaining + 10 granted)

#### Step 20: `update_price(new_price)`

- **Method:** `update_price`
- **Input:** `new_price`: `2000000000000000000` (2 GEN per call)
- **Expected:** ✅ Success

Verify with `get_price_per_call()` → `"2000000000000000000"`.

#### Step 21: `update_url_prefix(new_url)`

Switch the API we query. Try CoinGecko instead:

- **Method:** `update_url_prefix`
- **Input:** `new_url`: `https://api.coingecko.com/api/v3/simple/price?ids=`
- **Expected:** ✅ Success

#### Step 22: Test with New URL

**[Switch to User account]**

- **Method:** `execute_query`
- **Input:** `query_param`: `bitcoin&vs_currencies=usd`
- **Expected:** Wait 30-60s → AI summary of Bitcoin price

**Example output:**
```
"Bitcoin is currently trading at approximately $65,432 USD, based on 
CoinGecko's aggregated exchange data."
```

---

### Part 5: Error Handling

#### Step 23: Buy Credits Below Minimum

**[User account]**

- **Method:** `buy_credits`
- **Value (GEN):** `0` (tries to buy 0)
- **Expected:** ❌ ERROR: `"x402: Minimum is ... wei (1 credit)"`

#### Step 24: Exceed Max Credits

First, check max_credits is 1000. Try to buy 1001 credits at once:

- **Method:** `buy_credits`
- **Value (GEN):** `1001` (would buy 1001 credits)
- Wait, since `max_credits` is 1000, this fails:
- **Expected:** ❌ ERROR: `"x402: Would exceed max credits (1000)"`

**Note:** This assumes current price = 1 GEN/call. Adjust based on current `price_per_call_wei` and existing credits.

#### Step 25: Execute Query with 0 Credits

Exhaust credits first by calling `execute_query` repeatedly until `check_credits` = 0.

Then:
- **Method:** `execute_query`
- **Input:** `query_param`: `anyone`
- **Expected:** ❌ ERROR: `"x402: No credits. Buy via buy_credits()..."`

#### Step 26: Non-owner Tries grant_credits

**[User account]**

- **Method:** `grant_credits`
- **Input:** any user + amount
- **Expected:** ❌ ERROR: `"x402: Only owner"`

#### Step 27: Non-owner Tries update_price

**[User account]**

- **Method:** `update_price`
- **Expected:** ❌ ERROR: `"x402: Only owner"`

---

### Part 6: Revenue Withdrawal

**[Owner account]**

#### Step 28: Check Contract Balance

- `get_contract_balance()` → (should show accumulated GEN from `buy_credits`)

#### Step 29: Partial Withdraw

- **Method:** `withdraw`
- **Input:** `amount`: `1000000000000000000` (1 GEN)
- **Expected:** ✅ Success, 1 GEN to owner wallet

#### Step 30: Full Withdraw

- **Method:** `withdraw_all`
- **Expected:** ✅ Success

#### Step 31: Verify Empty

- `get_contract_balance()` → `"0"`

---

## 🎯 Quick Demo (8 Minutes)

Focus on the AI-powered query for maximum impact:

```
[Owner]
1. Deploy with price=1 GEN, URL prefix=https://api.github.com/users/

[User]
2. check_credits(user) → 0
3. buy_credits()  Value: 5 → +5 credits ✅
4. check_credits(user) → 5

5. execute_query("octocat")  → wait 60s → AI summary ✅
6. check_credits(user) → 4

7. execute_query("torvalds") → AI summary of Linus Torvalds
8. get_total_calls() → 2

[Owner]
9. withdraw_all() → 5 GEN to owner wallet
```

**Key talking points:**
- Step 5: "Contract fetches GitHub API on-chain, LLM summarizes the response, multiple validators reach consensus. All trustless."
- Step 6: "Each query automatically deducts 1 credit — transparent billing"
- Step 9: "Owner can withdraw revenue anytime. No middleman holding funds."

---

## 🌟 Try Other APIs

After `update_url_prefix`, test with different public APIs:

| API | URL Prefix | Example Query |
|---|---|---|
| CoinGecko (crypto) | `https://api.coingecko.com/api/v3/simple/price?ids=` | `bitcoin&vs_currencies=usd` |
| GitHub Users | `https://api.github.com/users/` | `octocat` |
| GitHub Repos | `https://api.github.com/repos/` | `genlayerlabs/genlayer-project-boilerplate` |
| JSONPlaceholder | `https://jsonplaceholder.typicode.com/posts/` | `1` |

Tip: APIs that don't need auth work best. Avoid APIs with API keys.

---

## 📊 Full Test Summary

| Test | Status |
|---|---|
| Deploy succeeds | ☐ |
| Initial state correct (8 view methods) | ☐ |
| User can buy credits | ☐ |
| Credits reflect correctly | ☐ |
| AI-powered query returns summary | ☐ |
| Credits deduct per query | ☐ |
| Call count increments | ☐ |
| Owner can grant free credits | ☐ |
| Owner can update price | ☐ |
| Owner can update URL prefix | ☐ |
| New URL works correctly | ☐ |
| Underpay rejected | ☐ |
| Max credits cap enforced | ☐ |
| No credits → query rejected | ☐ |
| Non-owner admin calls rejected | ☐ |
| Withdraw works | ☐ |

---

## 💡 Pro Tips

### 1. AI Quality Depends on URL Content

If `execute_query` returns junk summaries, the URL might return:
- Too large content (gets truncated to 2000 chars)
- Non-text content (images, binary)
- Empty response

Try GitHub APIs — they return clean JSON and AI summarizes them well.

### 2. Monitor Consensus in Node Logs

The logs show:
- Leader validator's proposed summary
- Other validators' summaries
- Whether they semantically match (via `prompt_comparative`)
- Final consensus result

This is GenLayer's "Optimistic Democracy" in action.

### 3. Realistic Demo Scenarios

- **"Pay-per-query price API"** — Use CoinGecko URL, charge per price check
- **"Paid GitHub analytics"** — Use GitHub API, summarize user profiles
- **"News API with AI TL;DR"** — Use RSS feed URL, AI summarizes articles

---

## 🔗 Back

← [Testing Overview](./TESTING.md)
← [Main README](../README.md)
