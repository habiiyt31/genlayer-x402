# Testing X402Subscription

Step-by-step testing guide for the X402Subscription contract — periodic quota-based subscription access.

---

## 📋 About This Contract

**Use case:** Users pay for N uses per period. Each use deducts 1 call from quota. Periods stack — buying 3 periods gives 3× calls.

**Key features tested:**
- Quota-based subscription (stackable)
- Subscriber count tracking
- Owner grant_access for free promotion
- Revenue withdrawal

**Total methods:** 16 (9 view + 7 write)

---

## 🏗️ Setup

### Accounts Needed

| Role | Description |
|---|---|
| **Owner** | Deploys, configures, grants free access |
| **Subscriber** | Buys subscriptions and consumes quota |

### Deploy Parameters

**[Switch to Owner account]**

Load `x402_subscription.py`, deploy with:

| Field | Value | Meaning |
|---|---|---|
| `price_per_period_wei` | `1000000000000000000` | 1 GEN per period |
| `calls_per_period` | `5` | 5 calls per period |
| `data_url` | `https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate` | Subscriber data URL |

Click **Deploy** → copy contract address.

---

## 🧪 Test Sequence

### Part 1: Verify Initial State (9 view methods)

**[Any account]**

| # | Method | Input | Expected |
|---|---|---|---|
| 1 | `get_price()` | - | `"1000000000000000000"` |
| 2 | `get_calls_per_period()` | - | `"5"` |
| 3 | `get_total_periods_sold()` | - | `"0"` |
| 4 | `get_subscriber_count()` | - | `"0"` |
| 5 | `get_total_revenue()` | - | `"0"` |
| 6 | `get_contract_balance()` | - | `"0"` |
| 7 | `is_active(user_address)` | Subscriber's address | `false` |
| 8 | `get_remaining_calls(user_address)` | Subscriber | `"0"` |
| 9 | `get_402_info()` | - | JSON metadata |

---

### Part 2: Subscribe for First Time

**[Switch to Subscriber account]**

#### Step 10: `subscribe(periods)` — Buy 1 period

- **Method:** `subscribe`
- **Input:** `periods`: `1`
- **Value (GEN):** `1` (1 period × 1 GEN)
- **Expected:** ✅ Transaction success

#### Step 11-16: Verify Subscription

| # | Method | Input | Expected |
|---|---|---|---|
| 11 | `is_active(user_address)` | Subscriber | `true` ✅ |
| 12 | `get_remaining_calls(user_address)` | Subscriber | `"5"` (1 period × 5 calls) |
| 13 | `get_subscriber_count()` | - | `"1"` (new subscriber) |
| 14 | `get_total_periods_sold()` | - | `"1"` |
| 15 | `get_total_revenue()` | - | `"1000000000000000000"` |
| 16 | `get_contract_balance()` | - | `"1000000000000000000"` |

---

### Part 3: Use Subscription (Consume Calls)

**[Subscriber account]**

#### Step 17: `get_data()` — First call

- **Method:** `get_data`
- **Input:** (none)
- **Expected:** 
  - Wait 30-60 seconds (URL fetch + consensus)
  - Returns: JSON data from GitHub repo

**Example output (truncated):**
```json
{"id":12345,"name":"genlayer-project-boilerplate","full_name":"genlayerlabs/...","description":"..."}
```

#### Step 18: Verify Quota Decreased

- `get_remaining_calls(user_address)` → `"4"` ✅ (was 5, now 4)

#### Step 19: Call get_data 2 more times

- Call 2: quota → `"3"`
- Call 3: quota → `"2"`

---

### Part 4: Test Stacking (Top Up)

Subscriptions STACK — buying more periods adds to existing quota.

#### Step 20: `subscribe(2)` — Buy 2 more periods

**[Subscriber account]**

- **Method:** `subscribe`
- **Input:** `periods`: `2`
- **Value (GEN):** `2` (2 periods × 1 GEN)
- **Expected:** ✅ Success

#### Step 21: Verify Stacking

| # | Method | Input | Expected |
|---|---|---|---|
| 21a | `get_remaining_calls(user_address)` | Subscriber | `"12"` (2 remaining + 10 new) |
| 21b | `get_subscriber_count()` | - | `"1"` (NOT incremented — same user) |
| 21c | `get_total_periods_sold()` | - | `"3"` (1 + 2) |
| 21d | `get_total_revenue()` | - | `"3000000000000000000"` (3 GEN) |

**Key insight:** Subscriber count stays at 1 because same user. But total periods sold increases.

---

### Part 5: Owner Methods

#### Step 22: `grant_access(user_address, periods)` — Free Subscription

**[Switch to Owner account]**

- **Method:** `grant_access`
- **Input:**
  - `user_address`: Subscriber's address
  - `periods`: `1` (gives 5 free calls)
- **Expected:** ✅ Success

#### Step 23: Verify Grant

- `get_remaining_calls(user_address)` → `"17"` (12 + 5 granted)

#### Step 24: `update_price(new_price)`

- **Method:** `update_price`
- **Input:** `new_price`: `2000000000000000000` (2 GEN)
- **Expected:** ✅ Success

Verify: `get_price()` → `"2000000000000000000"`.

#### Step 25: `update_calls_per_period(new_count)`

- **Method:** `update_calls_per_period`
- **Input:** `new_count`: `10` (was 5, now 10 calls per period)
- **Expected:** ✅ Success

Verify: `get_calls_per_period()` → `"10"`.

---

### Part 6: Grant Free to NEW User (Test Counter)

#### Step 26: Grant to a fresh account

