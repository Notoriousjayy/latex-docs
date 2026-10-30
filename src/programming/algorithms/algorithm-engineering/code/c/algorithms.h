#ifndef ALGORITHM_ENGINEERING_C_H
#define ALGORITHM_ENGINEERING_C_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Original educational baselines, ISO C11. */
typedef struct { int key; size_t ordinal; } alg_record;
uint64_t alg_gcd(uint64_t a, uint64_t b);
size_t alg_lower_bound(const int *values, size_t n, int target);
void alg_stable_insertion_sort(alg_record *records, size_t n);
bool alg_lcg_next(uint32_t *state, uint32_t multiplier, uint32_t increment, uint32_t modulus);
uint64_t alg_n_queens_count(unsigned n);
#endif
