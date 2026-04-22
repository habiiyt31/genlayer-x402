# Testing X402Paywall

Step-by-step testing guide for the X402Paywall contract — a one-time payment gate for web data.

---

## 📋 About This Contract

**Use case:** User pays once in GEN → permanent access to protected data fetched live from an external URL.

**Key features tested:**
- One-time payment unlocks permanent access via explicit flag
- Price updates do NOT revoke existing buyers
- Owner can withdraw accumulated revenue
- Real-time web data fetching with validator consensus

**Total methods:** 14 (8 view + 6 write)

---

## 🏗️ Setup

### Accounts Needed

| Role | Description |
|---|---|
| **Owner** | Deploys contract, can change price and withdraw |
| **User** | Pays for access and reads protected data |

### 1. Get the contract file

```bash
python -c "
import genlayer_x402, os, shutil
src = os.path.dirname(genlayer_x402.__file__)
shutil.copy(f'{src}/x402_paywall.py', 'contracts/x402_paywall.py')
print('Copied x402_paywall.py')
"
```

### 2. Lint before deploying

```bash
genvm-lint check contracts/x402_paywall.py
```

### 3. Deploy Parameters

**[Switch to Owner account]**

Load `contracts/x402_paywall.py`, click **Deploy**, fill constructor:

| Field | Value | Meaning |
|---|---|---|
| `price_wei` | `1000000000000000000` | 1 GEN (= 10¹⁸ wei) |
| `data_url` | `https://api.github.com/users/octocat` | URL to fetch for paid users |

Click **Deploy** → copy contract address.

---

## 🧪 Test Sequence

### Part 1: Verify Initial State (8 view methods)

**[Any account]**

| # | Method | Input | Expected |
|---|---|---|---|
| 1 | `get_price()` | - | `"1000000000000000000"` |
| 2 | `get_owner()` | - | Owner's address |
| 3 | `get_data_url()` | - | `"https://api.github.com/users/octocat"` |
| 4 | `get_total_revenue()` | - | `"0"` |
| 5 | `get_contract_balance()` | - | `"0"` |
| 6 | `has_access(user_address)` | User's address | `false` |
| 7 | `get_payment(user_address)` | User's address | `"0"` |
| 8 | `get_402_info()` | - | JSON metadata |

**Expected `get_402_info()` output:**
```json
{"price_wei": 1000000000000000000, "owner": "0x...", "protocol": "x402-genlayer", "type": "paywall"}
```

---

### Part 2: User Pays for Access

**[Switch to User account]**

#### Step 9: `pay_for_access()` — payable

- **Method:** `pay_for_access`
- **Value (GEN):** `1` (Studio auto-converts to 1e18 wei)
- **Expected:** ✅ Transaction success

#### Step 10-13: Verify Payment

| # | Method | Input | Expected |
|---|---|---|---|
| 10 | `has_access(user_address)` | User's address | `true` ✅ |
| 11 | `get_payment(user_address)` | User's address | `"1000000000000000000"` |
| 12 | `get_total_revenue()` | - | `"1000000000000000000"` |
| 13 | `get_contract_balance()` | - | `"1000000000000000000"` |

---

### Part 3: Fetch Protected Data (Core Feature)

**[Still on User account]**

#### Step 14: `get_protected_data()`

- **Method:** `get_protected_data`
- **Input:** (none)
- **Expected:**
  - Wait 30-60 seconds (validators fetch URL + consensus)
  - Returns: JSON data from GitHub API for user "octocat"

**Example output (truncated):**
```json
{"login":"octocat","id":583231,"node_id":"...","avatar_url":"...","name":"The Octocat",...}
```

> 💡 Open the **Node Logs** panel during this call. You'll see multiple validators fetching the same URL, comparing responses, and committing final result on-chain.

---

### Part 4: Test Access Persistence (Security Feature) 🔒

This proves the `access_granted` explicit flag — price updates never revoke existing buyers.

#### Step 15: Owner Updates Price

**[Switch to Owner account]**

- **Method:** `update_price`
- **Input:** `new_price`: `5000000000000000000` (5 GEN)
- **Expected:** ✅ Transaction success

#### Step 16: Verify Price Changed

- `get_price()` → `"5000000000000000000"` ✅

#### Step 17: Verify User's Access NOT Revoked