**[Owner account]**

- **Method:** `grant_access`
- **Input:**
  - `user_address`: **a different account** (new one without subscription)
  - `periods`: `1` (5 calls with old setting, or 10 with new — let me check)

Actually, after step 25, `calls_per_period = 10`. So:
- `periods: 1` × `calls_per_period: 10` = 10 free calls

- **Expected:** ✅ Success

#### Step 27: Verify Subscriber Count Increments

- `get_subscriber_count()` → `"2"` ✅ (new user = new subscriber)

---

### Part 7: Error Handling

#### Step 28: Subscribe with 0 periods

**[Subscriber account]**

- **Method:** `subscribe`
- **Input:** `periods`: `0`
- **Value (GEN):** `1`
- **Expected:** ❌ ERROR: `"Must buy at least 1 period"`

#### Step 29: Subscribe with Insufficient Value

After price update to 2 GEN, try to subscribe with only 1 GEN:

- **Method:** `subscribe`
- **Input:** `periods`: `1`
- **Value (GEN):** `1` (but needs 2 GEN now)
- **Expected:** ❌ ERROR: `"x402: Insufficient. Required ... wei"`

#### Step 30: get_data without subscription

**[Fresh account with no subscription]**

- **Method:** `get_data`
- **Expected:** ❌ ERROR: `"x402: No active subscription..."`

#### Step 31: Non-owner grant_access

**[Subscriber account]**

- **Method:** `grant_access`
- **Expected:** ❌ ERROR: `"x402: Only owner"`

#### Step 32: Non-owner update_price

- **Method:** `update_price`
- **Expected:** ❌ ERROR: `"x402: Only owner"`

---

### Part 8: Exhaust Subscription

#### Step 33: Use all remaining calls

**[Subscriber account]**

Call `get_data` repeatedly until `remaining_calls` = 0.

#### Step 34: Verify no access after exhaustion

- `is_active(user_address)` → `false` ✅

#### Step 35: Try get_data when quota = 0

- **Method:** `get_data`
- **Expected:** ❌ ERROR: `"x402: No active subscription..."`

---

### Part 9: Revenue Withdrawal

**[Owner account]**

#### Step 36: Check balance

- `get_contract_balance()` → should show accumulated revenue

#### Step 37: Partial withdraw

- **Method:** `withdraw`
- **Input:** `amount`: `1000000000000000000` (1 GEN)
- **Expected:** ✅ Success

#### Step 38: Full withdraw

- **Method:** `withdraw_all`
- **Expected:** ✅ Success, remaining balance to owner

#### Step 39: Verify empty

- `get_contract_balance()` → `"0"` ✅

---

## 🎯 Quick Demo (7 Minutes)

Focus on **stacking** — the most unique feature:

```
[Owner]
1. Deploy: price=1 GEN, calls_per_period=5

[Subscriber]
2. is_active(user) → false
3. subscribe(1)  Value: 1 → ✅
4. is_active(user) → true ✅
5. get_remaining_calls(user) → 5
6. get_data() → JSON from GitHub
7. get_remaining_calls(user) → 4

[Stacking demo]
8. subscribe(2)  Value: 2 → ✅
9. get_remaining_calls(user) → 14 (4 + 10) ✅

[Owner]
10. grant_access(user, 1) → +5 free
11. get_remaining_calls(user) → 19
12. withdraw_all() → 3 GEN to owner
```

**Key talking points:**
- Step 6-7: "Each call deducts 1 from quota, transparent usage tracking"
- Step 9: "Subscriptions STACK — users can top up anytime without losing existing quota. Unlike Netflix which resets monthly!"
- Step 10: "Owner can grant free access for promos, testing, or compensation"

---

## 📊 Stacking Formula

Understanding the math:

```
new_remaining_calls = old_remaining_calls + (periods_bought × calls_per_period)
```

Example timeline:

| Action | Remaining Calls |
|---|---|
| Start | 0 |
| subscribe(1) | 0 + (1 × 5) = **5** |
| get_data() | 5 - 1 = **4** |
| get_data() | 4 - 1 = **3** |
| subscribe(2) | 3 + (2 × 5) = **13** |
| subscribe(1) | 13 + (1 × 5) = **18** |
| get_data() × 3 | 18 - 3 = **15** |

---

## 📊 Full Test Summary

| Test | Status |
|---|---|
| Deploy succeeds | ☐ |
| Initial state correct (9 view methods) | ☐ |
| Subscribe adds quota | ☐ |
| Subscriber count increments | ☐ |
| get_data fetches + decrements quota | ☐ |
| Stacking works (subscribe again) | ☐ |
| Subscriber count doesn't re-increment for same user | ☐ |
| Owner can grant access | ☐ |
| Owner can update price | ☐ |
| Owner can update calls_per_period | ☐ |
| New user via grant increments subscriber count | ☐ |
| Subscribe 0 periods rejected | ☐ |
| Insufficient value rejected | ☐ |
| get_data without subscription rejected | ☐ |
| Non-owner admin calls rejected | ☐ |
| Exhausted quota → inactive | ☐ |
| Withdraw works | ☐ |

---

## 💡 Use Case Ideas

Real-world scenarios this contract fits:

| Scenario | Setup |
|---|---|
| Monthly data feed | 10 calls/period, 1 GEN/period |
| Premium research access | 50 calls/period, 5 GEN/period |
| Weather API tier | 100 calls/period, 2 GEN/period |
| AI inference credits | 20 calls/period, 3 GEN/period |

---

## 🔗 Back

← [Testing Overview](./TESTING.md)
← [Main README](../README.md)
