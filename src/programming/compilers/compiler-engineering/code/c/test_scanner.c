#include "scanner.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    const char *x=" 12 + (3*4)";
    ce_scanner s={x,strlen(x),0};
    assert(ce_next(&s).kind==CE_INT);
    assert(ce_next(&s).kind==CE_PLUS);
    assert(ce_next(&s).kind==CE_LPAREN);
    assert(ce_next(&s).kind==CE_INT);
    assert(ce_next(&s).kind==CE_STAR);
    assert(ce_next(&s).kind==CE_INT);
    assert(ce_next(&s).kind==CE_RPAREN);
    assert(ce_next(&s).kind==CE_END);
    ce_scanner bad={"3@",2,0};
    assert(ce_next(&bad).kind==CE_INT);
    assert(ce_next(&bad).kind==CE_ERROR);
    ce_scanner overflow={"12345678901234567890123456",26,0};
    assert(ce_next(&overflow).kind==CE_ERROR);
    ce_scanner empty={"",0,0};
    assert(ce_next(&empty).kind==CE_END);
    puts("C11 scanner tests passed");
}
