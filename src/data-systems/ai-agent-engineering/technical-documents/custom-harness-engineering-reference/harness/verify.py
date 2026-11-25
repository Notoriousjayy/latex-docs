"""External verification only: never executes an agent-proposed command."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

@dataclass(frozen=True)
class Result:
    gate: str
    status: str
    exit_code: int | None
    elapsed_ms: int
    output_sha256: str

# Production gate definitions must be mounted from a protected revision.
GATES = {"unit": (sys.executable, "-m", "unittest", "discover", "-s", "tests")}
WARNING = re.compile(r"(?:^(?:LaTeX(?: Font)?|Package .+?|Class .+?|pdfTeX|pdftex|LuaTeX|XeTeX) warning\b|^Warning\b|^Overfull \\[hv]box|^Underfull \\[hv]box|^! )", re.I)

def latex_diagnostics(log: str) -> list[str]:
    return [line for line in log.splitlines() if WARNING.search(line)]

def run_gate(gate: str, workspace: Path, timeout: int = 60) -> Result:
    if gate not in GATES or timeout < 1 or timeout > 600:
        raise ValueError("unknown gate or invalid timeout")
    start = time.monotonic()
    # A minimal environment reduces accidental credential propagation; not a sandbox.
    env = {k: os.environ[k] for k in ("PATH", "SYSTEMROOT", "TMPDIR", "TEMP") if k in os.environ}
    try:
        p = subprocess.run(GATES[gate], cwd=workspace.resolve(), env=env,
                           capture_output=True, timeout=timeout, check=False)
        output = p.stdout + p.stderr
        status, code = ("PASS" if p.returncode == 0 and not re.search(rb"Ran 0 tests?\b", output) else "FAIL"), p.returncode
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or b"") + (exc.stderr or b"")
        status, code = "TIMEOUT", None
    except OSError:
        output, status, code = b"runner unavailable", "BLOCKED", None
    return Result(gate, status, code, round((time.monotonic()-start)*1000), hashlib.sha256(output).hexdigest())

def bounded_remediation(check: Callable[[], tuple[str, str]], repair: Callable[[], bool], limit: int = 2) -> str:
    """Callback invokes an approved native agent externally; no model/tool loop."""
    if not 0 <= limit <= 5:
        raise ValueError("retry budget out of range")
    seen: set[str] = set()
    for attempt in range(limit + 1):
        status, signature = check()
        if status == "PASS":
            return "PASS"
        if status != "FAIL" or signature in seen or attempt == limit:
            return "ESCALATE"
        seen.add(signature)
        if not repair():
            return "ESCALATE"
    return "ESCALATE"

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", type=Path, default=Path.cwd())
    p.add_argument("--latex-log", type=Path)
    args = p.parse_args()
    if args.latex_log:
        try:
            hits = latex_diagnostics(args.latex_log.read_text(errors="replace"))
        except OSError:
            return 2
        print(json.dumps({"diagnostic_count": len(hits), "status": "FAIL" if hits else "PASS"}))
        return int(bool(hits))
    result = run_gate("unit", args.workspace)
    print(json.dumps(asdict(result)))
    return int(result.status != "PASS")

if __name__ == "__main__":
    raise SystemExit(main())
