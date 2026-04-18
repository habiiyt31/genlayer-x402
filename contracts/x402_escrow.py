# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

class X402Escrow(gl.Contract):
    """
    genlayer-x402 :: AI-Verified Escrow Contract
    ==============================================
    Escrow with AI-powered delivery verification.
    Client deposits GEN. Freelancer delivers work.
    GenLayer LLM validators judge if work meets the brief.
    Payment released automatically on approval.

    This is the bridge between x402 payment protocol and
    GenLayer's unique AI consensus capability — no human
    arbitrator needed.

    Use case: freelance work, content delivery,
              software milestone payments.

    States: OPEN → FUNDED → SUBMITTED → APPROVED/DISPUTED → RESOLVED

    Args (constructor):
        brief       (str):  Work description / acceptance criteria
        deadline_blocks (u256): Deadline in blocks from creation
    """

    # -- Storage types must use TreeMap/DynArray per GenLayer docs --
    brief:            str
    client:           Address
    freelancer:       Address
    amount:           u256
    deadline_block:   u256
    state:            str        # OPEN|FUNDED|SUBMITTED|APPROVED|DISPUTED|RESOLVED
    work_url:         str
    work_description: str
    ai_verdict:       str
    ai_score:         u256       # 0-100

    def __init__(self, brief: str, deadline_blocks: u256):
        assert len(brief) >= 20, "Brief must be at least 20 characters"
        assert deadline_blocks > u256(0), "Deadline must be > 0"

        self.brief            = brief
        self.client           = gl.message.sender_address
        self.freelancer       = Address("0x0000000000000000000000000000000000000000")
        self.amount           = u256(0)
        self.deadline_block   = gl.block.number + deadline_blocks
        self.state            = "OPEN"
        self.work_url         = ""
        self.work_description = ""
        self.ai_verdict       = ""
        self.ai_score         = u256(0)

    # ── READ ────────────────────────────────────────────────────────

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
    def get_deadline(self) -> u256:
        return self.deadline_block

    @gl.public.view
    def get_summary(self) -> str:
        return (
            f'{{"state": "{self.state}", '
            f'"client": "{self.client}", '
            f'"freelancer": "{self.freelancer}", '
            f'"amount_wei": {self.amount}, '
            f'"deadline_block": {self.deadline_block}, '
            f'"ai_score": {self.ai_score}, '
            f'"ai_verdict": "{self.ai_verdict}"}}'
        )

    @gl.public.view
    def get_402_info(self) -> str:
        """x402-compatible payment info for client funding."""
        return (
            f'{{"required_amount_wei": "{self.amount}", '
            f'"state": "{self.state}", '
            f'"client": "{self.client}", '
            f'"protocol": "x402-genlayer-escrow"}}'
        )

    # ── WRITE ───────────────────────────────────────────────────────

    @gl.public.write.payable
    def fund(self, freelancer_addr: Address) -> None:
        """
        Client funds the escrow and assigns a freelancer.
        Must be called by the client (contract creator).
        value = payment amount for the job.
        """
        assert gl.message.sender_address == self.client, "x402: Only client can fund"
        assert self.state == "OPEN",                      "x402: Escrow not in OPEN state"
        assert gl.message.value > u256(0),                "x402: Must send value to fund escrow"
        assert gl.block.number < self.deadline_block,     "x402: Deadline already passed"

        self.freelancer = freelancer_addr
        self.amount     = gl.message.value
        self.state      = "FUNDED"

    @gl.public.write
    def submit_work(self, work_url: str, work_description: str) -> None:
        """
        Freelancer submits completed work URL + description.
        Triggers AI evaluation via GenLayer LLM validators.
        """
        assert gl.message.sender_address == self.freelancer, "x402: Only freelancer can submit"
        assert self.state == "FUNDED",                        "x402: Escrow not funded"
        assert gl.block.number < self.deadline_block,         "x402: Deadline passed"
        assert len(work_url) > 0,                             "x402: Work URL required"

        self.work_url         = work_url
        self.work_description = work_description
        self.state            = "SUBMITTED"

        # AI Evaluation using GenLayer's non-deterministic LLM call
        def evaluate() -> str:
            # Fetch the submitted work from URL
            work_content = gl.get_webpage(work_url, mode="text")

            verdict_json = gl.exec_prompt(
                f"""You are an impartial work evaluator for a freelance escrow.

CLIENT BRIEF (acceptance criteria):
{self.brief}

SUBMITTED WORK DESCRIPTION:
{work_description}

SUBMITTED WORK CONTENT (fetched from URL):
{work_content[:3000]}

Evaluate whether the submitted work fulfills the client brief.
Be objective and fair to both parties.

Respond ONLY with valid JSON, no other text:
{{
  "approved": true or false,
  "score": <integer 0-100>,
  "reason": "<one sentence explanation>",
  "missing": "<what is missing if not approved, or 'nothing' if approved>"
}}"""
            )
            return verdict_json

        raw_verdict = gl.eq_principle_prompt_comparative(evaluate)
        self.ai_verdict = raw_verdict

        # Parse score from verdict (simple extraction)
        if '"approved": true' in raw_verdict or '"approved":true' in raw_verdict:
            self.state    = "APPROVED"
            self.ai_score = u256(90)  # approved
        else:
            self.state    = "DISPUTED"
            self.ai_score = u256(30)  # needs review

    @gl.public.write
    def release_payment(self) -> None:
        """
        Release payment to freelancer if work is APPROVED.
        Can be called by client (manual approval) or
        automatically triggered when state is APPROVED.
        """
        assert self.state == "APPROVED", \
            f"x402: Work not approved. Current state: {self.state}. AI verdict: {self.ai_verdict}"

        self.state = "RESOLVED"

        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass
        _EOA(self.freelancer).emit_transfer(value=self.amount)

    @gl.public.write
    def client_approve(self) -> None:
        """
        Client can manually approve disputed work.
        Override for edge cases where AI verdict is challenged.
        """
        assert gl.message.sender_address == self.client, "x402: Only client"
        assert self.state in ["SUBMITTED", "DISPUTED"],  "x402: Cannot approve in current state"

        self.state    = "APPROVED"
        self.ai_verdict = self.ai_verdict + " [MANUALLY APPROVED BY CLIENT]"

    @gl.public.write
    def client_reject_and_refund(self) -> None:
        """
        Client can reject work and reclaim funds.
        Only available if deadline has passed without approval.
        """
        assert gl.message.sender_address == self.client,    "x402: Only client"
        assert gl.block.number > self.deadline_block,        "x402: Deadline not yet passed"
        assert self.state not in ["APPROVED", "RESOLVED"],   "x402: Already resolved"

        self.state = "RESOLVED"

        @gl.evm.contract_interface
        class _EOA:
            class View: pass
            class Write: pass
        _EOA(self.client).emit_transfer(value=self.amount)
