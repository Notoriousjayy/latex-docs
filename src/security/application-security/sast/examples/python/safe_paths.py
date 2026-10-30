"""Educational canonical path checks; not atomic against malicious concurrent symlink writers."""
from pathlib import Path


def safe_path(root: Path, untrusted_name: str) -> Path:
    if not untrusted_name:
        raise ValueError("Path required")
    supplied = Path(untrusted_name)
    if supplied.is_absolute():
        raise ValueError("Absolute paths disallowed")
    trusted_root = root.resolve(strict=True)
    candidate = (trusted_root / supplied).resolve(strict=False)
    if not candidate.is_relative_to(trusted_root):
        raise ValueError("Outside trusted root")
    return candidate
