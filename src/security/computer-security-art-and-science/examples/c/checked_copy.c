/*
 * Original C99-compatible security training program.
 * A bounded copy helper is not a replacement for higher-level protocol design.
 */
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

static bool checked_copy(char *dst, size_t capacity,
                         const char *src, size_t length)
{
    if (dst == NULL || src == NULL || capacity == 0U ||
        length >= capacity) {
        return false;
    }
    /* Caller guarantees src has length readable bytes and no overlap. */
    memcpy(dst, src, length);
    dst[length] = '\0';
    return true;
}

int main(void)
{
    char dst[5] = {'x', 'x', 'x', 'x', '\0'};
    const char hello[] = "hello";
    assert(checked_copy(dst, sizeof dst, "ok", 2U));
    assert(strcmp(dst, "ok") == 0);
    assert(!checked_copy(dst, sizeof dst, hello, 5U));
    assert(strcmp(dst, "ok") == 0); /* Reject without modifying output. */
    assert(!checked_copy(dst, 0U, "a", 1U));
    assert(!checked_copy(NULL, sizeof dst, "a", 1U));
    assert(!checked_copy(dst, sizeof dst, NULL, 1U));
    assert(checked_copy(dst, sizeof dst, "", 0U));
    assert(strcmp(dst, "") == 0);
    return 0;
}
