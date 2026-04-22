# Testing X402Escrow

Step-by-step testing guide for the X402Escrow contract — AI-verified freelance payment escrow.

---

## 📋 About This Contract

**Use case:** Client funds escrow with GEN, freelancer submits work, GenLayer LLM validators evaluate if work meets brief. Payment auto-releases if approved, or goes to dispute resolution.

**Key features tested:**
- Structured brief validation (200+ chars, 4 fields)
- State machine: OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED
- AI-powered work evaluation via GenLayer validators
- Dispute resolution: client override, arbiter rule, force release

**Total methods:** 14 (8 view + 6 write)

> ⚠️ **You need 3 accounts:** Client, Freelancer, Arbiter. Set up 3 accounts in Studio before starting.

---

**[Switch to Client account]**

Load `contracts/x402_escrow.py`, deploy with:

| Field | Min | Example Value |
|---|---|---|
| `brief_title` | 10 chars | `Bitcoin Price Fetcher Python Script` |
| `brief_description` | 80 chars | `Build a Python script that fetches the current Bitcoin price from the CoinGecko API and prints it in formatted output with timestamp and 24h change percentage.` |
| `brief_acceptance_criteria` | 80 chars | `Script must run without errors on Python 3.10+. Must use requests library. Must print price in USD format. Must include error handling for API failures. Code must be PEP8 compliant.` |
| `brief_deliverable_format` | 30 chars | `Single Python file named btc_price.py committed to a public GitHub repo` |
| `arbiter_addr` | — | `0xARBITER_ADDRESS` |
| `max_claim_attempts` | min 3 | `3` |

> Total brief content must be **≥ 200 characters** combined.

Click **Deploy** → copy contract address.

---

## 🧪 Test Sequence

### Part 1: Verify Initial State (8 view methods)

**[Any account]**

| # | Method | Input | Expected |
|---|---|---|---|
| 1 | `get_state()` | - | `"OPEN"` |
| 2 | `get_amount()` | - | `"0"` |
| 3 | `get_client()` | - | Client's address |
| 4 | `get_freelancer()` | - | `"0x000...000"` (zero address) |
| 5 | `get_arbiter()` | - | Arbiter's address |
| 6 | `get_brief()` | - | JSON with all 4 brief fields |
| 7 | `get_claim_attempts()` | - | `"0"` |
| 8 | `get_max_claim_attempts()` | - | `"3"` |

---

### Part 2: Deploy Fails With Short Brief (Validation Test)

Try deploying with a brief that's too short:

- `brief_title`: `"short"` (less than 10 chars)
- **Expected:** ❌ ERROR: `"Brief title must be at least 10 characters"`

✅ Validation prevents trivial briefs.

---

### Part 3: Client Funds Escrow

**[Switch to Client account]**

#### Step 9: `fund(freelancer_address)` — payable

- **Method:** `fund`
- **Input:** `freelancer_address`: Freelancer's address
- **Value (GEN):** `5` (5 GEN escrow amount)
- **Expected:** ✅ Transaction success

#### Step 10-12: Verify Funded State

| # | Method | Input | Expected |
|---|---|---|---|
| 10 | `get_state()` | - | `"FUNDED"` ✅ |
| 11 | `get_amount()` | - | `"5000000000000000000"` |
| 12 | `get_freelancer()` | - | Freelancer's address |

---

### Part 4: Only Client Can Fund (Security Test)

**[Switch to non-client account]**

- **Method:** `fund`, **Input:** any address, **Value:** `100`
- **Expected:** ❌ ERROR: `"x402: Only client can fund"`

✅ Access control working.

---

### Part 5: Client Cancels While FUNDED

**[Client account]**

- **Method:** `client_cancel`
- **Expected:** ✅ Success, funds returned to client, state → `"RESOLVED"`

> If you want to continue testing, redeploy and fund again before continuing.

---

### Part 6: Freelancer Submits Work

Fund the escrow again (redeploy if needed), then:

**[Switch to Freelancer account]**

#### Step 13: `submit_work(work_url, work_description)`

- **Method:** `submit_work`
- **Input:**
  - `work_url`: `https://gist.github.com/example/btc_price.py`
  - `work_description`: `Completed Python script as specified in brief`
- **Expected:**
  - Wait **60-120 seconds** (fetch URL + LLM evaluate + consensus)
  - Returns: `"APPROVED <reason>"` or `"DISPUTED <reason>"`

#### Step 14: Check AI Verdict

| # | Method | Expected |
|---|---|---|
| 14a | `get_state()` | `"APPROVED"` or `"DISPUTED"` |
| 14b | `get_ai_verdict()` | Full verdict string from LLM |
| 14c | `get_work_url()` | URL you submitted |

