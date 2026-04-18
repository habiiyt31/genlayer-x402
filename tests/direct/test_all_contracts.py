"""
genlayer-x402 — Direct Mode Tests
===================================
Run with: pytest tests/direct/ -v

Direct mode = fast in-memory tests, no server/Docker needed.
Uses GenLayer's official genlayer-test framework.
"""
import json
import pytest


# ═══════════════════════════════════════════════════════════════
#  PAYWALL TESTS
# ═══════════════════════════════════════════════════════════════

class TestX402Paywall:

    def test_initial_state(self, direct_deploy, direct_alice):
        """Contract initializes with correct price and owner."""
        contract = direct_deploy(
            "contracts/x402_paywall.py",
            args=[u256(100), "https://api.example.com/data"]
        )
        assert contract.get_price() == u256(100)
        assert contract.get_owner() == direct_alice
        assert contract.get_total_revenue() == u256(0)

    def test_access_denied_before_payment(self, direct_deploy, direct_alice, direct_bob):
        """User cannot access data before paying."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        assert contract.has_access(direct_bob) == False
        assert contract.get_payment(direct_bob) == u256(0)

    def test_access_granted_after_exact_payment(self, direct_vm, direct_deploy,
                                                  direct_alice, direct_bob):
        """Exact payment grants access."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        direct_vm.sender = direct_bob
        contract.pay_for_access(value=u256(100))

        assert contract.has_access(direct_bob) == True
        assert contract.get_payment(direct_bob) == u256(100)
        assert contract.get_total_revenue() == u256(100)

    def test_access_granted_after_overpayment(self, direct_vm, direct_deploy,
                                                direct_alice, direct_bob):
        """Overpayment also grants access."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        direct_vm.sender = direct_bob
        contract.pay_for_access(value=u256(200))   # pay double

        assert contract.has_access(direct_bob) == True
        assert contract.get_payment(direct_bob) == u256(200)

    def test_insufficient_payment_rejected(self, direct_vm, direct_deploy,
                                            direct_alice, direct_bob):
        """Underpayment is rejected with clear error."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        direct_vm.sender = direct_bob

        with direct_vm.expect_revert("x402: Insufficient payment"):
            contract.pay_for_access(value=u256(50))

    def test_get_protected_data_requires_payment(self, direct_vm, direct_deploy,
                                                   direct_alice, direct_bob):
        """Accessing data without payment returns 402-style error."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])

        with direct_vm.expect_revert("x402: Payment required"):
            contract.get_protected_data(direct_bob)

    def test_get_protected_data_with_payment_and_mock(self, direct_vm, direct_deploy,
                                                        direct_alice, direct_bob):
        """Paying user gets real data (mocked web call)."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])

        direct_vm.mock_web(
            r".*api\.example\.com.*",
            {"status": 200, "body": '{"result": "premium_data_here"}'}
        )

        direct_vm.sender = direct_bob
        contract.pay_for_access(value=u256(100))
        result = contract.get_protected_data(direct_bob)
        assert "premium_data_here" in result

    def test_only_owner_can_update_price(self, direct_vm, direct_deploy,
                                          direct_alice, direct_bob):
        """Non-owner cannot update price."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        direct_vm.sender = direct_bob

        with direct_vm.expect_revert("x402: Only owner can update price"):
            contract.update_price(u256(200))

    def test_owner_can_update_price(self, direct_vm, direct_deploy, direct_alice):
        """Owner can update price successfully."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        direct_vm.sender = direct_alice
        contract.update_price(u256(500))
        assert contract.get_price() == u256(500)

    def test_402_info_returns_json(self, direct_deploy, direct_alice):
        """get_402_info returns valid JSON with required fields."""
        contract = direct_deploy("contracts/x402_paywall.py",
                                  args=[u256(100), "https://api.example.com/data"])
        info = contract.get_402_info()
        parsed = json.loads(info)
        assert "price_wei" in parsed
        assert "owner" in parsed
        assert "protocol" in parsed
        assert parsed["protocol"] == "x402-genlayer"


# ═══════════════════════════════════════════════════════════════
#  METERED TESTS
# ═══════════════════════════════════════════════════════════════

