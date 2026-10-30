#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
(cd "$ROOT/code/python" && python3 -m unittest -v)
(cd "$ROOT/code/c" && make test)
cmake -S "$ROOT/code/cpp" -B "${TMPDIR:-/tmp}/algorithm-suite-cpp-build-$USER" -DCMAKE_BUILD_TYPE=Debug
cmake --build "${TMPDIR:-/tmp}/algorithm-suite-cpp-build-$USER" --parallel 2
ctest --test-dir "${TMPDIR:-/tmp}/algorithm-suite-cpp-build-$USER" --output-on-failure
