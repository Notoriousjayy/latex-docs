#include <cassert>
#include <string>
#include <vector>
#include <set>
struct Event { std::string session_id;std::string type;int time_ms; };
bool collect(bool consent,Event e,std::vector<Event>& store){
    const std::set<std::string> allowed={"start","move","finish","hint"};
    if(!consent || !allowed.count(e.type) || e.session_id.empty() || e.time_ms<0)
        return false;
    store.push_back(e);return true;
}
int main(){
    std::vector<Event> items;
    Event e{"s1","move",12};
    assert(!collect(false,e,items) && items.empty());
    assert(collect(true,e,items) && items.size()==1);
    assert(!collect(true,{"s1","email",13},items));
    items.clear();assert(items.empty());
}
