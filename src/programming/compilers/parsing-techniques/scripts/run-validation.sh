#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$here/scripts/validate_suite.py"
python3 -m unittest discover -s "$here/code/python" -p 'test_*.py' -v
cmake -S "$here/code/cpp" -B "${TMPDIR:-/tmp}/parsing-suite-cpp-build" -DCMAKE_BUILD_TYPE=Debug
cmake --build "${TMPDIR:-/tmp}/parsing-suite-cpp-build" --parallel
ctest --test-dir "${TMPDIR:-/tmp}/parsing-suite-cpp-build" --output-on-failure
printf 'All suite structure and reference-code checks passed.\n'
