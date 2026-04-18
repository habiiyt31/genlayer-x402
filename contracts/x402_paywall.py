# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class X402Paywall(gl.Contract):
    """
    genlayer-x402 :: Paywall Contract
    ===================================
    One-time payment gate. User pays once → permanent access.
    Implements the x402 HTTP Payment Required protocol pattern
    natively inside a GenLayer Intelligent Contract.

    Use case: paid API endpoint, premium data feed, gated content.

    x402 Flow:
        1. Client calls get_protected_data() without paying
           → Contract returns 402-style error with price info
        2. Client calls pay_for_access() with required GEN value
           → Contract records payment, unlocks access
        3. Client calls get_protected_data() again
           → Contract fetches real-time data and returns it

    Args (constructor):
        price_wei (u256): Access price in wei (1 GEN = 10^18 wei)
        data_url  (str):  URL the contract will fetch for paying users
    """

    price_wei: u256
    owner:     Address
    data_url:  str
    payments:  TreeMap[Address, u256]   # addr → total paid
    total_revenue: u256

    def __init__(self, price_wei: u256, data_url: str):
        assert price_wei > u256(0), "Price must be greater than zero"
        self.price_wei     = price_wei
        self.owner         = gl.message.sender_address
        self.data_url      = data_url
        self.payments      = TreeMap()
        self.total_revenue = u256(0)

    # ── READ ────────────────────────────────────────────────────────

    @gl.public.view
    def get_price(self) -> u256:
        """Return access price in wei."""
        return self.price_wei

    @gl.public.view
    def get_owner(self) -> Address:
        return self.owner

    @gl.public.view
    def get_total_revenue(self) -> u256:
        return self.total_revenue

    @gl.public.view
    def has_access(self, user: Address) -> bool:
        """Check if a user has paid enough for access."""
        return self.payments.get(user, u256(0)) >= self.price_wei

    @gl.public.view
    def get_payment(self, user: Address) -> u256:
        """Return total amount a user has paid."""
        return self.payments.get(user, u256(0))

    @gl.public.view
    def get_402_info(self) -> str:
        """
        Returns x402-compatible payment info.
        Clients that receive a 402 error call this to learn
        how much to pay and where.
        """
        return f'{{"price_wei": {self.price_wei}, "owner": "{self.owner}", "protocol": "x402-genlayer"}}'

    # ── WRITE ───────────────────────────────────────────────────────

    @gl.public.write.payable
    def pay_for_access(self) -> None:
        """
        Send GEN to purchase access.
        gl.message.value must be >= price_wei.
        Excess is accepted and recorded (no change returned).
        """
        sender = gl.message.sender_address
        value  = gl.message.value

        assert value >= self.price_wei, \
            f"x402: Insufficient payment. Required {self.price_wei} wei, got {value} wei."

        current = self.payments.get(sender, u256(0))
        self.payments[sender] = current + value
        self.total_revenue    = self.total_revenue + value

    @gl.public.view
    def get_protected_data(self, user: Address) -> str:
        """
        Fetch and return real-time data from data_url.
        Access is gated: user must have called pay_for_access() first.
        Uses gl.get_webpage() — GenLayer's native web access.
        """
        assert self.has_access(user), \
            f"x402: Payment required. Price: {self.price_wei} wei. Call pay_for_access() first."

        def fetch() -> str:
            raw = gl.get_webpage(self.data_url, mode="text")
            return raw

        return gl.eq_principle_strict_eq(fetch)

    @gl.public.write
    def update_price(self, new_price: u256) -> None:
        """Owner can update the access price."""
        assert gl.message.sender_address == self.owner, "x402: Only owner can update price"
        assert new_price > u256(0), "Price must be greater than zero"
        self.price_wei = new_price

    @gl.public.write
    def update_data_url(self, new_url: str) -> None:
        """Owner can update the data URL."""
        assert gl.message.sender_address == self.owner, "x402: Only owner can update URL"
        assert len(new_url) > 0, "URL cannot be empty"
        self.data_url = new_url

    @gl.public.write
    def withdraw(self, amount: u256) -> None:
        """
        Owner withdraws accumulated revenue from the contract.
        Sends GEN to owner's EOA address.
        """
        assert gl.message.sender_address == self.owner, "x402: Only owner can withdraw"
        assert amount <= self.balance, "x402: Insufficient contract balance"

        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass

        _EOA(self.owner).emit_transfer(value=amount)