---

### Part 7A: Happy Path — Release Payment (If APPROVED)

**[Any account]**

- **Method:** `release_payment`
- **Expected:** ✅ Funds transferred to freelancer, state → `"RESOLVED"`

Verify: `get_state()` → `"RESOLVED"` ✅

---

### Part 7B: Dispute — Client Manually Approves

If AI returns DISPUTED, client can override:

**[Switch to Client account]**

- **Method:** `client_approve`
- **Expected:** ✅ State → `"APPROVED"`

Then release payment:

- **Method:** `release_payment`
- **Expected:** ✅ Freelancer paid

---

### Part 7C: Dispute — Arbiter Resolves

**[Switch to Arbiter account]**

- **Method:** `arbiter_rule`
- **Input:** `approve`: `true` (release to freelancer) or `false` (refund to client)
- **Expected:** ✅ Funds transferred accordingly, state → `"RESOLVED"`

---

### Part 7D: Dispute — Force Release (Timeout Safety)

If both client and arbiter are unresponsive:

**[Switch to Freelancer account]**

```
# Log 3 claim attempts (max_claim_attempts = 3)
freelancer_claim_attempt()  × 3
```

Verify: `get_claim_attempts()` → `"3"`

Then force release:

- **Method:** `force_release`
- **Expected:** ✅ Funds → freelancer, state → `"RESOLVED"`

---

### Part 8: Error Handling

#### Force Release Too Early (Should Fail)

- **Method:** `force_release` (before reaching max_claim_attempts)
- **Expected:** ❌ ERROR: `"x402: Not enough claim attempts. Current: 0, required: 3"`

#### Non-Freelancer Cannot Submit Work

**[Random account]**

- **Method:** `submit_work`
- **Expected:** ❌ ERROR: `"x402: Only freelancer can submit"`

#### Cannot Fund Twice

**[Client, when already FUNDED]**

- **Method:** `fund`, **Value:** `100`
- **Expected:** ❌ ERROR: `"x402: Escrow not in OPEN state"`

#### Arbiter Cannot Rule Outside DISPUTED

**[Arbiter account]**

- **Method:** `arbiter_rule` (when state is APPROVED)
- **Expected:** ❌ ERROR: `"x402: Arbiter only rules in DISPUTED state"`

---

## 🎯 Quick Demo (10 Minutes)

Full escrow flow — happy path:

```
[Client]
1. Deploy with structured brief (200+ chars)

2. fund(freelancer_addr)  Value: 5 → state: FUNDED ✅

[Freelancer]
3. submit_work(url, desc) → wait 90s → AI evaluates

[If APPROVED]
4. release_payment() → 5 GEN to freelancer ✅

[If DISPUTED — show force release safety valve]
4a. freelancer_claim_attempt() × 3
4b. force_release() → 5 GEN to freelancer ✅
```

**Key talking points:**
- Step 2: "Funds locked on-chain — neither party can disappear with the money"
- Step 3: "GenLayer LLM validators evaluate the work against the brief. No human judge needed."
- Step 4: "Payment releases automatically if work is approved"
- Step 4b: "Even if client goes offline, freelancer can force release after 3 failed attempts"

---

## 📊 State Machine

```
OPEN
 │
 ├── fund(freelancer) ──────────────────→ FUNDED
 │                                           │
 │                              client_cancel() → RESOLVED
 │                                           │
 │                              submit_work() → SUBMITTED
 │                                           │
 │                                    AI evaluates
 │                                    ┌──────┴──────┐
 │                                APPROVED       DISPUTED
 │                                    │               │
 │                          release_payment()   ┌─────┼─────┐
 │                                    │    client   arbiter  force
 │                                    │    _approve  _rule   _release
 │                                    └────────────┴─────────┘
 │                                                │
 └──────────────────────────────────────────── RESOLVED
```

---

## 📊 Full Test Summary

| Test | Status |
|---|---|
| Deploy successful with valid brief | ✅ |
| Deploy rejected with short brief fields | ✅ |
| Initial state is OPEN | ✅ |
| Client funds escrow → state FUNDED | ✅ |
| Non-client blocked from funding | ✅ |
| Client cancel refunds and resolves | ✅ |
| Freelancer submits work → AI evaluates | ✅ |
| APPROVED → release_payment works | ✅ |
| DISPUTED → client_approve overrides AI | ✅ |
| DISPUTED → arbiter_rule resolves | ✅ |
| DISPUTED → force_release after max attempts | ✅ |
| Force release blocked before threshold | ✅ |
| Non-freelancer blocked from submitting | ✅ |
| Cannot fund twice | ✅ |

---

## 🔗 Back

← [Testing Overview](./TESTING.md)
← [Main README](../README.md)