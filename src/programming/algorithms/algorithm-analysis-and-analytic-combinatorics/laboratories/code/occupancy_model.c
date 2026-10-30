/* Portable C11 occupancy exercise; pseudorandomness is educational only. */
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static size_t positive_size(const char *arg) {
    char *end = NULL;
    errno=0;
    unsigned long long v=strtoull(arg,&end,10);
    if(errno || end==arg || *end!='\0' || v==0 || v>10000000ULL) {
        fprintf(stderr,"invalid positive integer: %s\n",arg); exit(2);
    }
    return (size_t)v;
}
int main(int argc, char **argv) {
    if(argc!=4) {
        fputs("usage: occupancy_c <keys> <buckets> <seed>\n",stderr); return 2;
    }
    const size_t m=positive_size(argv[1]), b=positive_size(argv[2]);
    uint32_t state=(uint32_t)positive_size(argv[3]);
    if (b > UINT32_MAX) { fputs("too many buckets\n",stderr); return 2; }
    uint64_t *counts=calloc(b,sizeof(*counts));
    if(!counts) {perror("calloc");return 1;}
    for(size_t i=0;i<m;++i) {
        state=state*1664525u+1013904223u; /* fixed LCG, modulo bias possible */
        ++counts[(size_t)(state % (uint32_t)b)];
    }
    uint64_t sum=0, pairs=0;
    for(size_t j=0;j<b;++j) {
        const uint64_t x=counts[j]; sum+=x; pairs+=x*(x-1)/2;
    }
    free(counts);
    if(sum!=(uint64_t)m) {fputs("invariant failure\n",stderr);return 1;}
    printf("keys,buckets,seed,total,colliding_pairs\n%zu,%zu,%s,%" PRIu64 ",%" PRIu64 "\n",
           m,b,argv[3],sum,pairs);
    return 0;
}
