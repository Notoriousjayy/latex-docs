// Original greedy graph coloring demonstration. Spills are explicit, not rewritten.
#include <cassert>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
using Graph=std::map<std::string,std::set<std::string>>;
std::map<std::string,int> color(const Graph& g,int registers){
    if(registers<1) throw std::invalid_argument("register count must be positive");
    for(const auto& [node,neighbors]:g)
        for(const auto& other:neighbors)
            if(node==other || !g.contains(other) || !g.at(other).contains(node))
                throw std::invalid_argument("interference graph must be symmetric and loop-free");
    std::map<std::string,int> colors;
    for(const auto& [node,neighbors]:g){
        std::set<int> occupied;
        for(const auto& neighbor:neighbors) if(colors.contains(neighbor) && colors.at(neighbor)>=0)
            occupied.insert(colors.at(neighbor));
        int c=0;
        while(c<registers && occupied.contains(c))++c;
        colors[node]=c==registers ? -1 : c; // -1 means spill candidate
    }
    return colors;
}
int main(){
    Graph g={{"a",{"b","d"}},{"b",{"a","c"}},{"c",{"b","d"}},{"d",{"a","c"}}};
    auto m=color(g,2);
    for(const auto& [n,adj]:g)
       for(const auto& peer:adj)assert(m.at(n)<0 || m.at(peer)<0 || m.at(n)!=m.at(peer));
    for(const auto& [n,c]:m)assert(c>=0);
    Graph triangle={{"a",{"b","c"}},{"b",{"a","c"}},{"c",{"a","b"}}};
    auto tri=color(triangle,2);
    assert(tri.at("c")==-1);
    std::cout<<"C++20 graph-coloring tests passed (spill indicated, no code rewriting)\n";
}
