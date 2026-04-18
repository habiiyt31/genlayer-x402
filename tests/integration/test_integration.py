"""
genlayer-x402 — Integration Tests (Testnet)
=============================================
Run with: gltest tests/integration/ -v -s --network testnet_bradbury

These tests deploy contracts to real testnet and verify end-to-end flows.
Requires funded account in gltest.config.yaml.
"""
import json
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


class TestPaywallIntegration:

    def test_full_paywall_flow(self):
        """Full x402 paywall flow on testnet."""
        factory  = get_contract_factory("x402_paywall")
        contract = factory.deploy(args=[
            100,                                  # price_wei = 100
            "https://api.coinbase.com/v2/prices/BTC-USD/spot"
        ])
        assert contract.address is not None
        print(f"\n✓ Paywall deployed: {contract.address}")

        # Verify initial state
        price = contract.get_price(args=[]).call()
        assert price == 100
        print(f"✓ Price confirmed: {price} wei")

        # Check 402 info
        info = contract.get_402_info(args=[]).call()
        parsed = json.loads(info)
        assert parsed["protocol"] == "x402-genlayer"
        print(f"✓ 402 info: {info}")

        # Pay for access
        tx = contract.pay_for_access(args=[]).transact(value=100)
        assert tx_execution_succeeded(tx)
        print(f"✓ Payment tx: {tx['hash']}")

        # Verify access granted
        has_access = contract.has_access(args=[contract.owner]).call()
        assert has_access == True
        print(f"✓ Access granted")

        # Get protected data
        data = contract.get_protected_data(args=[contract.owner]).call()
        assert len(data) > 0
        print(f"✓ Protected data received: {data[:100]}...")


class TestMeteredIntegration:

    def test_full_metered_flow(self):
        """Full x402 metered billing flow on testnet."""
        factory  = get_contract_factory("x402_metered")
        contract = factory.deploy(args=[
            10,    # price_per_call_wei
            "https://api.coingecko.com/api/v3/simple/price?ids=",
            50     # max_credits
        ])
        print(f"\n✓ Metered deployed: {contract.address}")

        # Buy 3 credits
        tx = contract.buy_credits(args=[]).transact(value=30)
        assert tx_execution_succeeded(tx)
        credits = contract.check_credits(args=[contract.owner]).call()
        assert credits == 3
        print(f"✓ Credits purchased: {credits}")

        # Execute query
        tx2 = contract.execute_query(args=["bitcoin&vs_currencies=usd"]).transact()
        assert tx_execution_succeeded(tx2)
        remaining = contract.check_credits(args=[contract.owner]).call()
        assert remaining == 2
        print(f"✓ Query executed. Remaining credits: {remaining}")


class TestSubscriptionIntegration:

    def test_full_subscription_flow(self):
        """Full x402 subscription flow on testnet."""
        factory  = get_contract_factory("x402_subscription")
        contract = factory.deploy(args=[
            100,    # price_per_period_wei
            100,    # period_blocks (~200 seconds)
            "https://api.github.com/repos/genlayerlabs/genlayer-project-boilerplate"
        ])
        print(f"\n✓ Subscription deployed: {contract.address}")

        # Subscribe for 1 period
        tx = contract.subscribe(args=[1]).transact(value=100)
        assert tx_execution_succeeded(tx)
        is_active = contract.is_active(args=[contract.owner]).call()
        assert is_active == True
        print(f"✓ Subscription active")

        # Get data
        data = contract.get_data(args=[contract.owner]).call()
        assert len(data) > 0
        print(f"✓ Subscription data received: {data[:100]}...")


class TestEscrowIntegration:

    def test_full_escrow_flow(self):
        """Full x402 escrow flow on testnet."""
        factory  = get_contract_factory("x402_escrow")
        contract = factory.deploy(args=[
            "Build a Python script that fetches Bitcoin price from CoinGecko API and prints it formatted.",
            500    # deadline in 500 blocks
        ])
        print(f"\n✓ Escrow deployed: {contract.address}")
        assert contract.get_state(args=[]).call() == "OPEN"

        # Fund the escrow (client = deployer, use second account as freelancer)
        tx = contract.fund(args=[contract.accounts[1]]).transact(value=200)
        assert tx_execution_succeeded(tx)
        assert contract.get_state(args=[]).call() == "FUNDED"
        print(f"✓ Escrow funded: 200 wei")

        # Freelancer submits work
        tx2 = contract.submit_work(args=[
            "https://gist.github.com/example/bitcoin-price-fetcher",
            "Python script using requests library to fetch BTC price from CoinGecko"
        ]).transact(sender=contract.accounts[1])
        assert tx_execution_succeeded(tx2)

        state = contract.get_state(args=[]).call()
        print(f"✓ Work submitted. AI verdict state: {state}")

        summary = contract.get_summary(args=[]).call()
        print(f"✓ Summary: {summary}")
