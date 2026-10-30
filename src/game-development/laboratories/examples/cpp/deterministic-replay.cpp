#include <cassert>
#include <stdexcept>
#include <string>
#include <vector>
int replay(int score,const std::vector<std::string>& commands){
    for(const auto& command: commands){
        int delta=0;
        if(command=="gain")delta=2;
        else if(command=="spend")delta=-1;
        else throw std::invalid_argument("command");
        if(score+delta<0)throw std::invalid_argument("balance");
        score+=delta;
    }
    return score;
}
int main(){
    std::vector<std::string> cmds={"gain","spend","gain"};
    assert(replay(0,cmds)==3);
    assert(replay(0,cmds)==replay(0,cmds));
    bool rejected=false;
    try{(void)replay(0,{"spend"});}
    catch(const std::invalid_argument&){rejected=true;}
    assert(rejected);
}
