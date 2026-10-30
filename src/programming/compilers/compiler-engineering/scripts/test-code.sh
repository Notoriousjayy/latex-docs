#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
(cd "$DIR/code/python" && python3 -m unittest -v test_compiler)
make -C "$DIR/code/c" test
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"; make -C "$DIR/code/c" clean >/dev/null' EXIT
cmake -S "$DIR/code/cpp" -B "$BUILD" -DCMAKE_BUILD_TYPE=Debug
cmake --build "$BUILD" --parallel 2
ctest --test-dir "$BUILD" --output-on-failure
