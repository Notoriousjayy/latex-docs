#include <cassert>
#include <cmath>
#include <random>
#include <utility>
std::pair<double,double> estimate(double p,int n,unsigned seed) {
    assert(0<=p && p<=1 && n>0);
    std::mt19937 gen(seed);
    std::bernoulli_distribution success(p);
    int wins=0;
    for (int i=0;i<n;++i) if(success(gen)) ++wins;
    double rate=static_cast<double>(wins)/n;
    return {rate,std::sqrt(rate*(1-rate)/n)};
}
int main(){
    assert(estimate(0,100,17).first==0);
    assert(estimate(1,100,17).first==1);
    assert(estimate(.4,1000,17)==estimate(.4,1000,17));
}
