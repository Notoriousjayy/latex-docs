#pragma once
// Original reference algorithms for educational comparison; C++20.
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <cstdlib>
#include <optional>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace alg {
template <typename T> class RingBuffer {
    std::vector<std::optional<T>> storage_;
    std::size_t head_ = 0, size_ = 0;
public:
    explicit RingBuffer(std::size_t capacity): storage_(capacity) {
        if (!capacity) throw std::invalid_argument("capacity must be positive");
    }
    std::size_t size() const { return size_; }
    void enqueue(T value) {
        if (size_ == storage_.size()) throw std::overflow_error("buffer full");
        storage_[(head_ + size_) % storage_.size()] = std::move(value);
        ++size_;
    }
    T dequeue() {
        if (!size_) throw std::out_of_range("buffer empty");
        T value = std::move(*storage_[head_]);
        storage_[head_].reset();
        head_ = (head_ + 1) % storage_.size();
        --size_;
        return value;
    }
};

inline std::uint64_t gcd(std::uint64_t a, std::uint64_t b) {
    while (b) { auto r = a % b; a = b; b = r; }
    return a;
}

inline std::vector<std::uint32_t> lcg(std::uint32_t seed, std::uint32_t a,
                                     std::uint32_t c, std::uint32_t m, std::size_t count) {
    if (!m) throw std::invalid_argument("modulus must be positive");
    std::uint64_t state = seed % m;
    std::vector<std::uint32_t> out;
    out.reserve(count);
    for (std::size_t i = 0; i < count; ++i) {
        state = (static_cast<std::uint64_t>(a) * state + c) % m;
        out.push_back(static_cast<std::uint32_t>(state));
    }
    return out;  // NOT suitable for security-sensitive random values.
}

template <typename T, typename URBG>
void fisher_yates(std::vector<T>& items, URBG& gen) {
    for (std::size_t count=items.size(); count>1; --count) {
        std::uniform_int_distribution<std::size_t> choose(0,count-1);
        std::swap(items[count-1],items[choose(gen)]);
    }
}

struct Record {
    int key;
    std::size_t ordinal;
    bool operator==(const Record&) const = default;
};

inline std::vector<Record> insertion_sort(std::vector<Record> values) {
    for (std::size_t i=1;i<values.size();++i) {
        Record current=values[i];
        std::size_t j=i;
        while(j>0 && values[j-1].key>current.key) {
            values[j]=values[j-1]; --j;
        }
        values[j]=current;
    }
    return values;
}

inline std::vector<Record> stable_merge_sort(std::vector<Record> values) {
    if(values.size()<2) return values;
    std::vector<Record> scratch(values.size());
    std::function<void(std::size_t,std::size_t)> sort = [&](auto low, auto high) {
        if(high-low<2) return;
        auto mid=low+(high-low)/2;
        sort(low,mid);sort(mid,high);
        std::size_t i=low,j=mid,k=low;
        while(i<mid && j<high) {
            if(values[i].key<=values[j].key) scratch[k++]=values[i++];
            else scratch[k++]=values[j++];
        }
        while(i<mid) scratch[k++]=values[i++];
        while(j<high) scratch[k++]=values[j++];
        for(auto p=low;p<high;++p) values[p]=scratch[p];
    };
    sort(0,values.size());
    return values;
}

inline std::size_t lower_bound(const std::vector<int>& a,int key) {
    std::size_t low=0, high=a.size();
    while(low<high) {
        auto mid=low+(high-low)/2;
        if(a[mid]<key) low=mid+1; else high=mid;
    }
    return low;
}

template <typename F> void for_each_combination(std::size_t n,std::size_t k,F&& emit) {
    if(k>n) return;
    std::vector<std::size_t> indices(k);
    std::iota(indices.begin(),indices.end(),0);
    while(true) {
        emit(indices);
        auto i=static_cast<std::ptrdiff_t>(k)-1;
        while(i>=0 && indices[static_cast<std::size_t>(i)] == n-k+static_cast<std::size_t>(i)) --i;
        if(i<0) return;
        ++indices[static_cast<std::size_t>(i)];
        for(auto j=static_cast<std::size_t>(i)+1;j<k;++j) indices[j]=indices[j-1]+1;
    }
}

template <typename F> void for_each_permutation(const std::vector<int>& a,F&& emit) {
    std::vector<std::size_t> indices(a.size());
    std::iota(indices.begin(),indices.end(),0);
    while(true) {
        std::vector<int> value;
        value.reserve(indices.size());
        for(auto i:indices) value.push_back(a[i]);
        emit(value);
        auto p=static_cast<std::ptrdiff_t>(indices.size())-2;
        while(p>=0 && indices[static_cast<std::size_t>(p)]>=indices[static_cast<std::size_t>(p)+1]) --p;
        if(p<0) return;
        auto q=indices.size()-1;
        while(indices[q]<=indices[static_cast<std::size_t>(p)]) --q;
        std::swap(indices[static_cast<std::size_t>(p)],indices[q]);
        std::reverse(indices.begin()+p+1,indices.end());
    }
}

