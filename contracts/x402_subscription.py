# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing


class X402Subscription(gl.Contract):
    """
    X402 Subscription — Usage-based subscription.

    User pays for N uses per period. Each use (get_data call)
    decrements the quota. User can top up anytime to extend.
    Owner can withdraw accumulated revenue via withdraw().
    """

    price_per_period_wei: u256
    calls_per_period: u256
    owner: Address
    data_url: str
    remaining_calls: TreeMap[Address, u256]
    total_periods_sold: u256
    total_revenue: u256
    subscriber_count: u256

    def __init__(
        self,
        price_per_period_wei: u256,
        calls_per_period: u256,
        data_url: str,
    ):
        """
        Initialize subscription contract.

        Args:
            price_per_period_wei (u256): Cost per subscription period
            calls_per_period     (u256): Number of calls per period
            data_url             (str):  URL for subscriber data
        """
        assert price_per_period_wei > u256(0), "Price must be > 0"
        assert calls_per_period > u256(0), "Calls per period must be > 0"
        assert len(data_url) > 0, "URL cannot be empty"

        self.price_per_period_wei = price_per_period_wei
        self.calls_per_period = calls_per_period
        self.owner = gl.message.sender_address
        self.data_url = data_url
        self.total_periods_sold = u256(0)
        self.total_revenue = u256(0)
        self.subscriber_count = u256(0)

    # ── VIEW METHODS ──────────────────────────────────────────────

    @gl.public.view
    def get_price(self) -> u256:
        return self.price_per_period_wei

    @gl.public.view
    def get_calls_per_period(self) -> u256:
        return self.calls_per_period

    @gl.public.view
    def get_remaining_calls(self, user_address: str) -> u256:
        user = Address(user_address)
        return self.remaining_calls.get(user, u256(0))

    @gl.public.view
    def is_active(self, user_address: str) -> bool:
        user = Address(user_address)
        return self.remaining_calls.get(user, u256(0)) > u256(0)

    @gl.public.view
    def get_total_periods_sold(self) -> u256:
        return self.total_periods_sold

    @gl.public.view
    def get_subscriber_count(self) -> u256:
        return self.subscriber_count

    @gl.public.view
    def get_total_revenue(self) -> u256:
        return self.total_revenue

    @gl.public.view
    def get_contract_balance(self) -> u256:
        """Current GEN balance held by the contract."""
        return self.balance

    @gl.public.view
    def get_402_info(self) -> str:
        return (
            '{"price_per_period_wei": ' + str(self.price_per_period_wei) +
            ', "calls_per_period": ' + str(self.calls_per_period) +
            ', "owner": "' + self.owner.as_hex +
            '", "protocol": "x402-genlayer", "type": "subscription"}'
        )

    # ── WRITE METHODS ─────────────────────────────────────────────

    @gl.public.write.payable
    def subscribe(self, periods: u256) -> None:
        """
        Subscribe for N periods.
        Each period grants `calls_per_period` uses.
        Periods stack — buying 3 gives 3x calls_per_period.
        """
        assert periods > u256(0), "Must buy at least 1 period"
        required = self.price_per_period_wei * periods
        assert gl.message.value >= required, \
            "x402: Insufficient. Required " + str(required) + " wei"

        sender = gl.message.sender_address
        current = self.remaining_calls.get(sender, u256(0))

        was_new = current == u256(0)
        added = self.calls_per_period * periods
        self.remaining_calls[sender] = current + added

        self.total_periods_sold = self.total_periods_sold + periods
        self.total_revenue = self.total_revenue + gl.message.value

        if was_new:
            self.subscriber_count = self.subscriber_count + u256(1)

    @gl.public.write
    def get_data(self) -> typing.Any:
        """
        Fetch subscription-gated data. Decrements quota by 1.
        """
        sender = gl.message.sender_address
        remaining = self.remaining_calls.get(sender, u256(0))

        assert remaining > u256(0), \
            "x402: No active subscription. Subscribe for " + str(self.price_per_period_wei) + " wei/period"

        self.remaining_calls[sender] = remaining - u256(1)

        def nondet() -> str:
            response = gl.nondet.web.get(self.data_url)
            return response.body.decode("utf-8")

        return gl.eq_principle.strict_eq(nondet)

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_price > u256(0), "Price must be > 0"
        self.price_per_period_wei = new_price

    @gl.public.write
    def update_calls_per_period(self, new_count: u256) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_count > u256(0), "Must be > 0"
        self.calls_per_period = new_count

    @gl.public.write
    def grant_access(self, user_address: str, periods: u256) -> None:
        """Owner can grant free subscription."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        user = Address(user_address)
        current = self.remaining_calls.get(user, u256(0))
        was_new = current == u256(0)
        added = self.calls_per_period * periods
        self.remaining_calls[user] = current + added
        if was_new:
            self.subscriber_count = self.subscriber_count + u256(1)

    @gl.public.write
    def withdraw(self, amount: u256) -> None:
        """Owner withdraws accumulated revenue from contract balance."""
        assert gl.message.sender_address == self.owner, "x402: Only owner can withdraw"
        assert amount > u256(0), "Amount must be > 0"
        assert amount <= self.balance, \
            "x402: Insufficient balance. Available: " + str(self.balance)

        @gl.evm.contract_interface
        class _EOA:
            class View:
                pass
            class Write:
                pass

        _EOA(self.owner).emit_transfer(value=amount)

    @gl.public.write
    def withdraw_all(self) -> None:
        """Owner withdraws the entire contract balance."""
        assert gl.message.sender_address == self.owner, "x402: Only owner can withdraw"
        assert self.balance > u256(0), "x402: Contract balance is zero"

        amount = self.balance

        @gl.evm.contract_interface
        class _EOA:
            class View:
                pass
            class Write:
                pass

        _EOA(self.owner).emit_transfer(value=amount)
