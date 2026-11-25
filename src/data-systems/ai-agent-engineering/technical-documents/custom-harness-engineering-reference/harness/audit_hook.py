"""Illustrative observer; no raw arguments or credentials are logged."""
import json, sys
try:
    event = json.load(sys.stdin)
    if not isinstance(event, dict): raise ValueError('invalid event')
    print(json.dumps({"observed": True}), file=sys.stderr)
except (ValueError, OSError):
    print('invalid hook event', file=sys.stderr)
# Observation only; never claims authorization or comprehensive tool coverage.
