"""
genlayer-x402 — Deploy All Contracts
======================================
Deploys all 4 x402 contracts to the configured network.

Usage:
    # Deploy to localnet (default)
    python deploy/deploy_all.py

    # Deploy to testnet Bradbury
    genlayer network set testnet_bradbury
    python deploy/deploy_all.py

    # Deploy specific contract only
    python deploy/deploy_all.py --contract paywall
"""
import json
import sys
from gltest import get_contract_factory


def deploy_paywall():
    print("\n📦 Deploying X402Paywall...")
    factory  = get_contract_factory("x402_paywall")
    contract = factory.deploy(args=[
        100,   # price_wei: 100 wei per access
        "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    ])
    print(f"   ✓ Address: {contract.address}")
    print(f"   ✓ Tx Hash: {contract.deploy_tx_hash}")
    return contract.address


def deploy_metered():
    print("\n📦 Deploying X402Metered...")
    factory  = get_contract_factory("x402_metered")
    contract = factory.deploy(args=[
        10,    # price_per_call_wei: 10 wei per call
        "https://api.coingecko.com/api/v3/simple/price?ids=",
        100    # max_credits per user
    ])
    print(f"   ✓ Address: {contract.address}")
    print(f"   ✓ Tx Hash: {contract.deploy_tx_hash}")
    return contract.address


def deploy_subscription():
    print("\n📦 Deploying X402Subscription...")
    factory  = get_contract_factory("x402_subscription")
    contract = factory.deploy(args=[
        100,   # price_per_period_wei
        1000,  # period_blocks (~2000 seconds ≈ 33 min)
        "https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate"
    ])
    print(f"   ✓ Address: {contract.address}")
    print(f"   ✓ Tx Hash: {contract.deploy_tx_hash}")
    return contract.address


def deploy_escrow():
    print("\n📦 Deploying X402Escrow...")
    factory  = get_contract_factory("x402_escrow")
    contract = factory.deploy(args=[
        "Build a Python script that fetches BTC price from CoinGecko API and prints it formatted.",
        500    # deadline: 500 blocks
    ])
    print(f"   ✓ Address: {contract.address}")
    print(f"   ✓ Tx Hash: {contract.deploy_tx_hash}")
    return contract.address


def main():
    target = sys.argv[1].replace("--contract ", "") if len(sys.argv) > 1 else "all"

    print("=" * 55)
    print("  genlayer-x402 — Deployment Script")
    print("=" * 55)

    addresses = {}

    if target in ("all", "paywall"):
        addresses["paywall"] = deploy_paywall()

    if target in ("all", "metered"):
        addresses["metered"] = deploy_metered()

    if target in ("all", "subscription"):
        addresses["subscription"] = deploy_subscription()

    if target in ("all", "escrow"):
        addresses["escrow"] = deploy_escrow()

    # Save addresses to file for frontend
    with open("deploy/deployed_addresses.json", "w") as f:
        json.dump(addresses, f, indent=2)

    print("\n" + "=" * 55)
    print("  ✅ Deployment complete!")
    print("  📄 Addresses saved to deploy/deployed_addresses.json")
    print("=" * 55)
    print(json.dumps(addresses, indent=2))


if __name__ == "__main__":
    main()
