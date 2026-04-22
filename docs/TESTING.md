# Testing Overview — genlayer-x402

This folder contains step-by-step testing guides for all 4 x402 contracts. Each guide walks you through deploying, interacting, and verifying every method in GenLayer Studio or CLI.

---

## 🏗️ Prerequisites

### 1. Install the package and tools

```bash
pip install genlayer-x402 genvm-linter
npm install -g genlayer
```

### 2. Copy contracts to your project

```bash
python -c "
import genlayer_x402, os, shutil
src = os.path.dirname(genlayer_x402.__file__)
os.makedirs('contracts', exist_ok=True)
for f in ['x402_paywall', 'x402_metered', 'x402_subscription', 'x402_escrow']:
    shutil.copy(f'{src}/{f}.py', f'contracts/{f}.py')
    print(f'Copied {f}.py')
"
```

> ⚠️ Each contract file is **self-contained**. No other dependencies needed after copying.

### 3. Lint all contracts before deploying

```bash
genvm-lint check contracts/x402_paywall.py
genvm-lint check contracts/x402_metered.py
genvm-lint check contracts/x402_subscription.py
genvm-lint check contracts/x402_escrow.py
```

All should return exit code `0` before proceeding.

### 4. Start GenLayer Studio (if testing locally)

```bash
genlayer init
genlayer up
```

Or use [studio.genlayer.com](https://studio.genlayer.com) directly.

### 5. Get test GEN tokens

Visit [testnet-faucet.genlayer.foundation](https://testnet-faucet.genlayer.foundation/) and request tokens for your test account.

---

## 💱 Wei Conversion Reference

All value arguments use wei, not GEN:

| GEN | Wei |
|---|---|
| 0.001 | `1000000000000000` |
| 0.01 | `10000000000000000` |
| 0.1 | `100000000000000000` |
| **1** | **`1000000000000000000`** |
| 5 | `5000000000000000000` |
| 10 | `10000000000000000000` |

> 💡 In GenLayer Studio, the **Value field** auto-multiplies by 10¹⁸ for payable methods. But **constructor arguments** must be entered as full wei values.

---

## 🧪 Testing Guides

| Contract | Guide | Est. Time |
|---|---|---|
| X402Paywall | [test-paywall.md](test-paywall.md) | ~20 min |
| X402Metered | [test-metered.md](test-metered.md) | ~25 min |
| X402Subscription | [test-subscription.md](test-subscription.md) | ~30 min |
| X402Escrow | [test-escrow.md](test-escrow.md) | ~40 min |

---

## 💡 General Tips

- **Save contract addresses** after each deploy — you'll need them for all subsequent calls.
- **Switch accounts** in Studio to simulate different users (buyer vs owner vs freelancer).
- **Check the Logs panel** in Studio if a transaction fails — the error message is always there.
- **Studio Value field** auto-multiplies by 10¹⁸ for payable methods. Constructor args are entered as-is in wei.
- **Wait 30-90 seconds** for any method that calls `gl.nondet.web.get()` or `gl.nondet.exec_prompt()` — validators need time to reach consensus.

---

## 🔗 Back

← [Main README](../README.md)