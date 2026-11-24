# Offline AppSec harness examples

- [harness_demo.py](harness_demo.py): synthetic, read-only typed proposals, authorization and evidence receipts.
- [test_harness_demo.py](test_harness_demo.py): eleven standard-library unit tests.

Run from the suite root using Python 3.10 or newer:

```bash
python3 -m unittest discover -s examples -v
python3 examples/harness_demo.py
```

No live scanner, model, credentials or network access is used. See the [study](../agent-harness-engineering-for-application-security.tex) for production limitations.
