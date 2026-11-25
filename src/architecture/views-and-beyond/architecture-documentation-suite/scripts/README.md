# Structural validation

[validate.py](validate.py) checks manifest IDs, reference resolution, selected provenance fields, evidence ranges and high-priority concern coverage. It does not certify architecture correctness or ISO conformance.

Run from the suite root with Python 3:

```bash
python3 scripts/validate.py examples/example-manifest.json
```

See the [tests](../tests/README.md) and [suite index](../README.md).
