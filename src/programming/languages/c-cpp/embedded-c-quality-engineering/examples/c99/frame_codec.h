#ifndef FRAME_CODEC_H
#define FRAME_CODEC_H

#include <stddef.h>
#include <stdint.h>

/* Wire format: 0xA5, payload length, payload, XOR checksum.
 * Maximum payload length is 32 bytes. No dynamic allocation. */
#define FRAME_CODEC_MAX_PAYLOAD 32u

typedef enum
{
    FRAME_CODEC_OK = 0,
    FRAME_CODEC_INVALID_ARGUMENT,
    FRAME_CODEC_BAD_START,
    FRAME_CODEC_BAD_LENGTH,
    FRAME_CODEC_BAD_CHECKSUM
} frame_codec_status_t;

typedef struct
{
    uint8_t payload_size;
    uint8_t payload[FRAME_CODEC_MAX_PAYLOAD];
} frame_codec_packet_t;

/* On failure, output is not modified. The input must have exactly
 * 3 + payload_size bytes. No pointers may overlap output storage. */
frame_codec_status_t frame_codec_decode(uint8_t const * input,
                                        size_t input_size,
                                        frame_codec_packet_t * output);

#endif /* FRAME_CODEC_H */
