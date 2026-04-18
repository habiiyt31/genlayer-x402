# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class X402Metered(gl.Contract):
    """
    genlayer-x402 :: Metered Billing Contract
    ==========================================
    Pay-per-call billing. Users buy credits, each API call
    deducts one credit. Credits can be topped up at any time.

    Use case: AI inference billing, data API with usage limits,
              per-query analytics service.

    x402 Flow:
        1. User calls buy_credits() with GEN → credits deposited
        2. User calls execute_query() → 1 credit deducted, data returned
        3. When credits run out → error with top-up instructions
        4. User can check_credits() at any time

    Args (constructor):
        price_per_call_wei (u256): Cost per API call in wei
        data_url           (str):  URL template for data fetching
        max_credits        (u256): Max credits per user (anti-abuse)
    """

    price_per_call_wei: u256
    owner:              Address
    data_url:           str
    max_credits:        u256
    credits:            TreeMap[Address, u256]   # addr → remaining credits
    call_count:         TreeMap[Address, u256]   # addr → total calls made
    total_calls:        u256
    total_revenue:      u256

    def __init__(self, price_per_call_wei: u256, data_url: str, max_credits: u256):
        assert price_per_call_wei > u256(0), "Price per call must be > 0"
        assert max_credits > u256(0),         "Max credits must be > 0"

        self.price_per_call_wei = price_per_call_wei
        self.owner              = gl.message.sender_address
        self.data_url           = data_url
        self.max_credits        = max_credits
        self.credits            = TreeMap()
        self.call_count         = TreeMap()
        self.total_calls        = u256(0)
        self.total_revenue      = u256(0)

    # ── READ ────────────────────────────────────────────────────────

    @gl.public.view
    def get_price_per_call(self) -> u256:
        return self.price_per_call_wei

    @gl.public.view
    def check_credits(self, user: Address) -> u256:
        """Return remaining credits for a user."""
        return self.credits.get(user, u256(0))

    @gl.public.view
    def get_call_count(self, user: Address) -> u256:
        """Return total calls made by a user."""
        return self.call_count.get(user, u256(0))

    @gl.public.view
    def get_stats(self) -> str:
        """Return global usage statistics."""
        return f'{{"total_calls": {self.total_calls}, "total_revenue_wei": {self.total_revenue}, "price_per_call_wei": {self.price_per_call_wei}}}'

    @gl.public.view
    def get_402_info(self) -> str:
        """x402-compatible payment info for new users."""
        return f'{{"price_per_call_wei": {self.price_per_call_wei}, "owner": "{self.owner}", "protocol": "x402-genlayer-metered"}}'

    # ── WRITE ───────────────────────────────────────────────────────

    @gl.public.write.payable
    def buy_credits(self) -> u256:
        """
        Buy credits by sending GEN.
        Credits purchased = floor(value_sent / price_per_call_wei)
        Remainder is accepted and credited to partial next call.
        Returns number of credits purchased.
        """
        sender = gl.message.sender_address
        value  = gl.message.value

        assert value >= self.price_per_call_wei, \
            f"x402: Minimum purchase is {self.price_per_call_wei} wei (1 credit)."

        credits_to_add = value // self.price_per_call_wei
        current        = self.credits.get(sender, u256(0))
        new_total      = current + credits_to_add

        assert new_total <= self.max_credits, \
            f"x402: Would exceed max credits ({self.max_credits}). Current: {current}."

        self.credits[sender]   = new_total
        self.total_revenue     = self.total_revenue + value
        return credits_to_add

    @gl.public.write
    def execute_query(self, query_param: str) -> str:
        """
        Execute one metered API call.
        Deducts 1 credit and fetches data from data_url + query_param.
        Returns fetched data or raises error if no credits.
        """
        sender  = gl.message.sender_address
        current = self.credits.get(sender, u256(0))

        assert current > u256(0), \
            f"x402: No credits remaining. Buy credits via buy_credits(). Price: {self.price_per_call_wei} wei/call."

        # Deduct credit before fetching (prevent re-entrancy style issues)
        self.credits[sender]  = current - u256(1)
        self.total_calls      = self.total_calls + u256(1)
        prev_count            = self.call_count.get(sender, u256(0))
        self.call_count[sender] = prev_count + u256(1)

        url = self.data_url + query_param

        def fetch() -> str:
            data = gl.get_webpage(url, mode="text")
            return gl.eq_principle_prompt_comparative(
                lambda: gl.exec_prompt(
                    f"Summarize this API response concisely: {data}"
                )
            )

        return fetch()

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        """Owner can update price per call."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_price > u256(0), "Price must be > 0"
        self.price_per_call_wei = new_price

    @gl.public.write
    def refund_credits(self, user: Address) -> None:
        """Owner can refund all credits for a user (for disputes)."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        remaining = self.credits.get(user, u256(0))
        if remaining > u256(0):
            refund_amount = remaining * self.price_per_call_wei
            self.credits[user] = u256(0)

            @gl.evm.contract_interface
            class _EOA:
                class View: pass
                class Write: pass
            _EOA(user).emit_transfer(value=refund_amount)

    @gl.public.write
    def withdraw(self, amount: u256) -> None:
        """Owner withdraws revenue."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert amount <= self.balance, "x402: Insufficient balance"

        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass
        _EOA(self.owner).emit_transfer(value=amount)
