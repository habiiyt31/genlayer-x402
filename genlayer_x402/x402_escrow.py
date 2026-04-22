# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing


class X402Escrow(gl.Contract):
    """
    X402 Escrow — AI-verified freelance payment escrow.

    Workflow:
      1. Client deploys with structured brief + dispute parameters
      2. Client calls fund() with freelancer address + GEN payment
      3. Freelancer calls submit_work() with deliverable URL
      4. GenLayer LLM validators evaluate if work meets brief
      5. If APPROVED, anyone can release_payment() to freelancer
      6. If DISPUTED:
         a) Client calls client_approve() to override, or
         b) Arbiter calls arbiter_rule() to resolve, or
         c) After N claim attempts, freelancer can force_release()

    State flow:
      OPEN -> FUNDED -> SUBMITTED -> APPROVED/DISPUTED -> RESOLVED
    """

    brief_title: str
    brief_description: str
    brief_acceptance_criteria: str
    brief_deliverable_format: str

    client: Address
    freelancer: Address
    arbiter: Address
    amount: u256
    state: str

    work_url: str
    work_description: str
    ai_verdict: str

    max_claim_attempts: u256
    claim_attempts: u256

    def __init__(
        self,
        brief_title: str,
        brief_description: str,
        brief_acceptance_criteria: str,
        brief_deliverable_format: str,
        arbiter_addr: str,
        max_claim_attempts: u256,
    ):
        """
        Initialize escrow with structured brief.

        Args:
            brief_title              (str):  Short work title (≥ 10 chars)
            brief_description        (str):  Detailed description (≥ 80 chars)
            brief_acceptance_criteria (str): Measurable criteria (≥ 80 chars)
            brief_deliverable_format  (str): Expected output format (≥ 30 chars)
            arbiter_addr             (str):  Hex address of neutral arbiter
            max_claim_attempts       (u256): Attempts before force_release unlocks

        Total brief content must be ≥ 200 characters.
        """
        assert len(brief_title) >= 10, \
            "Brief title must be at least 10 characters"
        assert len(brief_description) >= 80, \
            "Brief description must be at least 80 characters"
        assert len(brief_acceptance_criteria) >= 80, \
            "Acceptance criteria must be at least 80 characters"
        assert len(brief_deliverable_format) >= 30, \
            "Deliverable format must be at least 30 characters"

        total_len = (
            len(brief_title) +
            len(brief_description) +
            len(brief_acceptance_criteria) +
            len(brief_deliverable_format)
        )
        assert total_len >= 200, \
            "Total brief content must be at least 200 characters"

        assert max_claim_attempts >= u256(3), \
            "Max claim attempts must be at least 3"

        self.brief_title = brief_title
        self.brief_description = brief_description
        self.brief_acceptance_criteria = brief_acceptance_criteria
        self.brief_deliverable_format = brief_deliverable_format
        self.client = gl.message.sender_address
        self.freelancer = Address("0x0000000000000000000000000000000000000000")
        self.arbiter = Address(arbiter_addr)
        self.amount = u256(0)
        self.state = "OPEN"
        self.work_url = ""
        self.work_description = ""
        self.ai_verdict = ""
        self.max_claim_attempts = max_claim_attempts
        self.claim_attempts = u256(0)

    # ── VIEW METHODS ──────────────────────────────────────────────

    @gl.public.view
    def get_state(self) -> str:
        return self.state

    @gl.public.view
    def get_brief(self) -> str:
        return (
            '{"title": "' + self.brief_title.replace('"', "'") +
            '", "description": "' + self.brief_description.replace('"', "'") +
            '", "acceptance_criteria": "' + self.brief_acceptance_criteria.replace('"', "'") +
            '", "deliverable_format": "' + self.brief_deliverable_format.replace('"', "'") +
            '"}'
        )

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
    def get_arbiter(self) -> str:
        return self.arbiter.as_hex

    @gl.public.view
    def get_work_url(self) -> str:
        return self.work_url

    @gl.public.view
    def get_ai_verdict(self) -> str:
        return self.ai_verdict

    @gl.public.view
    def get_claim_attempts(self) -> u256:
        return self.claim_attempts

    @gl.public.view
    def get_max_claim_attempts(self) -> u256:
        return self.max_claim_attempts

    @gl.public.view
    def get_summary(self) -> str:
        return (
            '{"state": "' + self.state +
            '", "client": "' + self.client.as_hex +
            '", "freelancer": "' + self.freelancer.as_hex +
            '", "arbiter": "' + self.arbiter.as_hex +
            '", "amount_wei": ' + str(self.amount) +
            ', "work_url": "' + self.work_url +
            '", "claim_attempts": ' + str(self.claim_attempts) +
            ', "max_claim_attempts": ' + str(self.max_claim_attempts) +
            '}'
        )

    # ── WRITE METHODS ─────────────────────────────────────────────

    @gl.public.write.payable
    def fund(self, freelancer_address: str) -> None:
        """Client funds the escrow and assigns a freelancer."""
        assert gl.message.sender_address == self.client, \
            "x402: Only client can fund"
        assert self.state == "OPEN", \
            "x402: Escrow not in OPEN state"
        assert gl.message.value > u256(0), \
            "x402: Must send value to fund escrow"

        self.freelancer = Address(freelancer_address)
        self.amount = gl.message.value
        self.state = "FUNDED"

    @gl.public.write
    def submit_work(self, work_url: str, work_description: str) -> typing.Any:
        """
        Freelancer submits completed work.
        Triggers AI evaluation via GenLayer LLM validators.
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

            if len(work_content) > 2500:
                work_content = work_content[:2500]

            task = (
                "You are evaluating freelance work for an escrow contract.\n\n"
                "=== BRIEF ===\n"
                "Title: " + self.brief_title + "\n"
                "Description: " + self.brief_description + "\n"
                "Acceptance Criteria: " + self.brief_acceptance_criteria + "\n"
                "Deliverable Format: " + self.brief_deliverable_format + "\n\n"
                "=== SUBMISSION ===\n"
                "Freelancer description: " + self.work_description + "\n"
                "Work content (fetched from URL):\n" + work_content + "\n\n"
                "=== YOUR TASK ===\n"
                "Does the submitted work meet ALL acceptance criteria?\n"
                "Be strict and objective.\n"
                "Respond with ONLY 'APPROVED' or 'DISPUTED' as the first word, "
                "followed by a single-sentence reason."
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
        """Release payment to freelancer. Works when state == APPROVED."""
        assert self.state == "APPROVED", \
            "x402: Work not approved. Current state: " + self.state

        self.state = "RESOLVED"

        @gl.evm.contract_interface
        class _EOA:
            class View:
                pass
            class Write:
                pass

        _EOA(self.freelancer).emit_transfer(value=self.amount)

    @gl.public.write
    def client_approve(self) -> None:
        """Client can override AI verdict and manually approve."""
        assert gl.message.sender_address == self.client, \
            "x402: Only client can approve manually"
        assert self.state == "SUBMITTED" or self.state == "DISPUTED", \
            "x402: Cannot approve in state " + self.state

        self.state = "APPROVED"
        self.ai_verdict = self.ai_verdict + " [MANUALLY APPROVED BY CLIENT]"

    @gl.public.write
    def client_cancel(self) -> None:
        """Client cancels and reclaims funds (only if still FUNDED)."""
        assert gl.message.sender_address == self.client, \
            "x402: Only client can cancel"
        assert self.state == "FUNDED", \
            "x402: Can only cancel from FUNDED state. Current: " + self.state

        refund_amount = self.amount
        self.state = "RESOLVED"

        @gl.evm.contract_interface
        class _EOA:
            class View:
                pass
            class Write:
                pass

        _EOA(self.client).emit_transfer(value=refund_amount)

    @gl.public.write
    def arbiter_rule(self, approve: bool) -> None:
        """
        Arbiter resolves a dispute.
        approve=True: release to freelancer
        approve=False: refund to client
        """
        assert gl.message.sender_address == self.arbiter, \
            "x402: Only arbiter can rule on disputes"
        assert self.state == "DISPUTED", \
            "x402: Arbiter only rules in DISPUTED state. Current: " + self.state

        self.ai_verdict = self.ai_verdict + " [ARBITER RULED]"
        self.state = "RESOLVED"

        @gl.evm.contract_interface
        class _EOA:
            class View:
                pass
            class Write:
                pass

        if approve:
            _EOA(self.freelancer).emit_transfer(value=self.amount)
        else:
            _EOA(self.client).emit_transfer(value=self.amount)

    @gl.public.write
    def freelancer_claim_attempt(self) -> None:
        """
        Freelancer logs a claim attempt when state is DISPUTED.
        After max_claim_attempts, freelancer can call force_release().
        """
        assert gl.message.sender_address == self.freelancer, \
            "x402: Only freelancer can log claim attempts"
        assert self.state == "DISPUTED", \
            "x402: Claim attempts only in DISPUTED state"

        self.claim_attempts = self.claim_attempts + u256(1)

    @gl.public.write
    def force_release(self) -> None:
        """
        Freelancer force-releases payment after max_claim_attempts.
        Safety valve to prevent permanent fund lockup.
        """
        assert gl.message.sender_address == self.freelancer, \
            "x402: Only freelancer can force-release"
        assert self.state == "DISPUTED", \
            "x402: Force-release only in DISPUTED state. Current: " + self.state
        assert self.claim_attempts >= self.max_claim_attempts, \
            "x402: Not enough claim attempts. Current: " + str(self.claim_attempts) + \
            ", required: " + str(self.max_claim_attempts)

        self.state = "RESOLVED"
        self.ai_verdict = self.ai_verdict + " [FORCE-RELEASED AFTER TIMEOUT]"

        @gl.evm.contract_interface
        class _EOA:
            class View:
                pass
            class Write:
                pass

        _EOA(self.freelancer).emit_transfer(value=self.amount)