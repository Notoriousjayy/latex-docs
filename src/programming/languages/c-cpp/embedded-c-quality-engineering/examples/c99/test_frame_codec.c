#include "frame_codec.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

static void
test_empty_packet(void)
{
    uint8_t const bytes[] = {0xA5u, 0u, 0u};
    frame_codec_packet_t packet = {0};

    assert(FRAME_CODEC_OK ==
           frame_codec_decode(bytes, sizeof(bytes), &packet));
    assert(0u == packet.payload_size);
}

static void
test_payload_and_checksum(void)
{
    uint8_t const bytes[] = {0xA5u, 2u, 0x11u, 0x22u, 0x31u};
    frame_codec_packet_t packet = {0};

    assert(FRAME_CODEC_OK ==
           frame_codec_decode(bytes, sizeof(bytes), &packet));
    assert(2u == packet.payload_size);
    assert(0x11u == packet.payload[0]);
    assert(0x22u == packet.payload[1]);
}

static void
test_failure_preserves_output(void)
{
    uint8_t const wrong_crc[] = {0xA5u, 1u, 0x7Fu, 0u};
    uint8_t const truncated[] = {0xA5u, 1u, 0x7Fu};
    frame_codec_packet_t packet = {0};
    packet.payload_size = 9u;
    packet.payload[0] = 0x44u;

    assert(FRAME_CODEC_BAD_CHECKSUM ==
           frame_codec_decode(wrong_crc, sizeof(wrong_crc), &packet));
    assert(9u == packet.payload_size);
    assert(0x44u == packet.payload[0]);
    assert(FRAME_CODEC_BAD_LENGTH ==
           frame_codec_decode(truncated, sizeof(truncated), &packet));
    assert(9u == packet.payload_size);
}

static void
test_invalid_arguments(void)
{
    uint8_t const bytes[] = {0xA5u, 0u, 0u};
    frame_codec_packet_t packet = {0};

    assert(FRAME_CODEC_INVALID_ARGUMENT ==
           frame_codec_decode(NULL, 3u, &packet));
    assert(FRAME_CODEC_INVALID_ARGUMENT ==
           frame_codec_decode(bytes, sizeof(bytes), NULL));
    assert(FRAME_CODEC_BAD_LENGTH ==
           frame_codec_decode(bytes, 2u, &packet));
}

static void
test_maximum_packet(void)
{
    uint8_t bytes[3u + FRAME_CODEC_MAX_PAYLOAD] = {0};
    uint8_t checksum = FRAME_CODEC_MAX_PAYLOAD;
    frame_codec_packet_t packet = {0};

    bytes[0] = 0xA5u;
    bytes[1] = FRAME_CODEC_MAX_PAYLOAD;

    for (size_t i = 0u; i < FRAME_CODEC_MAX_PAYLOAD; ++i)
    {
        bytes[2u + i] = (uint8_t)i;
        checksum = (uint8_t)(checksum ^ bytes[2u + i]);
    }

    bytes[2u + FRAME_CODEC_MAX_PAYLOAD] = checksum;

    assert(FRAME_CODEC_OK ==
           frame_codec_decode(bytes, sizeof(bytes), &packet));
    assert(FRAME_CODEC_MAX_PAYLOAD == packet.payload_size);
}

int
main(void)
{
    test_empty_packet();
    test_payload_and_checksum();
    test_failure_preserves_output();
    test_invalid_arguments();
    test_maximum_packet();
    puts("PASS: frame codec C99 tests");
    return 0;
}