inline std::uint64_t n_queens(std::size_t n) {
    if(n>20) throw std::invalid_argument("reference solver bound is n<=20");
    std::vector<bool> columns(n,false),d1(2*n+1,false),d2(2*n+1,false);
    std::function<std::uint64_t(std::size_t)> visit=[&](std::size_t row)->std::uint64_t {
        if(row==n) return 1;
        std::uint64_t total=0;
        for(std::size_t col=0;col<n;++col) {
            auto up=row+n-col,down=row+col;
            if(columns[col]||d1[up]||d2[down]) continue;
            columns[col]=d1[up]=d2[down]=true;
            total+=visit(row+1);
            columns[col]=d1[up]=d2[down]=false;
        }
        return total;
    };
    return visit(0);
}

inline std::vector<std::vector<std::size_t>> exact_cover(
    const std::set<int>& primary,const std::vector<std::set<int>>& options) {
    for(const auto& option: options) {
        if(option.empty() || !std::includes(primary.begin(),primary.end(),option.begin(),option.end()))
            throw std::invalid_argument("options must be nonempty subsets");
    }
    std::vector<std::vector<std::size_t>> solutions;
    std::vector<std::size_t> available(options.size());
    std::iota(available.begin(),available.end(),0);
    std::function<void(std::set<int>,std::vector<std::size_t>,std::vector<std::size_t>)>
    visit=[&](auto uncovered,auto selected,auto candidates) {
        if(uncovered.empty()) { solutions.push_back(std::move(selected)); return; }
        std::size_t best_count=std::numeric_limits<std::size_t>::max();
        int chosen=*uncovered.begin();
        for(int item: uncovered) {
            std::size_t count=0;
            for(auto id:candidates) if(options[id].count(item)) ++count;
            if(count<best_count) { best_count=count; chosen=item; }
        }
        for(auto index:candidates) {
            if(!options[index].count(chosen)) continue;
            auto remainder=uncovered;
            for(int item:options[index]) remainder.erase(item);
            std::vector<std::size_t> next;
            for(auto other:candidates) {
                if(other==index) continue;
                bool overlaps=false;
                for(int item:options[index]) if(options[other].count(item)) {overlaps=true;break;}
                if(!overlaps) next.push_back(other);
            }
            auto chosen_set=selected;chosen_set.push_back(index);
            visit(std::move(remainder),std::move(chosen_set),std::move(next));
        }
    };
    visit(primary,{},available);
    return solutions;
}

using CNF = std::vector<std::vector<int>>;
using Assignment = std::map<int,bool>;
inline bool cnf_satisfied(const CNF& formula,const Assignment& asg) {
    for(const auto& clause:formula) {
        bool ok=false;
        for(int lit:clause) {
            auto it=asg.find(std::abs(lit));
            if(it!=asg.end() && it->second==(lit>0)) {ok=true;break;}
        }
        if(!ok) return false;
    }
    return true;
}
inline CNF simplify(CNF formula,int variable,bool value) {
    int yes=value?variable:-variable,no=-yes;
    CNF filtered;
    for(const auto& clause:formula) {
        if(std::find(clause.begin(),clause.end(),yes)!=clause.end()) continue;
        std::vector<int> reduced;
        for(int lit:clause) if(lit!=no) reduced.push_back(lit);
        filtered.push_back(std::move(reduced));
    }
    return filtered;
}
inline std::optional<Assignment> dpll(CNF formula) {
    for(const auto& clause:formula) for(int lit:clause)
        if(lit==0 || lit==std::numeric_limits<int>::min())
            throw std::invalid_argument("invalid CNF literal");
    std::function<std::optional<Assignment>(CNF,Assignment)> visit = [&](CNF cnf,Assignment asg)->std::optional<Assignment> {
        while(true) {
            if(cnf.empty()) return asg;
            for(const auto& c:cnf) if(c.empty()) return std::nullopt;
            std::optional<int> unit;
            for(const auto& c:cnf) if(c.size()==1) {unit=c[0];break;}
            if(!unit) break;
            auto var=std::abs(*unit);bool value=*unit>0;
            if(asg.count(var) && asg[var]!=value) return std::nullopt;
            asg[var]=value;
            cnf=simplify(std::move(cnf),var,value);
        }
        int chosen=std::numeric_limits<int>::max();
        for(const auto& clause:cnf) for(int lit:clause)
            chosen=std::min(chosen,std::abs(lit));
        for(bool value:{true,false}) {
            auto child=asg; child[chosen]=value;
            auto result=visit(simplify(cnf,chosen,value),std::move(child));
            if(result) return result;
        }
        return std::nullopt;
    };
    return visit(std::move(formula),{});
}
} // namespace alg
