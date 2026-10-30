CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic
.PHONY: all test clean
all: alg_c_tests
alg_c_tests: algorithms.c algorithms.h test_algorithms.c
	$(CC) $(CFLAGS) algorithms.c test_algorithms.c -o alg_c_tests
test: alg_c_tests
	./alg_c_tests
clean:
	rm -f alg_c_tests
