CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -Werror -O2
.PHONY: all test clean
all: test_scanner
test_scanner: scanner.c scanner.h test_scanner.c
	$(CC) $(CFLAGS) scanner.c test_scanner.c -o $@
test: test_scanner
	./test_scanner
clean:
	rm -f test_scanner
