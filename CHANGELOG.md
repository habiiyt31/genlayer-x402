# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-04-19

Security and reliability improvements based on GenLayer

### Added

- **Paywall, Metered, Subscription**: `withdraw(amount)` and `withdraw_all()` methods so owners can withdraw accumulated revenue. Uses the EOA transfer pattern.
- **Paywall**: `access_granted: TreeMap[Address, bool]` — explicit flag set at purchase time.
- **Paywall, Metered, Subscription**: `get_contract_balance()` view method.
- **Escrow**: `arbiter` address for neutral third-party dispute resolution.
- **Escrow**: `arbiter_rule(approve: bool)` — arbiter resolves DISPUTED state.
- **Escrow**: `freelancer_claim_attempt()` — freelancer logs claim attempts.
- **Escrow**: `force_release()` — safety valve that unlocks funds after `max_claim_attempts` are reached, preventing permanent lockup.

### Changed

- **Paywall**: `has_access(user)` now reads the explicit `access_granted` flag instead of recomputing against the current price. Price updates no longer revoke existing buyers.
- **Paywall**: `update_price()` documentation clarified — does not affect existing buyers.
- **Escrow**: constructor signature changed from `__init__(brief: str)` to structured brief with 6 parameters: `brief_title`, `brief_description`, `brief_acceptance_criteria`, `brief_deliverable_format`, `arbiter_addr`, `max_claim_attempts`.
- **Escrow**: minimum brief content raised from 20 characters total to 200+ characters (enforced per field and total).

### Fixed

- **Paywall**: revoke bug where raising the price invalidated existing buyers' access.
- **All 3 payment contracts**: revenue could previously only accumulate, never be withdrawn.
- **Escrow**: if client went offline in DISPUTED state, freelancer was locked out forever with no recovery path.
- **Escrow**: trivial briefs like "make me a website" previously passed the 20-char minimum.

---

## [0.1.0] - 2026-04-18

Initial release.

### Added

- `x402_paywall.py` — one-time payment → permanent access
- `x402_metered.py` — credit-based per-call billing with AI-summarized responses
- `x402_subscription.py` — quota-based periodic subscription
- `x402_escrow.py` — AI-verified freelance payment escrow
- Multi-network support: localnet, studionet, testnet-bradbury
- TypeScript batch deploy script (`deploy/deployScript.ts`)
- CLI per-contract deployment guide
- GenLayer Studio deployment guide

---

[0.2.0]: https://github.com/YOUR_USERNAME/genlayer-x402/releases/tag/v0.2.0
[0.1.0]: https://github.com/YOUR_USERNAME/genlayer-x402/releases/tag/v0.1.0
