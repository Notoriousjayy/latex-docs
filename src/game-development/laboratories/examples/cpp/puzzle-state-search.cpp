#include <cassert>
#include <queue>
#include <set>
#include <map>
#include <utility>
#include <vector>
using Cell=std::pair<int,int>;
std::vector<Cell> shortest(Cell start,Cell goal,const std::set<Cell>& blocked,int width=3){
    std::queue<Cell> q;std::map<Cell,Cell> parent;std::set<Cell> seen;
    q.push(start); seen.insert(start);
    while(!q.empty()){
        Cell c=q.front();q.pop();
        if(c==goal){
            std::vector<Cell> path;
            while(c!=start){ path.push_back(c); c=parent[c]; }
            path.push_back(start);
            return std::vector<Cell>(path.rbegin(),path.rend());
        }
        for(Cell v: {Cell{c.first+1,c.second},Cell{c.first,c.second+1},
                     Cell{c.first-1,c.second},Cell{c.first,c.second-1}}){
            if(v.first>=0 && v.second>=0 && v.first<width && v.second<width
                && !blocked.count(v) && !seen.count(v)){
                seen.insert(v);parent[v]=c;q.push(v);
            }
        }
    }
    return {};
}
int main(){
    assert(shortest({0,0},{2,2},{{1,1}}).size()==5);
    assert(shortest({0,0},{2,2},{{0,1},{1,0}}).empty());
}
