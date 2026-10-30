#include <cassert>
#include <stdexcept>
#include <algorithm>
struct Challenge{
    int level=3,min=1,max=5;
    void observe(double rate){
        if(rate<0 || rate>1) throw std::invalid_argument("rate");
        if(rate>.8) level=std::min(max,level+1);
        else if(rate<.2) level=std::max(min,level-1);
    }
};
int main(){
    Challenge d;
    for(int i=0;i<20;++i)d.observe(1);
    assert(d.level==5);
    for(int i=0;i<20;++i)d.observe(0);
    assert(d.level==1);
    d.observe(.5);assert(d.level==1);
}
