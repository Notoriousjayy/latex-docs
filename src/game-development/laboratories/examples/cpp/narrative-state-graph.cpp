#include <cassert>
#include <stdexcept>
#include <string>
struct Story{bool clue=false,trusted=false;};
Story choose(Story s,const std::string& command){
    if(command=="investigate")s.clue=true;
    else if(command=="confide" && s.clue)s.trusted=true;
    else throw std::invalid_argument("locked choice");
    return s;
}
std::string ending(Story s){return s.trusted?"alliance":"isolation";}
int main(){
    Story s;
    bool rejected=false;
    try{(void)choose(s,"confide");}
    catch(const std::invalid_argument&){rejected=true;}
    assert(rejected);
    assert(ending(choose(choose(s,"investigate"),"confide"))=="alliance");
}
