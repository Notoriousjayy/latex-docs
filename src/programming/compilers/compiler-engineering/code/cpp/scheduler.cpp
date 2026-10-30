// Original simple one-issue list scheduler; dependency DAG with explicit latencies.
#include <cassert>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
struct Op {std::string id; int latency; std::vector<std::string> deps;};
struct Slot {std::string id; int issue;};
std::vector<Slot> schedule(const std::vector<Op>& ops) {
    std::map<std::string,Op> nodes;
    for (const auto& op:ops) {
        if(op.latency<1 || !nodes.emplace(op.id,op).second)
            throw std::invalid_argument("nonpositive latency or duplicate instruction");
    }
    for (const auto& op:ops) for(const auto& dep:op.deps)
        if(!nodes.contains(dep) || dep==op.id)throw std::invalid_argument("invalid dependency");
    std::map<std::string,int> issued;
    std::vector<Slot> result;
    int cycle=0;
    while(result.size()<ops.size()) {
        bool any=false;
        for(const auto& op:ops){
            if(issued.contains(op.id))continue;
            bool ready=true;
            for(const auto& dep:op.deps){
                if(!issued.contains(dep) || cycle<issued[dep]+nodes.at(dep).latency) {
                    ready=false;break;
                }
            }
            if(ready){
                issued[op.id]=cycle; result.push_back({op.id,cycle});any=true;break;
            }
        }
        if(!any && cycle>static_cast<int>(ops.size())*1000)
            throw std::invalid_argument("cycle in dependency graph or unreasonable latency");
        ++cycle;
    }
    return result;
}
int main() {
    std::vector<Op> ops={{"load",3,{}},{"add",1,{"load"}},{"mul",2,{"add"}}, {"independent",1,{}}};
    auto x=schedule(ops);
    std::map<std::string,int> starts;
    for(const auto& a:x)starts[a.id]=a.issue;
    assert(starts["add"]>=starts["load"]+3);
    assert(starts["mul"]>=starts["add"]+1);
    assert(starts["independent"]>starts["load"]);
    try{(void)schedule({{"a",1,{"b"}},{"b",1,{"a"}}});assert(false);}
    catch(const std::invalid_argument&){}
    std::cout<<"C++20 list-scheduler tests passed\n";
}
