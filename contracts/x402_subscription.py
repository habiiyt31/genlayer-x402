# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class X402Subscription(gl.Contract):
    """
    genlayer-x402 :: Subscription Contract
    ========================================
    Time-based subscription model. Pay once for a period,
    renew to extend. Access expires when period ends.

    Use case: monthly data feed, weekly analytics report,
              time-limited API access.

    x402 Flow:
        1. User calls subscribe() with GEN for N periods
        2. Contract records expiry timestamp
        3. User calls get_data() → works until expiry
        4. User can renew anytime before or after expiry

    Args (constructor):
        price_per_period_wei (u256): Price per period in wei
        period_blocks        (u256): Duration in blocks (~1 block=2s on GenLayer)
        data_url             (str):  URL to fetch for subscribers
    """

    price_per_period_wei: u256
    period_blocks:        u256
    owner:                Address
    data_url:             str
    subscriptions:        TreeMap[Address, u256]   # addr → expiry block
    total_revenue:        u256
    subscriber_count:     u256

    def __init__(self, price_per_period_wei: u256, period_blocks: u256, data_url: str):
        assert price_per_period_wei > u256(0), "Price must be > 0"
        assert period_blocks > u256(0),         "Period must be > 0"

        self.price_per_period_wei = price_per_period_wei
        self.period_blocks        = period_blocks
        self.owner                = gl.message.sender_address
        self.data_url             = data_url
        self.subscriptions        = TreeMap()
        self.total_revenue        = u256(0)
        self.subscriber_count     = u256(0)

    # ── READ ────────────────────────────────────────────────────────

    @gl.public.view
    def get_price(self) -> u256:
        return self.price_per_period_wei

    @gl.public.view
    def get_period_blocks(self) -> u256:
        return self.period_blocks

    @gl.public.view
    def get_expiry(self, user: Address) -> u256:
        """Return block number when user's subscription expires. 0 = never subscribed."""
        return self.subscriptions.get(user, u256(0))

    @gl.public.view
    def is_active(self, user: Address) -> bool:
        """Return True if user's subscription is currently active."""
        expiry = self.subscriptions.get(user, u256(0))
        if expiry == u256(0):
            return False
        return gl.block.number <= expiry

    @gl.public.view
    def get_stats(self) -> str:
        return (
            f'{{"subscriber_count": {self.subscriber_count}, '
            f'"total_revenue_wei": {self.total_revenue}, '
            f'"price_per_period_wei": {self.price_per_period_wei}, '
            f'"period_blocks": {self.period_blocks}}}'
        )

    @gl.public.view
    def get_402_info(self) -> str:
        return (
            f'{{"price_per_period_wei": {self.price_per_period_wei}, '
            f'"period_blocks": {self.period_blocks}, '
            f'"owner": "{self.owner}", '
            f'"protocol": "x402-genlayer-subscription"}}'
        )

    # ── WRITE ───────────────────────────────────────────────────────

    @gl.public.write.payable
    def subscribe(self, periods: u256) -> u256:
        """
        Purchase or extend a subscription.
        periods: number of periods to purchase (minimum 1)
        Returns expiry block number after subscription.
        """
        assert periods > u256(0), "Must purchase at least 1 period"
        required = self.price_per_period_wei * periods
        assert gl.message.value >= required, \
            f"x402: Insufficient payment. Required {required} wei for {periods} period(s)."

        sender     = gl.message.sender_address
        current_expiry = self.subscriptions.get(sender, u256(0))
        current_block  = gl.block.number

        # If already active, extend from current expiry; else start from now
        base = current_expiry if current_expiry > current_block else current_block
        new_expiry = base + (self.period_blocks * periods)

        is_new = current_expiry == u256(0)
        self.subscriptions[sender] = new_expiry
        self.total_revenue         = self.total_revenue + gl.message.value

        if is_new:
            self.subscriber_count = self.subscriber_count + u256(1)

        return new_expiry

    @gl.public.view
    def get_data(self, user: Address) -> str:
        """
        Fetch and return subscription-gated data.
        Raises error if subscription is expired or missing.
        """
        assert self.is_active(user), \
            (f"x402: Subscription expired or not found. "
             f"Subscribe via subscribe(). Price: {self.price_per_period_wei} wei/period.")

        def fetch() -> str:
            raw = gl.get_webpage(self.data_url, mode="text")
            return raw

        return gl.eq_principle_strict_eq(fetch)

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_price > u256(0), "Price must be > 0"
        self.price_per_period_wei = new_price

    @gl.public.write
    def update_data_url(self, new_url: str) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        self.data_url = new_url

    @gl.public.write
    def grant_access(self, user: Address, periods: u256) -> None:
        """Owner can grant free access (for promo/testing)."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        current_block  = gl.block.number
        current_expiry = self.subscriptions.get(user, u256(0))
        base           = current_expiry if current_expiry > current_block else current_block
        new_expiry     = base + (self.period_blocks * periods)

        is_new = current_expiry == u256(0)
        self.subscriptions[user] = new_expiry
        if is_new:
            self.subscriber_count = self.subscriber_count + u256(1)

    @gl.public.write
    def withdraw(self, amount: u256) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert amount <= self.balance, "x402: Insufficient balance"

        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass
        _EOA(self.owner).emit_transfer(value=amount)
