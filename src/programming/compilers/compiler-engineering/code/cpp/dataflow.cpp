// C++20 liveness model: original, intentionally compact teaching reference.
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

using Names=std::set<std::string>;
struct Block {
    std::string id;
    std::vector<std::string> successors;
    Names uses;
    Names defs;
};
struct Result {
    std::map<std::string,Names> in;
    std::map<std::string,Names> out;
    size_t iterations=0;
};
Result liveness(const std::vector<Block>& blocks) {
    std::set<std::string> ids;
    for(const auto& b:blocks) {
        if(!ids.insert(b.id).second) throw std::invalid_argument("duplicate block id");
    }
    for(const auto& b:blocks)
        for(const auto& s:b.successors)
            if(!ids.contains(s)) throw std::invalid_argument("unknown successor");
    Result state;
    for(const auto& id:ids){state.in[id]={};state.out[id]={};}
    bool changed=true;
    while(changed) {
        changed=false; ++state.iterations;
        for(auto it=blocks.rbegin();it!=blocks.rend();++it) {
            const auto& b=*it;
            Names out;
            for(const auto& succ:b.successors)
                out.insert(state.in.at(succ).begin(),state.in.at(succ).end());
            Names in=b.uses;
            for(const auto& n:out) if(!b.defs.contains(n)) in.insert(n);
            if(state.in.at(b.id)!=in || state.out.at(b.id)!=out) {
                state.in[b.id]=std::move(in);
                state.out[b.id]=std::move(out);
                changed=true;
            }
        }
    }
    return state;
}
int main() {
    const std::vector<Block> g={
        {"entry",{"left","right"},{},{"x"}},
        {"left",{"join"},{"x"},{}},
        {"right",{"join"},{"x"},{}},
        {"join",{},{},{}},
    };
    auto r=liveness(g);
    assert(r.in.at("entry").empty());
    assert(r.out.at("entry")==Names{"x"});
    assert(r.in.at("left")==Names{"x"});
    assert(r.iterations>=2);
    try {liveness({{"broken",{"missing"},{},{}}}); assert(false);}
    catch(const std::invalid_argument&) {}
    std::cout<<"C++20 dataflow tests passed; iterations="<<r.iterations<<'\n';
}
