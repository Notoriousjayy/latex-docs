#include <algorithm>
#include <cassert>
#include <chrono>
#include <cmath>
#include <iostream>
#include <thread>
#include <vector>

static double work(unsigned i) {
    double result=0.;
    for(unsigned j=0;j<300;j++) result+=std::sqrt(static_cast<double>((i%997)+j+1));
    return result;
}
int main() {
    constexpr unsigned N=10'000;
    std::vector<double> sequential(N), parallel(N);
    for(unsigned i=0;i<N;++i) sequential[i]=work(i);
    unsigned workers=std::min(8u,std::max(1u,std::thread::hardware_concurrency()));
    auto t0=std::chrono::steady_clock::now();
    std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w) threads.emplace_back([&,w]{
        for(unsigned i=w;i<N;i+=workers) parallel[i]=work(i);
    });
    for(auto& th:threads) th.join(); // synchronization barrier before read
    auto t1=std::chrono::steady_clock::now();
    for(unsigned i=0;i<N;++i) assert(sequential[i]==parallel[i]);
    auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(t1-t0).count();
    std::cout<<"workers="<<workers<<" items="<<N<<" parallel_ns="<<ns<<"\n";
}
