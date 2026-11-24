"""Offline, synthetic, read-only harness. Not a production security boundary."""
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable


@dataclass(frozen=True)
class Scope:
    tenant: str
    repository: str
    revision: str
    role: str = "appsec-investigator"


@dataclass(frozen=True)
class Proposal:
    tool: str
    repository: str
    revision: str
    finding_id: str

    @classmethod
    def parse(cls, raw: str):
        if not isinstance(raw, str) or len(raw) > 4096:
            raise ValueError("invalid-proposal-size")
        def unique(pairs):
            out = {}
            for key, value in pairs:
                if key in out:
                    raise ValueError("duplicate-field")
                out[key] = value
            return out
        data = json.loads(raw, object_pairs_hook=unique)
        fields = {"tool", "repository", "revision", "finding_id"}
        if type(data) is not dict or set(data) != fields:
            raise ValueError("invalid-fields")
        if any(type(v) is not str or not 0 < len(v) <= 128
               for v in data.values()):
            raise ValueError("invalid-value")
        return cls(**data)


@dataclass(frozen=True)
class Receipt:
    outcome: str
    reason: str
    policy_version: str
    evidence_digest: str | None = None


class Harness:
    """One synchronous run; no concurrency, network or mutation."""

    def __init__(self, scope: Scope, budget: int = 3):
        if type(budget) is not int or not 1 <= budget <= 10:
            raise ValueError("invalid-budget")
        self.scope = scope
        self.remaining = budget
        self.receipts: list[Receipt] = []
        # Only synthetic, sanitized metadata is stored.
        self._fixtures = {
            ("training", "demo/repo", "revision-1", "F-1"): {
                "finding_id": "F-1",
                "kind": "secret-placeholder",
                "location": "examples/config.txt",
                "credential_value": "[REDACTED]",
                "source_state": "open",
            }
        }

    def _record(self, outcome, reason, digest=None):
        receipt = Receipt(outcome, reason, "offline-v1", digest)
        self.receipts.append(receipt)
        return receipt

    def step(self, raw: str):
        if self.remaining <= 0:
            return self._record("deny", "budget-exhausted"), None
        # Reserve before validation; denied attempts consume budget.
        self.remaining -= 1
        try:
            action = Proposal.parse(raw)
        except (ValueError, RecursionError):
            return self._record("deny", "invalid-proposal"), None
        s = self.scope
        if (s.role != "appsec-investigator"
                or action.tool != "read_evidence"
                or action.repository != s.repository
                or action.revision != s.revision):
            return self._record("deny", "out-of-scope"), None
        key = (s.tenant, s.repository, s.revision, action.finding_id)
        data = self._fixtures.get(key)
        if data is None:
            return self._record("abstain", "evidence-unavailable"), None
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":"))
        digest = sha256(encoded.encode()).hexdigest()
        return self._record("allow", "synthetic-read", digest), dict(data)


def investigate(harness: Harness, propose: Callable[[], str]):
    """A model port is represented by a local callable, not an API."""
    try:
        raw = propose()
    except Exception:
        return harness._record("abstain", "model-unavailable"), None
    return harness.step(raw)


if __name__ == "__main__":
    run = Harness(Scope("training", "demo/repo", "revision-1"))
    receipt, evidence = investigate(run, lambda: json.dumps({
        "tool": "read_evidence", "repository": "demo/repo",
        "revision": "revision-1", "finding_id": "F-1",
    }))
    print(receipt)
    print(evidence)
