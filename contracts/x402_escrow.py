# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing


class X402Escrow(gl.Contract):
    """
    X402 Escrow — AI-verified freelance payment escrow.

    Workflow:
      1. Client deploys contract with brief
      2. Client calls fund() with freelancer address + GEN payment
      3. Freelancer calls submit_work() with deliverable URL
      4. GenLayer LLM validators evaluate if work meets brief
      5. If approved, client releases payment to freelancer
      6. If disputed, client can manually approve or cancel

    This combines x402 payment protocol with GenLayer's
    unique AI consensus capability.

    State flow:
      OPEN -> FUNDED -> SUBMITTED -> APPROVED/DISPUTED -> RESOLVED
    """

    brief: str
    client: Address
    freelancer: Address
    amount: u256
    state: str
    work_url: str
    work_description: str
    ai_verdict: str

    def __init__(self, brief: str):
        """
        Initialize escrow contract.

        Args:
            brief (str): Acceptance criteria for the work (min 20 chars)
        """
        assert len(brief) >= 20, "Brief must be at least 20 characters"

        self.brief = brief
        self.client = gl.message.sender_address
        self.freelancer = Address("0x0000000000000000000000000000000000000000")
        self.amount = u256(0)
        self.state = "OPEN"
        self.work_url = ""
        self.work_description = ""
        self.ai_verdict = ""

    # ── VIEW METHODS ──────────────────────────────────────────────

    @gl.public.view
    def get_state(self) -> str:
        return self.state

    @gl.public.view
    def get_brief(self) -> str:
        return self.brief

    @gl.public.view
    def get_amount(self) -> u256:
        return self.amount

    @gl.public.view
    def get_client(self) -> str:
        return self.client.as_hex

    @gl.public.view
    def get_freelancer(self) -> str:
        return self.freelancer.as_hex

    @gl.public.view
    def get_work_url(self) -> str:
        return self.work_url

    @gl.public.view
    def get_ai_verdict(self) -> str:
        return self.ai_verdict

    @gl.public.view
    def get_summary(self) -> str:
        return (
            '{"state": "' + self.state +
            '", "client": "' + self.client.as_hex +
            '", "freelancer": "' + self.freelancer.as_hex +
            '", "amount_wei": ' + str(self.amount) +
            ', "work_url": "' + self.work_url +
            '"}'
        )

    # ── WRITE METHODS ─────────────────────────────────────────────

    @gl.public.write.payable
    def fund(self, freelancer_addr: Address) -> None:
        """
        Client funds the escrow and assigns a freelancer.
        Must be called by the contract creator (client).
        """
        assert gl.message.sender_address == self.client, \
            "x402: Only client can fund"
        assert self.state == "OPEN", \
            "x402: Escrow not in OPEN state"
        assert gl.message.value > u256(0), \
            "x402: Must send value to fund escrow"

        self.freelancer = freelancer_addr
        self.amount = gl.message.value
        self.state = "FUNDED"

    @gl.public.write
    def submit_work(self, work_url: str, work_description: str) -> typing.Any:
        """
        Freelancer submits completed work URL and description.
        Triggers AI evaluation via GenLayer LLM validators.
        Returns the AI verdict and updates state.
        """
        assert gl.message.sender_address == self.freelancer, \
            "x402: Only freelancer can submit"
        assert self.state == "FUNDED", \
            "x402: Escrow must be in FUNDED state"
        assert len(work_url) > 0, "Work URL required"

        self.work_url = work_url
        self.work_description = work_description
        self.state = "SUBMITTED"

        def nondet() -> str:
            response = gl.nondet.web.get(self.work_url)
            work_content = response.body.decode("utf-8")

            # Truncate for LLM context
            if len(work_content) > 2500:
                work_content = work_content[:2500]

            task = (
                "You are evaluating freelance work for an escrow contract.\n\n"
                "CLIENT BRIEF (acceptance criteria):\n" +
                self.brief + "\n\n"
                "FREELANCER DESCRIPTION:\n" +
                self.work_description + "\n\n"
                "SUBMITTED WORK CONTENT (fetched from URL):\n" +
                work_content + "\n\n"
                "Does the work fulfill the client brief? "
                "Be objective and fair to both parties.\n"
                "Respond with ONLY 'APPROVED' or 'DISPUTED' as the first word, "
                "followed by a single-sentence reason on the same line."
            )
            return gl.nondet.exec_prompt(task)

        verdict = gl.eq_principle.prompt_comparative(
            nondet,
            "The verdicts must reach the same APPROVED or DISPUTED conclusion"
        )

        self.ai_verdict = verdict

        if verdict.strip().startswith("APPROVED"):
            self.state = "APPROVED"
        else:
            self.state = "DISPUTED"

        return verdict

    @gl.public.write
    def release_payment(self) -> None:
        """
        Release payment to freelancer. Works when state == APPROVED.
        Either client or freelancer can trigger this.
        """
        assert self.state == "APPROVED", \
            "x402: Work not approved. Current state: " + self.state

        self.state = "RESOLVED"

        # Transfer GEN to freelancer using EOA interface
        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass

        _EOA(self.freelancer).emit_transfer(value=self.amount)

    @gl.public.write
    def client_approve(self) -> None:
        """
        Client can override AI verdict and manually approve.
        Useful for edge cases where AI is wrong.
        """
        assert gl.message.sender_address == self.client, \
            "x402: Only client can approve manually"
        assert self.state == "SUBMITTED" or self.state == "DISPUTED", \
            "x402: Cannot approve in state " + self.state

        self.state = "APPROVED"
        self.ai_verdict = self.ai_verdict + " [MANUALLY APPROVED BY CLIENT]"

    @gl.public.write
    def client_cancel(self) -> None:
        """
        Client cancels and reclaims funds.
        Only available if state is FUNDED (freelancer hasn't submitted yet).
        """
        assert gl.message.sender_address == self.client, \
            "x402: Only client can cancel"
        assert self.state == "FUNDED", \
            "x402: Can only cancel from FUNDED state. Current: " + self.state

        refund_amount = self.amount
        self.state = "RESOLVED"

        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass

        _EOA(self.client).emit_transfer(value=refund_amount)