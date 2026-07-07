"""Governance queue tools — the propose -> approve -> execute spine.

This is the heart of the governance model. The agent PROPOSES; the operator disposes. `propose` is
the DEFAULT for anything impactful that should be reviewed before it runs. The approve/reject/execute
tools are HUMAN-AUTHORIZED ONLY (operator-token gated) — never call them unless the operator
explicitly says so, and never approve your own proposal.
"""

from .. import client
from . import ora_tool

_ACTOR = "mcp-client"


def register_queue_tools(server):

    @server.tool()
    @ora_tool
    def propose(objective: str, recommendation: str = "", lane: str = "note",
                confidence: int = 0, evidence_tier: str = "", payload: "dict | None" = None) -> str:
        """Put a proposed action into the governed operator QUEUE instead of doing it. The kernel
        evaluates it (confidence/evidence -> blocked / approval_required / auto_eligible) and it waits
        for the operator's approval. Use this for ANYTHING that should be reviewed before it runs:
        deliverables, outreach, external sends, deploys, spends. Nothing executes until it's approved.

        Args:
            objective: what the action accomplishes (required).
            recommendation: the recommended action / summary.
            lane: producer lane — note | html | pdf | doc | site (default note).
            confidence: 0-100 confidence in this proposal.
            evidence_tier: tier_1 | tier_2 | tier_3.
            payload: lane content, e.g. {"title": ..., "body": ...}.
        """
        body: dict = {"objective": objective, "actor": _ACTOR}
        if recommendation:
            body["recommendation"] = recommendation
        if lane:
            body["lane"] = lane
        if confidence:
            body["confidence"] = int(confidence)
        if evidence_tier:
            body["evidence_tier"] = evidence_tier
        if payload:
            body["payload"] = payload
        status, d = client.operator_post("/proposals", body)
        err = client.blocked_or_error(status, d)
        if err:
            return err
        dec = d.get("decision") or {}
        return (
            f"Proposed to the queue: {d.get('id')}\n"
            f"  status: {d.get('status')}\n"
            f"  decision: {dec.get('decision')} (class {dec.get('action_class')}, route {dec.get('approval_route')})\n"
            f"It is waiting for the operator's approval — nothing runs until they approve."
        )

    @server.tool()
    @ora_tool
    def queue() -> str:
        """Show the approval queue summary (counts by status)."""
        status, d = client.operator_get("/queue")
        err = client.blocked_or_error(status, d)
        if err:
            return err
        return client.pretty(d.get("queue", d))

    @server.tool()
    @ora_tool
    def proposals_list(status: str = "pending_review") -> str:
        """List proposals in the operator queue, filtered by status (default pending_review).

        Args:
            status: pending_review | approved | rejected | executing | executed | blocked.
        """
        params = {"status": status} if status else None
        st, d = client.operator_get("/proposals", params=params)
        err = client.blocked_or_error(st, d)
        if err:
            return err
        props = d.get("proposals", [])
        if not props:
            return f"Queue is empty for status='{status}'."
        lines = [f"{len(props)} proposal(s) [{status}]:"]
        for p in props:
            dec = p.get("decision") or {}
            obj = (p.get("data") or {}).get("objective") or p.get("objective") or ""
            lines.append(f"  {p.get('id')} — {obj}  [{dec.get('decision', '?')}/{dec.get('action_class', '?')}]")
        return "\n".join(lines)

    @server.tool()
    @ora_tool
    def proposal_get(id: str) -> str:
        """Show the full detail of one proposal (what it actually is — the report/draft/email body).

        Args:
            id: the proposal id.
        """
        st, d = client.operator_get(f"/proposals/{id}")
        err = client.blocked_or_error(st, d)
        if err:
            return err
        return client.pretty(d)

    @server.tool()
    @ora_tool
    def proposal_approve(id: str) -> str:
        """HUMAN-AUTHORIZED ONLY (operator-gated). Approve a queued proposal. Call this ONLY when the
        operator explicitly says to approve it. Never approve your own proposal on your own judgement.

        Args:
            id: the proposal id to approve.
        """
        st, d = client.operator_post(f"/proposals/{id}/approve", {"approver_id": _ACTOR}, gated=True)
        err = client.blocked_or_error(st, d)
        if err:
            return err
        return f"Approved {id}: {client.pretty(d)}"

    @server.tool()
    @ora_tool
    def proposal_reject(id: str, reason: str = "") -> str:
        """HUMAN-AUTHORIZED ONLY (operator-gated). Reject a queued proposal. Call this ONLY when the
        operator says so.

        Args:
            id: the proposal id to reject.
            reason: optional reason.
        """
        body = {"approver_id": _ACTOR}
        if reason:
            body["reason"] = reason
        st, d = client.operator_post(f"/proposals/{id}/reject", body, gated=True)
        err = client.blocked_or_error(st, d)
        if err:
            return err
        return f"Rejected {id}: {client.pretty(d)}"

    @server.tool()
    @ora_tool
    def proposal_execute(id: str) -> str:
        """HUMAN-AUTHORIZED ONLY (operator-gated). Execute an APPROVED proposal (this performs the
        action). Call this ONLY when the operator explicitly says to execute it.

        Args:
            id: the approved proposal id to execute.
        """
        st, d = client.operator_post(f"/proposals/{id}/execute", {"approver_id": _ACTOR}, gated=True)
        err = client.blocked_or_error(st, d)
        if err:
            return err
        return f"Executed {id}: {client.pretty(d)}"
