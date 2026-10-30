# Build and validation scripts

- `build-algorithm-suite.sh` compiles each standalone source (two passes for cross-references), with `ALGO_SUITE_SKIP_EXISTING=1` for already validated PDF outputs.
- `test-algorithm-code.sh` runs Python, ISO C11, and C++20 tests.
- `validate-algorithm-suite.py` audits document inventory, source hygiene, and Template-to-Blank pairing.

`ALGO_SUITE_SOURCE_ROOT` and `ALGO_SUITE_OUTPUT_ROOT` can override the default LaTeX input and output paths for imported repositories.
