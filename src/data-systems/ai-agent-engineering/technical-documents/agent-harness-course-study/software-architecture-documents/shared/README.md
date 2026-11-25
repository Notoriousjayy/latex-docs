# Shared model verification

Run `python3 validate.py` from this directory; use `--require-rendered` after canonical rendering. Structural validation is not semantic verification. [Cross-SAD source mappings](cross-sad-mappings.json) compare selected matching paths in Parts 2 and 3 by blob SHA. Equal source does not imply equal configuration or runtime behavior. Part 1 semantic response caching is distinct from Part 3 prompt-prefix caching.
