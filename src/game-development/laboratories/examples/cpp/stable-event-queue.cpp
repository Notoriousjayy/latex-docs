#include <cassert>
#include <queue>
#include <string>
#include <vector>
#include <tuple>
#include <functional>
using Event=std::tuple<int,int,std::string>;
int main(){
    std::priority_queue<Event,std::vector<Event>,std::greater<Event>> q;
    int id=0;
    q.emplace(3,id++,"A");q.emplace(1,id++,"B");q.emplace(3,id++,"C");
    std::vector<std::string> got;
    while(!q.empty()){got.push_back(std::get<2>(q.top()));q.pop();}
    assert((got==std::vector<std::string>{"B","A","C"}));
}
