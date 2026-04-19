# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing


class X402Paywall(gl.Contract):
    """
    X402 Paywall — One-time payment gate for web data.

    User pays once in GEN → permanent access to protected data
    fetched live from an external URL using GenLayer web access.

    This implements the HTTP 402 Payment Required pattern on-chain.
    """

    price_wei: u256
    owner: Address
    data_url: str
    payments: TreeMap[Address, u256]
    total_revenue: u256

    def __init__(self, price_wei: u256, data_url: str):
        """
        Initialize paywall contract.

        Args:
            price_wei (u256): Price for permanent access in wei
            data_url  (str):  URL to fetch for paying users
        """
        assert price_wei > u256(0), "Price must be greater than zero"
        assert len(data_url) > 0, "Data URL cannot be empty"

        self.price_wei = price_wei
        self.owner = gl.message.sender_address
        self.data_url = data_url
        self.total_revenue = u256(0)

    # ── VIEW METHODS ──────────────────────────────────────────────

    @gl.public.view
    def get_price(self) -> u256:
        return self.price_wei

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner.as_hex

    @gl.public.view
    def get_data_url(self) -> str:
        return self.data_url

    @gl.public.view
    def get_total_revenue(self) -> u256:
        return self.total_revenue

    @gl.public.view
    def has_access(self, user: Address) -> bool:
        paid = self.payments.get(user, u256(0))
        return paid >= self.price_wei

    @gl.public.view
    def get_payment(self, user: Address) -> u256:
        return self.payments.get(user, u256(0))

    @gl.public.view
    def get_402_info(self) -> str:
        """x402-compatible payment info for clients."""
        return (
            '{"price_wei": ' + str(self.price_wei) +
            ', "owner": "' + self.owner.as_hex +
            '", "protocol": "x402-genlayer", "type": "paywall"}'
        )

    # ── WRITE METHODS ─────────────────────────────────────────────

    @gl.public.write.payable
    def pay_for_access(self) -> None:
        """
        User sends GEN to purchase permanent access.
        gl.message.value must be >= price_wei.
        """
        sender = gl.message.sender_address
        value = gl.message.value

        assert value >= self.price_wei, \
            "x402: Insufficient payment. Required " + str(self.price_wei) + " wei."

        current = self.payments.get(sender, u256(0))
        self.payments[sender] = current + value
        self.total_revenue = self.total_revenue + value

    @gl.public.write
    def get_protected_data(self) -> typing.Any:
        """
        Fetch and return data from data_url.
        Requires payment from the caller first.
        Uses Equivalence Principle for validator consensus.
        """
        sender = gl.message.sender_address
        assert self.has_access(sender), \
            "x402: Payment required. Call pay_for_access() first."

        def nondet() -> str:
            response = gl.nondet.web.get(self.data_url)
            return response.body.decode("utf-8")

        return gl.eq_principle.strict_eq(nondet)

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        """Owner can update price (does not affect existing buyers)."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_price > u256(0), "Price must be > 0"
        self.price_wei = new_price

    @gl.public.write
    def update_data_url(self, new_url: str) -> None:
        """Owner can update data URL."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert len(new_url) > 0, "URL cannot be empty"
        self.data_url = new_url