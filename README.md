# genlayer-x402

> **x402 Payment Protocol for GenLayer Intelligent Contracts**

A reusable library of **4 Intelligent Contracts** implementing the [HTTP 402 Payment Required](https://x402.org) standard on GenLayer.

This package provides ready-to-use contract patterns for building **paid APIs, AI services, and on-chain payment flows** — without centralized servers.

---

## 🚀 What is this?

`genlayer-x402` is a **contract library**, not a standalone app.

It gives you reusable building blocks for:

* Pay-per-access APIs
* Credit-based billing
* Subscription systems
* Escrow with AI verification

All logic runs **on-chain via GenLayer**, not locally.

---

## 📦 Contracts Included

| Contract           | Description                         |
| ------------------ | ----------------------------------- |
| `X402Paywall`      | One-time payment → permanent access |
| `X402Metered`      | Credit-based pay-per-call           |
| `X402Subscription` | Usage quota per period              |
| `X402Escrow`       | AI-verified escrow with safety      |

---

## 📥 Installation

### Install from GitHub

```bash
pip install git+https://github.com/habiiyt31/genlayer-x402.git
```

---

## 🧠 Usage (inside GenLayer contract)

```python
import genlayer as gl
from genlayer_x402 import X402Paywall

class MyApp(gl.Contract):
    def __init__(self):
        self.paywall = X402Paywall(
            price_wei=1000000000000000000,
            data_url="https://api.example.com"
        )
```

> ⚠️ Note:
> This library is intended to run **inside GenLayer contracts**, not as a local Python runtime.

---

## ⚙️ Deployment

Deploy contracts using GenLayer CLI:

```bash
genlayer deploy --contract contracts/x402_paywall.py
```

Follow prompts to input constructor arguments.

---

## 💰 GEN & Wei

GenLayer uses:

```
1 GEN = 10^18 wei
```

Example:

| GEN     | Wei                 |
| ------- | ------------------- |
| 1 GEN   | 1000000000000000000 |
| 0.1 GEN | 100000000000000000  |

---

## 🔐 Features

* On-chain payment verification
* Real-time web data (`gl.nondet.web.get`)
* AI-assisted validation (Escrow)
* Revenue withdrawal (`withdraw`, `withdraw_all`)
* Permanent access after payment (Paywall)
* Anti-lock escrow mechanisms

---

## 📁 Project Structure

```
genlayer-x402/
│
├── genlayer_x402/        # Library package
│   ├── __init__.py
│   ├── x402_paywall.py
│   ├── x402_metered.py
│   ├── x402_subscription.py
│   └── x402_escrow.py
│
├── docs/                 # Testing guides
├── README.md
├── LICENSE
```

---

## 🧪 Testing

See documentation in:

```
docs/
```

Each contract has its own test guide.

---

## ⚠️ Important Notes

* This is **not a local Python library**
* Contracts depend on `genlayer` runtime
* Import may fail outside GenLayer environment (this is expected)

---

## 📜 License

MIT
