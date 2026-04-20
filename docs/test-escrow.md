# Testing X402Escrow

Step-by-step testing guide for the X402Escrow contract — AI-verified freelance payment escrow with arbiter and timeout safety mechanisms.

---

## 📋 About This Contract

**Use case:** Client funds escrow with structured brief. Freelancer submits work URL. GenLayer LLM validators evaluate if work meets the brief. If approved, payment releases; if disputed, 3 fallback mechanisms prevent fund lockup.

**Key features tested:**
- Structured 4-field brief (200+ chars) prevents trivial tasks
- AI-powered verdict via GenLayer LLM consensus
- Client override for manual approval
- Arbiter role for third-party dispute resolution
- **Force release safety valve** — prevents permanent lockup

**Total methods:** 19 (11 view + 8 write)

**State machine:**
```
OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED
```

---

## 🏗️ Setup

### Accounts Needed (3 accounts!)

| Role | Description |
|---|---|
| **Client** | Deploys, funds, owns the escrow |
| **Freelancer** | Assigned by client, submits work |
| **Arbiter** | Neutral 3rd party for dispute resolution |

Create all 3 accounts in Studio dropdown. Fund each with 💧 faucet.

**Record all 3 addresses** before starting:

```
CLIENT:     0x______________________________________________
FREELANCER: 0x______________________________________________
ARBITER:    0x______________________________________________
```

### Deploy Parameters

**[Switch to Client account]**

Load `x402_escrow.py`, deploy with **6 arguments**:

#### 1. `brief_title` (min 10 chars)
```
Python HTTP Library Documentation Review
```

#### 2. `brief_description` (min 80 chars)
```
Review and document a Python HTTP library README covering installation instructions, basic usage examples, feature list, supported Python versions, and contribution guidelines for developers integrating the library into their projects.
```

#### 3. `brief_acceptance_criteria` (min 80 chars)
```
README must include installation instructions using pip. Must include basic usage examples with code snippets. Must list main library features. Must mention supported Python versions. Must include contribution or license information.
```

#### 4. `brief_deliverable_format` (min 30 chars)
```
Markdown README file accessible via HTTPS URL on GitHub raw content
```

#### 5. `arbiter_addr`
```
[paste Arbiter's address here]
```

#### 6. `max_claim_attempts`
```
3
```

Click **Deploy** → copy contract address.

---

## 🧪 Test Sequence — Happy Path APPROVED

### Part 1: Verify Initial State (11 view methods)

**[Any account]**

| # | Method | Input | Expected |
|---|---|---|---|
| 1 | `get_state()` | - | `"OPEN"` |
| 2 | `get_client()` | - | Client's address |
| 3 | `get_freelancer()` | - | `"0x0000000000000000000000000000000000000000"` |
| 4 | `get_arbiter()` | - | Arbiter's address |
| 5 | `get_amount()` | - | `"0"` |
| 6 | `get_work_url()` | - | `""` |
| 7 | `get_ai_verdict()` | - | `""` |
| 8 | `get_claim_attempts()` | - | `"0"` |
| 9 | `get_max_claim_attempts()` | - | `"3"` |
| 10 | `get_brief()` | - | JSON with 4 brief fields |
| 11 | `get_summary()` | - | JSON with full state |

---

### Part 2: Client Funds Escrow

**[Client account]**

#### Step 12: `fund(freelancer_address)`

- **Method:** `fund`
- **Input:** `freelancer_address`: Freelancer's address
- **Value (GEN):** `5`
- **Expected:** ✅ Success

#### Step 13: Verify Fund

| Method | Expected |
|---|---|
| `get_state()` | `"FUNDED"` ✅ |
| `get_freelancer()` | Freelancer's address ✅ |
| `get_amount()` | `"5000000000000000000"` (5 GEN) |

---

### Part 3: Freelancer Submits Work

**[SWITCH to Freelancer account]**

⚠️ **Important:** Make sure you're logged into the exact address you specified in `fund()`.

#### Step 14: `submit_work(work_url, work_description)`

- **Method:** `submit_work`
- **Input:**
  - `work_url`:
    ```
    https://raw.githubusercontent.com/requests/requests/main/README.md
    ```
  - `work_description`:
    ```
    Comprehensive Python HTTP library README with installation via pip, multiple usage examples, full feature list, supported versions, and contribution guidelines. All acceptance criteria met.
    ```
