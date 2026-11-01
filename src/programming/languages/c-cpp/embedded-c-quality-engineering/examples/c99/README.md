# Original C99 frame-codec demonstration

A small host-only packet decoder with no MCU dependencies. Protocol: start byte `0xA5`, one-byte payload length (0..32), payload and XOR checksum. Invalid packets do not modify the output object.

Run `make test` in this directory; run `make clean` afterward. The Makefile intentionally keeps the program offline and uses strict compiler diagnostics. This teaching program is not a cryptographic integrity protocol, a safety-certified driver or a fuzzed production implementation.

The inactive workflow example is placed in `../workflows/` and requires action SHA pinning and environment review before operational use.
