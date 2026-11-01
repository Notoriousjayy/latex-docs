#include "frame_codec.h"

#include <stddef.h>
#include <stdint.h>

#define FRAME_CODEC_START 0xA5u
#define FRAME_CODEC_OVERHEAD 3u

frame_codec_status_t
frame_codec_decode(uint8_t const * input,
                   size_t input_size,
                   frame_codec_packet_t * output)
{
    uint8_t payload_size;
    uint8_t checksum;
    size_t expected_size;
    frame_codec_packet_t candidate = {0};

    if ((NULL == input) || (NULL == output))
    {
        return FRAME_CODEC_INVALID_ARGUMENT;
    }

    if (input_size < FRAME_CODEC_OVERHEAD)
    {
        return FRAME_CODEC_BAD_LENGTH;
    }

    if (FRAME_CODEC_START != input[0])
    {
        return FRAME_CODEC_BAD_START;
    }

    payload_size = input[1];

    if (payload_size > FRAME_CODEC_MAX_PAYLOAD)
    {
        return FRAME_CODEC_BAD_LENGTH;
    }

    /* size_t is at least 16 bits in C99; 3 + 32 cannot overflow. */
    expected_size = (size_t)payload_size + FRAME_CODEC_OVERHEAD;

    if (input_size != expected_size)
    {
        return FRAME_CODEC_BAD_LENGTH;
    }

    checksum = payload_size;

    for (size_t i = 0u; i < (size_t)payload_size; ++i)
    {
        candidate.payload[i] = input[2u + i];
        /* XOR of 8-bit operands remains in the unsigned 8-bit range. */
        checksum = (uint8_t)(checksum ^ input[2u + i]);
    }

    if (checksum != input[2u + (size_t)payload_size])
    {
        return FRAME_CODEC_BAD_CHECKSUM;
    }

    candidate.payload_size = payload_size;
    *output = candidate;
    return FRAME_CODEC_OK;
}
