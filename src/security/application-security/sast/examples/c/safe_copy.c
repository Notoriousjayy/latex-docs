#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* Avoids unbounded writes and reports lack of capacity without truncation. */
int safe_copy(char *dst, size_t capacity, const char *src) {
    if (!dst || !src || capacity == 0) return -1;
    size_t len = 0;
    /* Source must be readable for up to capacity bytes. */
    while (len < capacity && src[len] != '\0') ++len;
    if (len == capacity) return -2;
    memmove(dst, src, len + 1);
    return 0;
}

int checked_multiply(size_t count, size_t width, size_t *result) {
    if (!result) return -1;
    if (width != 0 && count > SIZE_MAX / width) return -2;
    *result = count * width;
    return 0;
}

int main(void) {
    char buffer[5] = {0};
    size_t n = 0;
    if (safe_copy(buffer, sizeof buffer, "abcd") != 0) return 1;
    if (strcmp(buffer, "abcd") != 0) return 2;
    if (safe_copy(buffer, sizeof buffer, "abcde") != -2) return 3;
    if (safe_copy(buffer, 0, "x") != -1) return 4;
    if (checked_multiply(SIZE_MAX, 2, &n) != -2) return 5;
    if (checked_multiply(4, 8, &n) != 0 || n != 32) return 6;
    puts("safe_copy tests passed");
    return 0;
}
