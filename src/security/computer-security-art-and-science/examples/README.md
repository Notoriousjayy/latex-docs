# Executable, synthetic security laboratories

All examples are original and operate locally without a network service or credentials. They demonstrate *bounded* properties; no sample proves production security or general model safety.

From the repository root:

```bash
SUITE=src/security/computer-security-art-and-science
python3 -m unittest discover -s "$SUITE/examples/python" -p 'test_*.py' -v
cc -std=c99 -O2 -Wall -Wextra -Wpedantic -Werror "$SUITE/examples/c/checked_copy.c" -o /tmp/ces-checked-copy
/tmp/ces-checked-copy
c++ -std=c++17 -O2 -Wall -Wextra -Wpedantic -Werror "$SUITE/examples/cpp/object_authorization.cpp" -o /tmp/ces-object-auth
/tmp/ces-object-auth
```

Negative cases are deliberate test assertions; no exploit code, untrusted target or external data is required. The C helper assumes a valid readable source range and non-overlapping buffers; use a higher-level parsing contract to establish those preconditions. The noninterference probe evaluates only sampled executions, not a mathematical proof.
