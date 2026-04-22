# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

---

## [0.2.1] - 2026-04-22

Minor improvements and packaging updates.

### Changed

- Updated project metadata in `pyproject.toml`
- Added author email for PyPI verification
- Improved project URLs (Homepage, Repository, Issues)
- Packaging cleanup for better PyPI distribution

---

## [0.2.0] - 2026-04-19

Security and reliability improvements based on GenLayer.

### Added

- **Paywall, Metered, Subscription**
  - `withdraw(amount)` and `withdraw_all()` for owner revenue withdrawal
  - `get_contract_balance()` view method

- **Paywall**
  - `access_granted: TreeMap[Address, bool]` explicit access tracking

- **Escrow**
  - `arbiter` address for third-party dispute resolution
  - `arbiter_rule(approve: bool)` for dispute resolution
  - `freelancer_claim_attempt()` for tracking attempts
  - `force_release()` safety mechanism after max attempts

### Changed

- **Paywall**
  - `has_access(user)` now uses stored access instead of recalculating
  - Price updates no longer affect existing users

- **Escrow**
  - Constructor updated to structured format:
    `brief_title`, `brief_description`, `brief_acceptance_criteria`,
    `brief_deliverable_format`, `arbiter_addr`, `max_claim_attempts`
  - Minimum brief length increased (200+ characters)

### Fixed

- **Paywall**
  - Fixed access revocation when price changes

- **All payment contracts**
  - Added missing withdrawal mechanism

- **Escrow**
  - Prevented permanent lock when client inactive
  - Rejected low-quality briefs

---

## [0.1.0] - 2026-04-18

Initial release.

### Added

- `x402_paywall.py` — one-time payment access
- `x402_metered.py` — credit-based billing
- `x402_subscription.py` — subscription model
- `x402_escrow.py` — freelance escrow system
- Multi-network support
- Deployment scripts and guides
