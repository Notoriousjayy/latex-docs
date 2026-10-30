# C++20 reference implementations

The header-only examples live in `include/algorithms.hpp`; tests are under `tests/` and the standalone CSV benchmarking harness is in `src/`. Run:

```sh
cmake -S . -B /tmp/algo-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /tmp/algo-build
ctest --test-dir /tmp/algo-build --output-on-failure
/tmp/algo-build/alg_bench 4096 15 20 > results.csv
```

The reference DPLL and exact-cover implementations prioritize understandable invariants and validation, not industrial solver performance.
