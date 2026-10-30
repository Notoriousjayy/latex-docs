#include "algorithms.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"failed line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
int main(void){
    CHECK(alg_gcd(0,0)==0);CHECK(alg_gcd(252,105)==21);
    for(uint64_t a=0;a<40;++a)for(uint64_t b=0;b<40;++b){
        uint64_t x=a,y=b;while(y){uint64_t r=x%y;x=y;y=r;}CHECK(alg_gcd(a,b)==x);
    }
    const int seq[]={1,1,2,4,4,6};
    CHECK(alg_lower_bound(seq,6,4)==3);
    CHECK(alg_lower_bound(seq,6,5)==5);
    CHECK(alg_lower_bound(seq,0,5)==0);
    alg_record rec[]={{2,0},{1,1},{2,2},{1,3}};
    alg_stable_insertion_sort(rec,4);
    CHECK(rec[0].ordinal==1 && rec[1].ordinal==3 && rec[2].ordinal==0 && rec[3].ordinal==2);
    uint32_t state=0;const uint32_t expected[]={1,5,3,4,8,6,7,2,0};
    for(size_t i=0;i<9;++i){CHECK(alg_lcg_next(&state,4,1,9));CHECK(state==expected[i]);}
    CHECK(!alg_lcg_next(NULL,4,1,9));
    const uint64_t queen_counts[]={1,1,0,0,2,10,4,40,92};
    for(unsigned n=0;n<9;++n)CHECK(alg_n_queens_count(n)==queen_counts[n]);
    puts("C11 reference tests passed");return 0;
}
