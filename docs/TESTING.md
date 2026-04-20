# Testing Guide — genlayer-x402

Complete testing documentation for all 4 Intelligent Contracts in the genlayer-x402 library.

---

## 📚 Testing Docs

Each contract has its own detailed step-by-step testing guide:

| Contract | Testing Guide | Methods | Est. Time |
|---|---|---|---|
| X402Paywall | [test-paywall.md](./test-paywall.md) | 14 (8 view + 6 write) | ~20 min |
| X402Metered | [test-metered.md](./test-metered.md) | 15 (8 view + 7 write) | ~25 min |
| X402Subscription | [test-subscription.md](./test-subscription.md) | 16 (9 view + 7 write) | ~30 min |
| X402Escrow | [test-escrow.md](./test-escrow.md) | 19 (11 view + 8 write) | ~40 min |

---

## 🏗️ General Setup

Before testing any contract, complete these setup steps once.

### 1. Open GenLayer Studio

Choose one:
- **Studio Online** (recommended, zero setup): https://studio.genlayer.com
- **Studio Local** (no rate limit, needs Docker):
  ```bash
  genlayer init
  genlayer up
  ```
  Opens at http://localhost:8080

### 2. Prepare Test Accounts

Each contract needs 2-3 accounts with different roles:

| Role | Purpose |
|---|---|
| **Owner/Deployer** | Deploys the contract, can withdraw revenue |
| **User/Customer** | Interacts with paid methods |
| **Arbiter** (Escrow only) | Resolves disputes as neutral third party |

In Studio, create accounts via the dropdown in the top-right corner. Use the 💧 faucet button to fund each account.

### 3. Verify Environment

Before deploying, check:
- ✅ Python 3.12+ installed (`python --version`)
- ✅ GenLayer CLI installed (`genlayer --version`)
- ✅ Contracts pass lint (`genvm-lint check contracts/*.py`)

---

## 💰 Understanding Values (Wei vs GEN)

Per the [official GenLayer docs](https://docs.genlayer.com/developers/intelligent-contracts/features/value-transfers), **1 GEN = 10¹⁸ wei**.

### Studio Conventions

| Field | Unit | Example |
|---|---|---|
| **Value (GEN)** field in payable methods | GEN (auto × 10¹⁸) | Type `5` → sends 5 GEN |
| **Constructor args** with `_wei` suffix | wei (as-is) | Type `1000000000000000000` = 1 GEN |
| **Method args** like `withdraw(amount)` | wei (as-is) | Type `1000000000000000000` = 1 GEN |

### Wei Conversion Cheat Sheet

| Amount | Wei Value |
|---|---|
| 0.01 GEN | `10000000000000000` |
| 0.1 GEN | `100000000000000000` |
| **1 GEN** | **`1000000000000000000`** |
| 5 GEN | `5000000000000000000` |
| 10 GEN | `10000000000000000000` |

---

## 🧪 Testing Philosophy

Each testing guide follows this structure:

1. **Setup** — Accounts, deployment parameters
2. **Verify Initial State** — Call view methods to confirm correct deploy
3. **Happy Path** — Test normal flow end-to-end
4. **Owner Functions** — Test admin-only methods
5. **Error Handling** — Verify assertions reject invalid inputs
6. **Cleanup** — Withdraw revenue, verify zero balance

Each step shows:
- ✅ **Expected result** when things work
- ❌ **Expected error** when testing boundary conditions

---

## 📊 Quick Test Recommendations

### For Demo / Presentation (5-10 min)

Focus on **Metered** or **Escrow** — they showcase GenLayer's unique features (web data + AI consensus):

- **[test-metered.md](./test-metered.md)** — Quick Demo section (8 steps)
- **[test-escrow.md](./test-escrow.md)** — Quick Demo section (6 steps)

### For Full Validation (1-2 hours)

Test all 4 contracts in order:

1. [Paywall](./test-paywall.md) — Simplest, builds intuition
2. [Metered](./test-metered.md) — Shows AI summarization
3. [Subscription](./test-subscription.md) — Quota stacking mechanics
4. [Escrow](./test-escrow.md) — Complex state machine + AI verdicts

### For Code Review

Testing order:
1. Start with Paywall (confidence builder)
2. Jump to Escrow's **Force Release** flow (shows timeout safety)
3. Demonstrate Metered's AI consensus (most impressive)
4. End with Paywall's `access_granted` persistence (show security feature)

---

## 🐛 Common Issues

### "execution failed" error

Most likely caused by:
- **Invalid address format** — must be `0x` + 40 hex chars, no spaces
- **Insufficient balance** — check wallet has GEN (use 💧 faucet)
- **Transaction from wrong account** — owner-only methods reject non-owners
- **Studio Online overload** — try again in a few minutes or switch to local Studio

### Long waits on non-det methods

Methods that fetch web data (`get_protected_data`, `execute_query`, `submit_work`, `get_data`) take **30-90 seconds** because:
1. Multiple validators fetch the URL
2. LLM evaluates the content (for metered + escrow)
3. Consensus must be reached across validators

Open the **Node Logs** panel to watch the process.

### AI verdict unexpectedly DISPUTED

If `submit_work` returns DISPUTED when you expected APPROVED:
- AI validators are strict and objective
- Use `client_approve()` to manually override
- Or adjust brief to match deliverable more closely

---

## 🎯 Testing Success Criteria

A contract passes full testing if:

- ✅ All view methods return expected initial state after deploy
- ✅ Happy path executes end-to-end without errors
- ✅ Owner-only methods reject non-owner calls
- ✅ Assertions reject invalid inputs with clear error messages
- ✅ Revenue can be withdrawn (no funds stuck)
- ✅ Edge cases (exhausted credits, closed disputes) handled gracefully

---

## 🔗 Related Resources

- **Main README:** [../README.md](../README.md)
- **Changelog:** [../CHANGELOG.md](../CHANGELOG.md)
- **Contract code:** [../contracts/](../contracts/)
- **GenLayer Docs:** https://docs.genlayer.com
- **GenLayer Studio:** https://studio.genlayer.com
- **x402 Protocol Spec:** https://x402.org
