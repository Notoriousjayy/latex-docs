#include "algorithms.h"
#include <stdint.h>
uint64_t alg_gcd(uint64_t a,uint64_t b) {
    while(b){uint64_t r=a%b;a=b;b=r;}return a;
}
size_t alg_lower_bound(const int *values,size_t n,int target) {
    size_t lo=0,hi=n;
    while(lo<hi){size_t mid=lo+(hi-lo)/2;
        if(values[mid]<target)lo=mid+1;else hi=mid;
    }return lo;
}
void alg_stable_insertion_sort(alg_record *v,size_t n){
    for(size_t i=1;i<n;++i){
        alg_record current=v[i];size_t j=i;
        while(j && v[j-1].key>current.key){v[j]=v[j-1];--j;}
        v[j]=current;
    }
}
bool alg_lcg_next(uint32_t *state,uint32_t multiplier,uint32_t increment,uint32_t modulus){
    if(!state||!modulus)return false;
    *state=(uint32_t)(((uint64_t)multiplier*(*state)+increment)%modulus);
    return true; /* NOT suitable for security-sensitive randomness */
}
typedef struct {unsigned n;bool col[16],up[32],down[32];} queen_state;
static uint64_t queens_visit(queen_state *s,unsigned row){
    if(row==s->n)return 1;
    uint64_t count=0;
    for(unsigned c=0;c<s->n;++c){
        unsigned u=row+s->n-c,d=row+c;
        if(s->col[c]||s->up[u]||s->down[d])continue;
        s->col[c]=s->up[u]=s->down[d]=true;
        count+=queens_visit(s,row+1);
        s->col[c]=s->up[u]=s->down[d]=false;
    }
    return count;
}
uint64_t alg_n_queens_count(unsigned n){
    if(n>16)return UINT64_MAX; /* documented invalid-size sentinel */
    queen_state s={0};s.n=n;return queens_visit(&s,0);
}
