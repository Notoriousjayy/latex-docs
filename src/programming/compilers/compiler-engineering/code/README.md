# Compiler Engineering Reference Code

This directory contains independent, runnable teaching kernels supporting the [Compiler Engineering Documentation Suite](../README.md). These examples are deliberately scoped laboratory implementations, not a production compiler.

## Language implementations

- [Python 3](python/README.md) — lexical analysis, expression parsing, three-address IR, liveness, local optimization, differential tests and a benchmarking driver.
- [C11](c/README.md) — bounded token scanner, diagnostic interfaces, assertion-based tests and a Makefile.
- [C++20](cpp/README.md) — CFG/data-flow solver, local scheduling and graph-coloring allocator demonstrations, with CMake and CTest.

## Verification

From the suite root, run `bash scripts/test-code.sh`. Read the associated laboratory manuals before extending these kernels, and preserve correctness tests before publishing performance claims.

## Boundaries

The reference kernels are not a full SSA implementation, ABI-compatible code generator, production JIT or hardened compiler. Do not execute untrusted source in an unrestricted host process.
