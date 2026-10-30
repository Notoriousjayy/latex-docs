// Educational C++17 algorithms. Metrics count explicitly defined operations.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

struct Counts { std::uint64_t comparisons=0, shifts=0, colliding_pairs=0; };

Counts merge_sort(std::vector<int>& a) {
    Counts out;
    std::vector<int> scratch(a.size());
    const auto visit = [&](const auto& self, std::size_t lo, std::size_t hi)->void {
        if (hi-lo<2) return;
        const auto mid=lo+(hi-lo)/2;
        self(self,lo,mid); self(self,mid,hi);
        auto i=lo, j=mid, k=lo;
        while (i<mid && j<hi) {
            ++out.comparisons;
            scratch[k++] = (a[i]<=a[j]) ? a[i++] : a[j++];
        }
        while(i<mid) scratch[k++]=a[i++];
        while(j<hi) scratch[k++]=a[j++];
        std::copy(scratch.begin()+lo,scratch.begin()+hi,a.begin()+lo);
    };
    visit(visit,0,a.size());
    return out;
}

Counts insertion_sort(std::vector<int>& a) {
    Counts out;
    for(std::size_t i=1;i<a.size();++i) {
        int key=a[i]; std::size_t j=i;
        while(j>0) {
            ++out.comparisons;
            if(a[j-1]<=key) break;
            a[j]=a[j-1]; --j; ++out.shifts;
        }
        a[j]=key;
    }
    return out;
}

std::uint64_t inversion_oracle(const std::vector<int>& a) {
    std::uint64_t count=0;
    for (std::size_t i=0;i<a.size();++i)
        for (std::size_t j=i+1;j<a.size();++j)
            if (a[i]>a[j]) ++count;
    return count;
}

Counts occupancy(std::size_t m, std::size_t b, std::uint32_t seed) {
    if(b==0) throw std::invalid_argument("bucket count must be >0");
    std::mt19937 gen(seed);
    std::uniform_int_distribution<std::size_t> pick(0,b-1);
    std::vector<std::uint64_t> counts(b,0);
    for(std::size_t i=0;i<m;++i) ++counts[pick(gen)];
    Counts result;
    std::uint64_t total=0;
    for(auto x:counts) {total+=x;result.colliding_pairs+=x*(x-1)/2;}
    if(total!=m) throw std::runtime_error("occupancy invariant failed");
    return result;
}

#ifndef ANALYSIS_LIB_ONLY
int main(int argc, char** argv) {
    try {
        if(argc<4) {
            std::cerr << "usage: analysis_cpp <merge|insert|occupancy> <n> <seed> [buckets]\n";
            return 2;
        }
        const std::string method=argv[1];
        const auto n=static_cast<std::size_t>(std::stoull(argv[2]));
        const auto seed=static_cast<std::uint32_t>(std::stoul(argv[3]));
        if(n>10000000) throw std::invalid_argument("n exceeds demo guard");
        Counts result;
        std::int64_t elapsed=0;
        if(method=="occupancy") {
            if(argc!=5) throw std::invalid_argument("occupancy requires buckets");
            auto b=static_cast<std::size_t>(std::stoull(argv[4]));
            const auto start=std::chrono::steady_clock::now();
            result=occupancy(n,b,seed);
            elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::steady_clock::now()-start).count();
        } else {
            if(n>static_cast<std::size_t>(INT32_MAX)) throw std::invalid_argument("n exceeds int key range");
            std::vector<int> data(n);
            std::iota(data.begin(),data.end(),0);
            std::mt19937 gen(seed);
            std::shuffle(data.begin(),data.end(),gen);
            const auto start=std::chrono::steady_clock::now();
            if(method=="merge") result=merge_sort(data);
            else if(method=="insert") result=insertion_sort(data);
            else throw std::invalid_argument("unknown algorithm");
            elapsed=std::chrono::duration_cast<std::chrono::nanoseconds>(
                std::chrono::steady_clock::now()-start).count();
            if(!std::is_sorted(data.begin(),data.end())) throw std::runtime_error("sort incorrect");
        }
        std::cout << "algorithm,language,n,seed,comparisons,shifts,colliding_pairs,elapsed_ns,correct\n"
                  << method << ",C++," << n << ',' << seed << ','
                  << result.comparisons << ',' << result.shifts << ','
                  << result.colliding_pairs << ',' << elapsed << ",true\n";
    } catch(const std::exception& e) {
        std::cerr << "error: " << e.what() << '\n'; return 1;
    }
}
#endif
