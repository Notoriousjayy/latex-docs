# Reproducible laboratory code

These original companion implementations are didactic: the counters deliberately measure elementary operations rather than wall-clock time. The Python CLI produces one raw CSV row per independent repetition. The C++ CLI produces one row per execution. They are not optimized library substitutes or cryptographic tools.

## Python

```bash
python3 -m unittest -v test_models.py
python3 run_benchmarks.py --algorithm quick --sizes 16 32 64 128 --repeats 15 --seed 71 --output results.csv
```

## C/C++

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
./build/analysis_cpp merge 128 71
./build/analysis_cpp insert 128 71
./build/analysis_cpp occupancy 512 71 64
./build/occupancy_c 512 64 71
```

C++ and Python sort counts use the same semantic *type* of metric (element comparisons or shifts), but their operation counts need not be identical for every variant. C11 occupancy uses a small fixed LCG and modulo reduction; independence/uniformity assumptions are only approximate and must not be overclaimed. Use the templates in `../../templates/` for evidence capture.