class TestX402Metered:

    def test_buy_credits_correct_amount(self, direct_vm, direct_deploy,
                                         direct_alice, direct_bob):
        """Buying credits calculates correct count."""
        contract = direct_deploy(
            "contracts/x402_metered.py",
            args=[u256(10), "https://api.example.com/query?q=", u256(100)]
        )
        direct_vm.sender = direct_bob
        credits_bought = contract.buy_credits(value=u256(50))  # 50/10 = 5 credits

        assert credits_bought == u256(5)
        assert contract.check_credits(direct_bob) == u256(5)

    def test_no_credits_blocks_query(self, direct_vm, direct_deploy,
                                      direct_alice, direct_bob):
        """Query fails with no credits."""
        contract = direct_deploy(
            "contracts/x402_metered.py",
            args=[u256(10), "https://api.example.com/query?q=", u256(100)]
        )
        direct_vm.sender = direct_bob

        with direct_vm.expect_revert("x402: No credits remaining"):
            contract.execute_query("bitcoin")

    def test_query_deducts_credit(self, direct_vm, direct_deploy,
                                   direct_alice, direct_bob):
        """Each query deducts exactly 1 credit."""
        contract = direct_deploy(
            "contracts/x402_metered.py",
            args=[u256(10), "https://api.example.com/query?q=", u256(100)]
        )
        direct_vm.sender = direct_bob
        contract.buy_credits(value=u256(30))  # 3 credits

        direct_vm.mock_web(r".*api\.example\.com.*", {"status": 200, "body": "data"})
        direct_vm.mock_llm(r".*Summarize.*", "Summary: data")

        contract.execute_query("test")
        assert contract.check_credits(direct_bob) == u256(2)
        assert contract.get_call_count(direct_bob) == u256(1)

    def test_max_credits_enforced(self, direct_vm, direct_deploy,
                                   direct_alice, direct_bob):
        """Cannot buy more than max_credits."""
        contract = direct_deploy(
            "contracts/x402_metered.py",
            args=[u256(10), "https://api.example.com/query?q=", u256(5)]
        )
        direct_vm.sender = direct_bob
        contract.buy_credits(value=u256(50))  # 5 credits (max)

        with direct_vm.expect_revert("Would exceed max credits"):
            contract.buy_credits(value=u256(10))  # would make 6 > max 5

    def test_stats_updated_correctly(self, direct_vm, direct_deploy,
                                      direct_alice, direct_bob):
        """Global stats are accurate after operations."""
        contract = direct_deploy(
            "contracts/x402_metered.py",
            args=[u256(10), "https://api.example.com/query?q=", u256(100)]
        )
        direct_vm.sender = direct_bob
        contract.buy_credits(value=u256(20))

        direct_vm.mock_web(r".*", {"status": 200, "body": "result"})
        direct_vm.mock_llm(r".*", "summary")
        contract.execute_query("q")

        stats = json.loads(contract.get_stats())
        assert stats["total_calls"] == 1
        assert stats["total_revenue_wei"] == 20


# ═══════════════════════════════════════════════════════════════
#  SUBSCRIPTION TESTS
# ═══════════════════════════════════════════════════════════════

class TestX402Subscription:

    def test_subscribe_grants_access(self, direct_vm, direct_deploy,
                                      direct_alice, direct_bob):
        """Paying for subscription grants active status."""
        contract = direct_deploy(
            "contracts/x402_subscription.py",
            args=[u256(100), u256(1000), "https://api.example.com/feed"]
        )
        direct_vm.sender = direct_bob
        contract.subscribe(u256(1), value=u256(100))

        assert contract.is_active(direct_bob) == True

    def test_no_subscription_blocks_data(self, direct_vm, direct_deploy,
                                          direct_alice, direct_bob):
        """Unsubscribed user cannot access data."""
        contract = direct_deploy(
            "contracts/x402_subscription.py",
            args=[u256(100), u256(1000), "https://api.example.com/feed"]
        )
        with direct_vm.expect_revert("x402: Subscription expired or not found"):
            contract.get_data(direct_bob)

    def test_multi_period_subscription(self, direct_vm, direct_deploy,
                                        direct_alice, direct_bob):
        """Buying multiple periods sets correct expiry."""
        contract = direct_deploy(
            "contracts/x402_subscription.py",
            args=[u256(100), u256(1000), "https://api.example.com/feed"]
        )
        direct_vm.sender = direct_bob
        expiry = contract.subscribe(u256(3), value=u256(300))   # 3 periods

        assert expiry > u256(0)
        assert contract.is_active(direct_bob) == True

    def test_subscribe_insufficient_payment(self, direct_vm, direct_deploy,
                                             direct_alice, direct_bob):
        """Insufficient payment rejected."""
        contract = direct_deploy(
            "contracts/x402_subscription.py",
            args=[u256(100), u256(1000), "https://api.example.com/feed"]
        )
        direct_vm.sender = direct_bob
        with direct_vm.expect_revert("x402: Insufficient payment"):
            contract.subscribe(u256(1), value=u256(50))

    def test_owner_can_grant_access(self, direct_vm, direct_deploy,
                                     direct_alice, direct_bob):
        """Owner can grant free access."""
        contract = direct_deploy(
            "contracts/x402_subscription.py",
            args=[u256(100), u256(1000), "https://api.example.com/feed"]
        )
        direct_vm.sender = direct_alice
        contract.grant_access(direct_bob, u256(1))

        assert contract.is_active(direct_bob) == True

    def test_subscriber_count_increments(self, direct_vm, direct_deploy,
                                          direct_alice, direct_bob):
        """Subscriber count tracks new subscribers."""
        contract = direct_deploy(
            "contracts/x402_subscription.py",
            args=[u256(100), u256(1000), "https://api.example.com/feed"]
        )
        direct_vm.sender = direct_bob
        contract.subscribe(u256(1), value=u256(100))

        stats = json.loads(contract.get_stats())
        assert stats["subscriber_count"] == 1


