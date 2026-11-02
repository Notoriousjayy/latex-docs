"""Minimal finite access matrix for controlled training, not an IAM product."""
from dataclasses import dataclass, field

RIGHTS = frozenset({"read", "write"})


@dataclass
class AccessMatrix:
    owners: dict[str, str]
    rights: dict[tuple[str, str], set[str]] = field(default_factory=dict)

    def check(self, subject: str, obj: str, right: str) -> bool:
        return right in RIGHTS and right in self.rights.get((subject, obj), set())

    def grant(self, actor: str, subject: str, obj: str, right: str) -> None:
        if self.owners.get(obj) != actor or right not in RIGHTS:
            raise PermissionError("grant not authorized")
        self.rights.setdefault((subject, obj), set()).add(right)

    def revoke(self, actor: str, subject: str, obj: str, right: str) -> None:
        if self.owners.get(obj) != actor:
            raise PermissionError("revoke not authorized")
        self.rights.get((subject, obj), set()).discard(right)
