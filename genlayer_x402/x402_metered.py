# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import genlayer as gl

import typing


class X402Metered(gl.Contract):
    """
    X402 Metered — Credit-based per-call billing.

    Users buy credits with GEN. Each API call deducts 1 credit.
    When credits run out, user must top up to continue.
    Owner can withdraw accumulated revenue via withdraw().
    """

    price_per_call_wei: u256
    owner: Address
    data_url_prefix: str
    max_credits: u256
    credits: TreeMap[Address, u256]
    call_count: TreeMap[Address, u256]
    total_calls: u256
    total_revenue: u256

    def __init__(
        self,
        price_per_call_wei: u256,
        data_url_prefix: str,
        max_credits: u256,
    ):
        """
        Initialize metered billing contract.

        Args:
            price_per_call_wei (u256): Cost per single API call
            data_url_prefix    (str):  URL prefix (query param appended)
            max_credits        (u256): Max credits any user can accumulate
        """
        assert price_per_call_wei > u256(0), "Price must be > 0"
        assert max_credits > u256(0), "Max credits must be > 0"

        self.price_per_call_wei = price_per_call_wei
        self.owner = gl.message.sender_address
        self.data_url_prefix = data_url_prefix
        self.max_credits = max_credits
        self.total_calls = u256(0)
        self.total_revenue = u256(0)

    # ── VIEW METHODS ──────────────────────────────────────────────

    @gl.public.view
    def get_price_per_call(self) -> u256:
        return self.price_per_call_wei

    @gl.public.view
    def get_max_credits(self) -> u256:
        return self.max_credits

    @gl.public.view
    def check_credits(self, user_address: str) -> u256:
        user = Address(user_address)
        return self.credits.get(user, u256(0))

    @gl.public.view
    def get_call_count(self, user_address: str) -> u256:
        user = Address(user_address)
        return self.call_count.get(user, u256(0))

    @gl.public.view
    def get_total_calls(self) -> u256:
        return self.total_calls

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
            '{"price_per_call_wei": ' + str(self.price_per_call_wei) +
            ', "max_credits": ' + str(self.max_credits) +
            ', "owner": "' + self.owner.as_hex +
            '", "protocol": "x402-genlayer", "type": "metered"}'
        )

    # ── WRITE METHODS ─────────────────────────────────────────────

    @gl.public.write.payable
    def buy_credits(self) -> None:
        """
        Purchase credits by sending GEN.
        Credits = floor(value / price_per_call_wei).
        """
        sender = gl.message.sender_address
        value = gl.message.value

        assert value >= self.price_per_call_wei, \
            "x402: Minimum is " + str(self.price_per_call_wei) + " wei (1 credit)"

        credits_to_add = value // self.price_per_call_wei
        current = self.credits.get(sender, u256(0))
        new_total = current + credits_to_add

        assert new_total <= self.max_credits, \
            "x402: Would exceed max credits (" + str(self.max_credits) + ")"

        self.credits[sender] = new_total
        self.total_revenue = self.total_revenue + value

    @gl.public.write
    def execute_query(self, query_param: str) -> typing.Any:
        """
        Execute one metered query. Deducts 1 credit.
        Returns AI-summarized data from external URL.
        """
        sender = gl.message.sender_address
        current = self.credits.get(sender, u256(0))

        assert current > u256(0), \
            "x402: No credits. Buy via buy_credits(). Price: " + str(self.price_per_call_wei) + " wei/call"

        # Deduct credit BEFORE external call
        self.credits[sender] = current - u256(1)
        self.total_calls = self.total_calls + u256(1)
        prev = self.call_count.get(sender, u256(0))
        self.call_count[sender] = prev + u256(1)

        def nondet() -> str:
            url = self.data_url_prefix + query_param
            response = gl.nondet.web.get(url)
            raw_data = response.body.decode("utf-8")

            truncated = raw_data[:2000] if len(raw_data) > 2000 else raw_data

            prompt = (
                "Summarize this API response in 2-3 sentences. "
                "Focus on the key data points only.\n\n"
                "Response:\n" + truncated
            )
            return gl.nondet.exec_prompt(prompt)

        return gl.eq_principle.prompt_comparative(
            nondet,
            "The summaries should convey the same key information"
        )

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_price > u256(0), "Price must be > 0"
        self.price_per_call_wei = new_price

    @gl.public.write
    def update_url_prefix(self, new_url: str) -> None:
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        self.data_url_prefix = new_url

    @gl.public.write
    def grant_credits(self, user_address: str, amount: u256) -> None:
        """Owner can grant free credits (promo/testing)."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        user = Address(user_address)
        current = self.credits.get(user, u256(0))
        new_total = current + amount
        assert new_total <= self.max_credits, "x402: Would exceed max"
        self.credits[user] = new_total

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