- **Method:** `has_access(user_address)`
- **Input:** User's address (who paid 1 GEN earlier)
- **Expected:** `true` ✅

**Why this matters:** Even though price jumped from 1 GEN to 5 GEN, the user who paid before still has access. This is the explicit `access_granted` flag — prevents retroactive access revocation.

#### Step 18: Verify User Can Still Fetch Data

- **Method:** `get_protected_data()`
- **Expected:** ✅ Returns data (user still has access)

---

### Part 5: Owner Methods

#### Step 19: `update_data_url(new_url)`

**[Owner account]**

- **Method:** `update_data_url`
- **Input:** `new_url`: `https://api.github.com/users/torvalds`
- **Expected:** ✅ Success

Verify: `get_data_url()` → should show new URL.

#### Step 20: `withdraw(amount)` — Partial Withdraw

- **Method:** `withdraw`
- **Input:** `amount`: `500000000000000000` (0.5 GEN)
- **Expected:** ✅ Success, 0.5 GEN transferred to owner wallet

#### Step 21: Verify Balance Decreased

- `get_contract_balance()` → `"500000000000000000"` (0.5 GEN remaining)

#### Step 22: `withdraw_all()` — Withdraw Rest

- **Method:** `withdraw_all`
- **Expected:** ✅ Success

#### Step 23: Verify Empty Contract

- `get_contract_balance()` → `"0"` ✅

---

### Part 6: Error Handling

#### Step 24: Non-owner Tries to Change Price

**[User account]**

- **Method:** `update_price`
- **Input:** `new_price`: `1`
- **Expected:** ❌ ERROR: `"x402: Only owner"`

#### Step 25: Non-owner Tries to Withdraw

**[User account]**

- **Method:** `withdraw_all`
- **Expected:** ❌ ERROR: `"x402: Only owner can withdraw"`

#### Step 26: Insufficient Payment

**[New account that hasn't paid]**

- **Method:** `pay_for_access`
- **Value (GEN):** `0`
- **Expected:** ❌ ERROR: `"x402: Insufficient payment..."`

#### Step 27: Fetch Data Without Paying

**[New account that hasn't paid]**

- **Method:** `get_protected_data`
- **Expected:** ❌ ERROR: `"x402: Payment required..."`

#### Step 28: Withdraw More Than Balance

**[Owner, when contract is empty]**

- **Method:** `withdraw`
- **Input:** `amount`: `1000000000000000000`
- **Expected:** ❌ ERROR: `"x402: Insufficient contract balance..."`

#### Step 29: Withdraw All When Balance Is Zero

**[Owner, after successful withdraw_all]**

- **Method:** `withdraw_all`
- **Expected:** ❌ ERROR: `"x402: Contract balance is zero"`

---

## 🎯 Quick Demo (5 Minutes)

```
[Owner]
1. Deploy with price_wei=1000000000000000000 (1 GEN)

[User]
2. has_access(user) → false
3. pay_for_access()  Value: 1 → ✅
4. has_access(user) → true ✅
5. get_protected_data() → JSON from GitHub API

[Owner]
6. update_price(5000000000000000000) → ✅
7. has_access(user) → still true ✅ (no revoke!)
8. withdraw_all() → 1 GEN transferred to owner
```

**Key talking points:**
- Step 4: "User paid once, now has permanent access stored on-chain"
- Step 5: "Contract fetches GitHub data LIVE via GenLayer validators — no middleware"
- Step 7: "Even when price goes up, existing buyers are NOT revoked"
- Step 8: "Owner can withdraw earnings anytime, no funds stuck"

---

## 📊 Full Test Summary

| Test | Status |
|---|---|
| Deploy succeeds | ✅ |
| Initial state correct (8 view methods) | ✅ |
| User can pay and get access | ✅ |
| User can fetch protected data | ✅ |
| Price update does NOT revoke access | ✅ |
| Owner can update URL | ✅ |
| Partial withdraw works | ✅ |
| Full withdraw works | ✅ |
| Non-owner cannot update price | ✅ |
| Non-owner cannot withdraw | ✅ |
| Insufficient payment rejected | ✅ |
| Access required for data | ✅ |
| Over-withdraw rejected | ✅ |

---

## 🔗 Back

← [Testing Overview](./TESTING.md)
← [Main README](../README.md)