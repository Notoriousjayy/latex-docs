#include "scanner.h"
#include <stdint.h>

#define CE_MAX_SOURCE ((size_t)65536)
#define CE_MAX_DIGITS ((size_t)18)

ce_token ce_next(ce_scanner *s) {
    ce_token t={CE_ERROR,0,0,0};
    if (!s || !s->source || s->length>CE_MAX_SOURCE || s->offset>s->length)
        return t;
    while (s->offset<s->length) {
        char c=s->source[s->offset];
        if (c==' ' || c=='\t' || c=='\r' || c=='\n') ++s->offset;
        else break;
    }
    t.start=s->offset;
    if (s->offset==s->length) { t.kind=CE_END; t.end=s->offset; return t; }
    const char c=s->source[s->offset++];
    switch(c) {
      case '+':t.kind=CE_PLUS;break;
      case '-':t.kind=CE_MINUS;break;
      case '*':t.kind=CE_STAR;break;
      case '/':t.kind=CE_SLASH;break;
      case '(':t.kind=CE_LPAREN;break;
      case ')':t.kind=CE_RPAREN;break;
      default:
        if(c>='0' && c<='9') {
            uint64_t n=(uint64_t)(c-'0');
            size_t digits=1;
            while(s->offset<s->length && s->source[s->offset]>='0' && s->source[s->offset]<='9') {
                unsigned d=(unsigned)(s->source[s->offset]-'0');
                if(digits>=CE_MAX_DIGITS || n>(UINT64_MAX-d)/10) {
                    while(s->offset<s->length && s->source[s->offset]>='0' && s->source[s->offset]<='9')++s->offset;
                    t.end=s->offset;
                    return t;
                }
                n=n*10+d; ++digits; ++s->offset;
            }
            t.kind=CE_INT;t.value=n;
        } else t.kind=CE_ERROR;
    }
    t.end=s->offset;
    return t;
}