- **Expected:**
  - Wait **60-120 seconds** (URL fetch + LLM evaluation + consensus)
  - Returns: verdict string starting with `"APPROVED"` or `"DISPUTED"`

**Important:** Open **Node Logs** panel during this call. You'll see:
- Validators fetching GitHub README
- Each validator runs LLM with full brief + content
- Consensus: do all verdicts agree (APPROVED or DISPUTED)?

#### Step 15: Verify State Change

| Method | Expected |
|---|---|
| `get_state()` | `"APPROVED"` or `"DISPUTED"` |
| `get_work_url()` | URL you submitted |
| `get_ai_verdict()` | Full AI reasoning text |

---

### Part 4: Branching Based on Verdict

#### ✅ IF AI Returned APPROVED:

**[Any account]**

##### Step 16a: `release_payment()`

- **Method:** `release_payment`
- **Expected:** ✅ Success, 5 GEN transferred to Freelancer

##### Step 17a: Verify Resolution

| Method | Expected |
|---|---|
| `get_state()` | `"RESOLVED"` ✅ |
| Contract balance | `"0"` |
| Freelancer wallet | +5 GEN 🎉 |

**Done!** Happy path complete.

---

#### ❌ IF AI Returned DISPUTED:

You have **3 fallback options** to try. Each demonstrates a different safety mechanism.

---

## 🔄 Option 1: Client Override (Fastest)

**[Switch to Client account]**

### Step 16b: `client_approve()`

- **Method:** `client_approve`
- **Expected:** ✅ Success, state → APPROVED

### Step 17b: Verify Override

- `get_state()` → `"APPROVED"` ✅
- `get_ai_verdict()` → original verdict + `" [MANUALLY APPROVED BY CLIENT]"`

### Step 18b: Release Payment

**[Any account]**

- `release_payment()` → ✅ 5 GEN to Freelancer

**Narrative:** "AI was strict, but Client reviewed manually and approved. Override works."

---

## 🔄 Option 2: Arbiter Rules (Third-Party Resolution)

**[Switch to Arbiter account]**

### Step 16c: `arbiter_rule(approve)`

Decide outcome:
- `approve: true` → pay Freelancer
- `approve: false` → refund Client

- **Method:** `arbiter_rule`
- **Input:** `approve`: `true` (or `false`)
- **Expected:** ✅ Success, state → RESOLVED, auto-transfer

### Step 17c: Verify Arbiter Resolution

- `get_state()` → `"RESOLVED"` ✅
- `get_ai_verdict()` → original + `" [ARBITER RULED]"`
- If approve=true: Freelancer +5 GEN
- If approve=false: Client +5 GEN (refund)

**Narrative:** "Arbiter acts as impartial third party. Their decision is final. Dispute resolved without central authority."

---

## 🔄 Option 3: Force Release (Timeout Safety) ⭐ RECOMMENDED

This is the **most impressive demo** because it shows the anti-lockup mechanism addressing steward's specific feedback.

**[Switch to Freelancer account]**

### Step 16d: Try force_release prematurely (should fail)

- **Method:** `force_release`
- **Expected:** ❌ ERROR: `"Not enough claim attempts. Current: 0, required: 3"`

This proves you can't spam the safety valve.

### Step 17d: `freelancer_claim_attempt()` — Attempt 1

- **Method:** `freelancer_claim_attempt`
- **Expected:** ✅ Success
- `get_claim_attempts()` → `"1"`

### Step 18d: Claim Attempt 2

- `freelancer_claim_attempt()` → `get_claim_attempts()` → `"2"`

### Step 19d: Claim Attempt 3

- `freelancer_claim_attempt()` → `get_claim_attempts()` → `"3"`

### Step 20d: `force_release()` — Now allowed

- **Method:** `force_release`
- **Expected:** ✅ Success!
- Freelancer receives 5 GEN
- `get_state()` → `"RESOLVED"`
- `get_ai_verdict()` → original + `" [FORCE-RELEASED AFTER TIMEOUT]"`

**Narrative:** "AI was DISPUTED, Client went offline, Arbiter unresponsive. Freelancer logs 3 claim attempts. Then auto-unlocks the funds. **Funds can never be stuck permanently.** This prevents the #1 escrow failure mode."

---

## 🧪 Part 5: Alternative Scenario — Client Cancel

Test cancellation BEFORE freelancer submits.

Deploy a new contract, then:

### Step 21: Client funds

