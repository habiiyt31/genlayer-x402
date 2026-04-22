# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing


class X402Paywall(gl.Contract):
    """
    X402 Paywall — One-time payment gate for web data.

    User pays once in GEN → permanent access to protected data.
    Access is stored as an explicit flag at purchase time,
    so price updates do NOT revoke existing buyers.

    Owner can withdraw accumulated revenue via withdraw().
    """

    price_wei: u256
    owner: Address
    data_url: str
    # Explicit access flag — stored as u256 (0 = no access, 1 = granted).
    # Using u256 instead of bool for reliable TreeMap default handling.
    access_granted: TreeMap[Address, u256]
    total_paid: TreeMap[Address, u256]
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
    def get_contract_balance(self) -> u256:
        """Current GEN balance held by the contract."""
        return self.balance

    @gl.public.view
    def has_access(self, user_address: str) -> bool:
        """
        Check if user has been granted access.
        Takes string hex address, converts to Address internally.
        Returns True if flag is set to 1 (paid), False otherwise.
        """
        user = Address(user_address)
        return self.access_granted.get(user, u256(0)) > u256(0)

    @gl.public.view
    def get_payment(self, user_address: str) -> u256:
        """Total amount a user has paid (historical sum)."""
        user = Address(user_address)
        return self.total_paid.get(user, u256(0))

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
        Access is granted via explicit flag — future price changes
        do NOT affect users who already paid.
        """
        sender = gl.message.sender_address
        value = gl.message.value

        assert value >= self.price_wei, \
            "x402: Insufficient payment. Required " + str(self.price_wei) + " wei."

        # Set explicit access flag to 1 (granted).
        self.access_granted[sender] = u256(1)

        # Record payment history
        prev = self.total_paid.get(sender, u256(0))
        self.total_paid[sender] = prev + value
        self.total_revenue = self.total_revenue + value

    @gl.public.write
    def get_protected_data(self) -> typing.Any:
        """
        Fetch and return data from data_url.
        Requires access flag > 0.
        """
        sender = gl.message.sender_address
        flag = self.access_granted.get(sender, u256(0))
        assert flag > u256(0), \
            "x402: Payment required. Call pay_for_access() first."

        def nondet() -> str:
            response = gl.nondet.web.get(self.data_url)
            return response.body.decode("utf-8")

        return gl.eq_principle.strict_eq(nondet)

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        """
        Owner can update price for FUTURE buyers.
        Does NOT revoke existing access_granted flags.
        """
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert new_price > u256(0), "Price must be > 0"
        self.price_wei = new_price

    @gl.public.write
    def update_data_url(self, new_url: str) -> None:
        """Owner can update data URL."""
        assert gl.message.sender_address == self.owner, "x402: Only owner"
        assert len(new_url) > 0, "URL cannot be empty"
        self.data_url = new_url

    @gl.public.write
    def withdraw(self, amount: u256) -> None:
        """
        Owner withdraws accumulated revenue from contract balance.
        Transfers GEN to the owner's EOA address.
        """
        assert gl.message.sender_address == self.owner, "x402: Only owner can withdraw"
        assert amount > u256(0), "Amount must be > 0"
        assert amount <= self.balance, \
            "x402: Insufficient contract balance. Available: " + str(self.balance)

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
        