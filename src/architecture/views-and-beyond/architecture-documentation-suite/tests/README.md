# Manifest validator tests

[test_validate.py](test_validate.py) covers a valid example, dangling references, missing observed evidence, duplicate IDs, uncovered high-priority concerns and a missing baseline.

Run from the suite root with Python 3:

```bash
python3 -m unittest discover -s tests -v
```

The tests verify selected structural checks, not architecture quality or standards conformance. See the [validator](../scripts/validate.py) and [suite index](../README.md).
