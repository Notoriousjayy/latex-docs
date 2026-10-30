# Original executable teaching examples

Python 3.11+ (standard library only):

```bash
cd code/python
python3 -m unittest -v test_animation
python3 export_demo.py --prefix shot01
```

C++20 (CMake 3.18+):

```bash
cmake -S code/cpp -B /tmp/animation-timing-cpp
cmake --build /tmp/animation-timing-cpp
ctest --test-dir /tmp/animation-timing-cpp --output-on-failure
/tmp/animation-timing-cpp/animation_timing_demo > spacing.csv
```

Metrics should be collected at real target runtime cadences. These reference exercises do not depend on a game engine and are not a complete animation renderer. Please do not publish captured animation assets or excerpts from the source book without the appropriate rights.
