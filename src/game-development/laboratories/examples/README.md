# Executable laboratory examples

These are small, synthetic, standalone examples, not a game engine. They model rules and evidence, not player enjoyment.

```bash
python3 -m unittest discover -s python -p "test_*.py"
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

Run from this examples directory. Python programs also execute their own assertions when run individually. The C++ example programs use `assert`, so build without `NDEBUG` to retain those checks.
