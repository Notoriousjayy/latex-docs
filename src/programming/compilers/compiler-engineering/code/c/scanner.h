#ifndef CE_SCANNER_H
#define CE_SCANNER_H
#include <stddef.h>
#include <stdint.h>
typedef enum { CE_INT, CE_PLUS, CE_MINUS, CE_STAR, CE_SLASH, CE_LPAREN, CE_RPAREN, CE_END, CE_ERROR } ce_kind;
typedef struct { ce_kind kind; size_t start, end; uint64_t value; } ce_token;
typedef struct { const char *source; size_t length, offset; } ce_scanner;
/* Token length and integer range are bounded. Input is ASCII expression subset. */
ce_token ce_next(ce_scanner *scanner);
#endif
