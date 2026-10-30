#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$ROOT/python-service/src${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest "$ROOT/python-service/tests" -q
python3 "$ROOT/database-migration/check_migration.py"
(cd "$ROOT/benchmarks" && python3 -m unittest -q test_analyze_runs.py)
if command -v mvn >/dev/null 2>&1; then
  mvn -B -ntp -f "$ROOT/java-service/pom.xml" verify
else
  echo "SKIP: Maven unavailable; Java JUnit integration unverified" >&2
fi
if command -v cmake >/dev/null 2>&1; then
  BUILD_DIR="$(mktemp -d)"
  trap 'rm -rf "$BUILD_DIR"' EXIT
  cmake -S "$ROOT/cpp-service" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Debug
  cmake --build "$BUILD_DIR" --parallel 2
  ctest --test-dir "$BUILD_DIR" --output-on-failure
else
  echo "SKIP: CMake unavailable; C++ integration unverified" >&2
fi
