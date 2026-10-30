#include "algorithms.hpp"
#include <algorithm>
#include <stdexcept>
#define CHECK(expr) do { if (!(expr)) throw std::runtime_error("CHECK failed at line " + std::to_string(__LINE__) + ": " #expr); } while(false)
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

int main() {
    alg::RingBuffer<int> b(2);
    b.enqueue(1);b.enqueue(2);CHECK(b.dequeue()==1);
    b.enqueue(3);CHECK(b.dequeue()==2);CHECK(b.dequeue()==3);
    bool threw=false;
    try { (void)b.dequeue(); } catch(const std::out_of_range&) {threw=true;}
    CHECK(threw);
    for(std::uint64_t a=0;a<50;++a)for(std::uint64_t c=0;c<50;++c)
        CHECK(alg::gcd(a,c)==std::gcd(a,c));
    CHECK((alg::lcg(0,4,1,9,9)==std::vector<std::uint32_t>{1,5,3,4,8,6,7,2,0}));
    std::vector<int> shuffled={1,2,3,4};std::mt19937 gen(17);
    alg::fisher_yates(shuffled,gen);std::sort(shuffled.begin(),shuffled.end());
    CHECK((shuffled==std::vector<int>{1,2,3,4}));
    std::mt19937 rng(3);
    for(auto n:{0,1,2,4,17,128}) {
        std::vector<alg::Record> records;
        for(int i=0;i<n;++i) records.push_back({static_cast<int>(rng()%5),static_cast<std::size_t>(i)});
        auto reference=records;
        std::stable_sort(reference.begin(),reference.end(),[](auto a,auto b){return a.key<b.key;});
        CHECK(alg::insertion_sort(records)==reference);
        CHECK(alg::stable_merge_sort(records)==reference);
    }
    std::vector<int> ordered={1,1,2,4,4,6};
    for(int value=-2;value<8;++value)
        CHECK(alg::lower_bound(ordered,value)==static_cast<std::size_t>(std::lower_bound(ordered.begin(),ordered.end(),value)-ordered.begin()));
    for(std::size_t n=0;n<7;++n)for(std::size_t k=0;k<=n;++k) {
        std::size_t count=0;
        alg::for_each_combination(n,k,[&](const auto& items){CHECK(items.size()==k);++count;});
        std::uint64_t expected=1;
        for(std::size_t i=1;i<=k;++i)expected=expected*(n-i+1)/i;
        CHECK(count==expected);
    }
    for(int n=0;n<=6;++n) {
        std::vector<int> elems(static_cast<std::size_t>(n));
        std::iota(elems.begin(),elems.end(),0);
        int count=0;
        alg::for_each_permutation(elems,[&](const auto& item){CHECK(item.size()==elems.size());++count;});
        int fac=1;for(int i=1;i<=n;++i)fac*=i;
        CHECK(count==fac);
    }
    const std::vector<std::uint64_t> expected={1,1,0,0,2,10,4,40,92};
    for(std::size_t n=0;n<expected.size();++n)CHECK(alg::n_queens(n)==expected[n]);
    const std::vector<std::set<int>> options={{1,2},{3,4},{1,3},{2,4}};
    auto sols=alg::exact_cover({1,2,3,4},options);
    CHECK(sols.size()==2);
    for(const auto& sol:sols) {
        std::set<int> seen;
        for(auto ix:sol)for(int item:options.at(ix))
            CHECK(seen.insert(item).second);
        CHECK((seen==std::set<int>{1,2,3,4}));
    }
    CHECK(alg::exact_cover({},{}).size()==1);
    CHECK(alg::exact_cover({1},{}).empty());
    CHECK(alg::dpll({}).has_value());
    CHECK(!alg::dpll({{1},{-1}}).has_value());
    auto witness=alg::dpll({{1,2},{-1,2},{1,-2}});
    CHECK(witness.has_value());
    CHECK(alg::cnf_satisfied({{1,2},{-1,2},{1,-2}},*witness));
    std::mt19937 dg(13);
    for(int vars=1;vars<=4;++vars)for(int trial=0;trial<100;++trial) {
        alg::CNF cnf;
        auto clause_count=dg()%7;
        for(unsigned j=0;j<clause_count;++j) {
            std::vector<int> clause;
            auto clause_len=dg()%4;
            for(unsigned t=0;t<clause_len;++t) {
                int var=static_cast<int>(dg()%static_cast<unsigned>(vars))+1;
                clause.push_back((dg()%2)?var:-var);
            }
            cnf.push_back(clause);
        }
        bool brute=false;
        for(int mask=0;mask<(1<<vars);++mask) {
            alg::Assignment asg;
            for(int v=1;v<=vars;++v)asg[v]=bool(mask&(1<<(v-1)));
            brute|=alg::cnf_satisfied(cnf,asg);
        }
        auto solution=alg::dpll(cnf);
        CHECK(solution.has_value()==brute);
        if(solution)CHECK(alg::cnf_satisfied(cnf,*solution));
    }
    std::cout << "All algorithm reference tests passed.\n";
}