**[Client]**
- `fund(freelancer)` Value: 5 → state FUNDED

### Step 22: Client cancels (before work submitted)

- **Method:** `client_cancel`
- **Expected:** ✅ Success
- Client gets 5 GEN refunded
- `get_state()` → `"RESOLVED"`

### Step 23: Verify refund

- Client wallet: +5 GEN (originally deducted when fund()'d)
- `get_state()` → `"RESOLVED"`

---

## 🧪 Part 6: Error Handling

### Step 24: Short brief rejected at deploy

Try deploying with too-short brief fields:

- `brief_title`: `"Too short"` (only 9 chars, min 10)
- **Expected:** ❌ ERROR: `"Brief title must be at least 10 characters"`

Try different combinations:
- Too-short description → error
- Total < 200 chars → error
- `max_claim_attempts: 2` → error `"Max claim attempts must be at least 3"`

### Step 25: Fund twice

After state is FUNDED (or further):

**[Client]**
- `fund(anyone)` Value: 1
- **Expected:** ❌ ERROR: `"Escrow not in OPEN state"`

### Step 26: Non-client fund

**[Freelancer account]**
- `fund(anyone)` Value: 1
- **Expected:** ❌ ERROR: `"Only client can fund"`

### Step 27: Non-freelancer submit

**[Client account] on a FUNDED contract**
- `submit_work(url, desc)`
- **Expected:** ❌ ERROR: `"Only freelancer can submit"`

### Step 28: Submit before funding

Deploy new contract, immediately try to submit:

**[Freelancer]**
- `submit_work(url, desc)`
- **Expected:** ❌ ERROR: `"Escrow must be in FUNDED state"`

### Step 29: Release when not APPROVED

On FUNDED or SUBMITTED state:
- `release_payment()`
- **Expected:** ❌ ERROR: `"Work not approved..."`

### Step 30: Cancel after submit

After `submit_work`:

**[Client]**
- `client_cancel()`
- **Expected:** ❌ ERROR: `"Can only cancel from FUNDED state..."`

### Step 31: Arbiter rules when not disputed

On APPROVED or RESOLVED state:

**[Arbiter]**
- `arbiter_rule(true)`
- **Expected:** ❌ ERROR: `"Arbiter only rules in DISPUTED state..."`

### Step 32: Non-arbiter arbitrates

**[Client or Freelancer]**
- `arbiter_rule(true)`
- **Expected:** ❌ ERROR: `"Only arbiter can rule on disputes"`

### Step 33: Claim attempt in non-DISPUTED state

On any state except DISPUTED:

**[Freelancer]**
- `freelancer_claim_attempt()`
- **Expected:** ❌ ERROR: `"Claim attempts only in DISPUTED state"`

---

## 🎯 Quick Demo (10 Minutes) — Force Release Flow

The most impressive demo, showing anti-lockup mechanism:

```
[Client]
1. Deploy with 6-arg structured brief
2. get_state() → "OPEN"
3. fund(alamat Freelancer)  Value: 5 → ✅

[Freelancer]
4. submit_work(URL unmatching brief, description)
   → wait 60s → AI verdict: DISPUTED (expected)
5. get_ai_verdict() → full reasoning

[Show failed premature release]
6. force_release() → ❌ "Not enough claim attempts"

[Log claim attempts]
7. freelancer_claim_attempt() × 3
8. get_claim_attempts() → "3"

[Force unlock]
9. force_release() → ✅ SUCCESS!
10. get_state() → "RESOLVED"
11. Freelancer wallet → +5 GEN 🎉
```

**Key talking points:**

- **Step 3:** "5 GEN locked in escrow, freelancer assigned on-chain"
- **Step 4-5:** "AI validators are strict, reject work that doesn't match brief"
- **Step 6:** "Safety valve can't be spammed — must log attempts first"
- **Step 9:** "After 3 attempts, freelancer can auto-unlock. This prevents the #1 risk in escrow — funds stuck forever when client ghosts."

---

## 🎯 Alternative Demo (5 Minutes) — Happy Path APPROVED

For happy path, use brief matching popular README content:

```
[Client]
1. Deploy with brief about "Python HTTP library documentation"
2. fund(freelancer)  Value: 5

[Freelancer]
3. submit_work(URL: requests README, description matching)
   → wait 60s → AI: APPROVED ✅
4. get_state() → "APPROVED"

[Any account]
5. release_payment() → ✅ 5 GEN to Freelancer
6. get_state() → "RESOLVED"
```

**If AI says DISPUTED** (it's strict), fallback to `client_approve()` or `force_release()`.

---

## 📊 State Transition Tests

Verify all state transitions work correctly:

| From State | Action | Expected Result |
|---|---|---|
| OPEN | `fund()` | → FUNDED ✅ |
| FUNDED | `submit_work()` | → SUBMITTED → APPROVED/DISPUTED |
| FUNDED | `client_cancel()` | → RESOLVED (refund) |
| APPROVED | `release_payment()` | → RESOLVED (freelancer paid) |
| APPROVED | `client_approve()` | ✅ no-op (already approved) |
| DISPUTED | `client_approve()` | → APPROVED |
| DISPUTED | `arbiter_rule(true)` | → RESOLVED (freelancer paid) |
| DISPUTED | `arbiter_rule(false)` | → RESOLVED (client refund) |
| DISPUTED | `freelancer_claim_attempt() × 3 + force_release()` | → RESOLVED (freelancer paid) |
| RESOLVED | any action | ❌ all fail |

---

## 📊 Full Test Summary

| Test | Status |
|---|---|
| Deploy with structured brief (200+ chars) | ☐ |
| Deploy rejects short briefs | ☐ |
| Deploy rejects max_claim_attempts < 3 | ☐ |
| Initial state view methods (11) | ☐ |
| Client funds escrow | ☐ |
| Freelancer submits work | ☐ |
| AI evaluates and sets state | ☐ |
| **Happy path:** release_payment (if APPROVED) | ☐ |
| **Alt 1:** client_approve works in DISPUTED | ☐ |
| **Alt 2:** arbiter_rule(true) → freelancer paid | ☐ |
| **Alt 2:** arbiter_rule(false) → client refund | ☐ |
| **Alt 3:** force_release after 3 attempts | ☐ |
| force_release prematurely rejected | ☐ |
| client_cancel works in FUNDED state | ☐ |
| client_cancel rejected in SUBMITTED | ☐ |
| Non-client fund rejected | ☐ |
| Non-freelancer submit rejected | ☐ |
| Non-arbiter arbitrate rejected | ☐ |
| release_payment before APPROVED rejected | ☐ |
| claim_attempt outside DISPUTED rejected | ☐ |

---

## 💡 Pro Tips

### 1. Prepare Clipboard Content

Save these in a notepad for easy demo:

```
CLIENT_ADDRESS: 0x______
FREELANCER_ADDRESS: 0x______
ARBITER_ADDRESS: 0x______

WORK_URL: https://raw.githubusercontent.com/requests/requests/main/README.md
WORK_DESCRIPTION: Comprehensive Python HTTP library README with installation via pip...
```

### 2. Use Summary JSON

`get_summary()` returns all contract state in one call:

```json
{
  "state": "APPROVED",
  "client": "0x...",
  "freelancer": "0x...",
  "arbiter": "0x...",
  "amount_wei": 5000000000000000000,
  "work_url": "https://...",
  "claim_attempts": 0,
  "max_claim_attempts": 3
}
```

Screenshot this at key moments for proof.

### 3. Recording Demos

For Builder Program:
- Record with OBS/Loom
- 10-minute walkthrough showing all 3 fallback mechanisms
- Emphasize the **anti-lockup safety valve** — this is your unique value prop

---

## 🎬 Demo Script Highlights

Here's what to say at each step for maximum impact:

> **Step 1 (Deploy):** "I'm deploying an escrow contract with a 200+ character structured brief. Notice the 4 required fields — title, description, acceptance criteria, deliverable format. This prevents trivial briefs like 'make me a website'."
>
> **Step 3 (Fund):** "Client locks 5 GEN in the contract and assigns a specific freelancer. Funds are in the contract ghost wallet now."
>
> **Step 4 (Submit):** "Freelancer submits their work URL. GenLayer's LLM validators will fetch this URL, compare content against the brief, and reach consensus on whether it meets all criteria. This takes 60-90 seconds of real AI work."
>
> **Step 9 (Force release):** "Key feature: if AI disputes AND client goes offline AND arbiter is unresponsive — the freelancer can still unlock funds after logging 3 claim attempts. Funds **cannot be permanently stuck**. This was a direct response to feedback during my review."

---

## 🔗 Back

← [Testing Overview](./TESTING.md)
← [Main README](../README.md)