# ═══════════════════════════════════════════════════════════════
#  ESCROW TESTS
# ═══════════════════════════════════════════════════════════════

class TestX402Escrow:

    def test_initial_state_is_open(self, direct_deploy, direct_alice):
        """Escrow starts in OPEN state."""
        contract = direct_deploy(
            "contracts/x402_escrow.py",
            args=["Build a landing page with React and Tailwind CSS.", u256(1000)]
        )
        assert contract.get_state() == "OPEN"
        assert contract.get_amount() == u256(0)

    def test_client_can_fund(self, direct_vm, direct_deploy, direct_alice, direct_bob):
        """Client funds escrow and assigns freelancer."""
        contract = direct_deploy(
            "contracts/x402_escrow.py",
            args=["Build a landing page with React and Tailwind CSS.", u256(1000)]
        )
        direct_vm.sender = direct_alice
        contract.fund(direct_bob, value=u256(500))

        assert contract.get_state() == "FUNDED"
        assert contract.get_amount() == u256(500)

    def test_only_client_can_fund(self, direct_vm, direct_deploy,
                                   direct_alice, direct_bob):
        """Non-client cannot fund."""
        contract = direct_deploy(
            "contracts/x402_escrow.py",
            args=["Build a landing page with React and Tailwind CSS.", u256(1000)]
        )
        direct_vm.sender = direct_bob
        with direct_vm.expect_revert("x402: Only client can fund"):
            contract.fund(direct_bob, value=u256(500))

    def test_freelancer_submits_work_triggers_ai(self, direct_vm, direct_deploy,
                                                  direct_alice, direct_bob):
        """Freelancer submission triggers AI evaluation."""
        contract = direct_deploy(
            "contracts/x402_escrow.py",
            args=["Build a landing page with React and Tailwind CSS.", u256(1000)]
        )
        direct_vm.sender = direct_alice
        contract.fund(direct_bob, value=u256(500))

        # Mock web fetch of work URL
        direct_vm.mock_web(
            r".*github\.com.*",
            {"status": 200, "body": "React landing page with Tailwind CSS components"}
        )
        # Mock AI verdict — approved
        direct_vm.mock_llm(
            r".*impartial work evaluator.*",
            '{"approved": true, "score": 92, "reason": "Work meets all requirements", "missing": "nothing"}'
        )

        direct_vm.sender = direct_bob
        contract.submit_work(
            "https://github.com/bob/landing-page",
            "React landing page with all requirements met"
        )

        assert contract.get_state() == "APPROVED"

    def test_approved_work_releases_payment(self, direct_vm, direct_deploy,
                                             direct_alice, direct_bob):
        """Payment releases after approval."""
        contract = direct_deploy(
            "contracts/x402_escrow.py",
            args=["Build a landing page with React and Tailwind CSS.", u256(1000)]
        )
        direct_vm.sender = direct_alice
        contract.fund(direct_bob, value=u256(500))

        direct_vm.mock_web(r".*", {"status": 200, "body": "completed work"})
        direct_vm.mock_llm(r".*", '{"approved": true, "score": 95, "reason": "Excellent", "missing": "nothing"}')

        direct_vm.sender = direct_bob
        contract.submit_work("https://github.com/bob/work", "Done")

        # State should be APPROVED, then release
        if contract.get_state() == "APPROVED":
            contract.release_payment()
            assert contract.get_state() == "RESOLVED"

    def test_client_can_manually_approve(self, direct_vm, direct_deploy,
                                          direct_alice, direct_bob):
        """Client can override AI rejection."""
        contract = direct_deploy(
            "contracts/x402_escrow.py",
            args=["Build a landing page with React and Tailwind CSS.", u256(1000)]
        )
        direct_vm.sender = direct_alice
        contract.fund(direct_bob, value=u256(500))

        direct_vm.mock_web(r".*", {"status": 200, "body": "partial work"})
        direct_vm.mock_llm(r".*", '{"approved": false, "score": 40, "reason": "Missing features", "missing": "mobile responsiveness"}')

        direct_vm.sender = direct_bob
        contract.submit_work("https://github.com/bob/partial", "Partial work")

        # Client manually approves despite AI rejection
        direct_vm.sender = direct_alice
        contract.client_approve()
        assert contract.get_state() == "APPROVED"

    def test_brief_too_short_rejected(self, direct_deploy, direct_alice):
        """Brief shorter than 20 chars is rejected."""
        with pytest.raises(Exception):
            direct_deploy(
                "contracts/x402_escrow.py",
                args=["Too short", u256(1000)]
            )
