CC ?= cc
CPPFLAGS ?=
CFLAGS ?= -std=c99 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -O2
.PHONY: all test clean
all: frame_test
frame_test: frame_codec.c frame_codec.h test_frame_codec.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -I. frame_codec.c test_frame_codec.c -o $@
test: frame_test
	./frame_test
clean:
	rm -f frame_test
