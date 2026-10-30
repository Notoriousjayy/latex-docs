// Usage: ./alg_bench 4096 15 20 > results.csv
#include "algorithms.hpp"
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>
static std::atomic<std::uint64_t> sink{0};
int main(int argc,char** argv) {
    const std::size_t n=argc>1?std::stoull(argv[1]):1024;
    const int repeats=argc>2?std::stoi(argv[2]):15;
    const int batch=argc>3?std::stoi(argv[3]):20;
    if(n==0 || repeats<=0 || batch<=0) throw std::invalid_argument("invalid benchmark parameters");
    std::mt19937 gen(42);
    std::vector<alg::Record> input;
    for(std::size_t i=0;i<n;++i)input.push_back({static_cast<int>(gen()%static_cast<std::uint32_t>(n/2+1)),i});
    auto ref=input;
    std::stable_sort(ref.begin(),ref.end(),[](auto a,auto b){return a.key<b.key;});
    std::cout << "language,variant,n,seed,run,batch_ops,elapsed_ns,checksum\n";
    for(int variant=0;variant<2;++variant) {
        auto method=variant==0?alg::insertion_sort:alg::stable_merge_sort;
        if(method(input)!=ref)throw std::runtime_error("correctness gate failed");
        (void)method(input);
        for(int run=0;run<repeats;++run) {
            const auto begin=std::chrono::steady_clock::now();
            for(int b=0;b<batch;++b) {
                auto result=method(input);
                sink.fetch_xor(static_cast<std::uint64_t>(result.back().key),std::memory_order_relaxed);
            }
            auto delta=std::chrono::steady_clock::now()-begin;
            auto ns=std::chrono::duration_cast<std::chrono::nanoseconds>(delta).count();
            std::cout << "cpp," << (variant==0?"insertion":"merge") << ',' << n << ",42," << run << ',' << batch << ',' << ns << ',' << sink.load() << '\n';
        }
    }
}
