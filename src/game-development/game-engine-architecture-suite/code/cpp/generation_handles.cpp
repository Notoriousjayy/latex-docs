#include <cassert>
#include <cstdint>
#include <iostream>
#include <optional>
#include <vector>
struct Handle { std::uint32_t slot; std::uint32_t generation; };
struct Slot { std::uint32_t generation=1; bool live=false; int payload=0; };
class Resources {
    std::vector<Slot> slots_;
public:
    Handle create(int value) {
        for(std::uint32_t i=0;i<slots_.size();++i) if(!slots_[i].live) {
            auto& s=slots_[i]; s.live=true; s.payload=value; return {i,s.generation};
        }
        slots_.push_back({1,true,value});
        return {static_cast<std::uint32_t>(slots_.size()-1),1};
    }
    std::optional<int> get(Handle h) const {
        if(h.slot>=slots_.size()) return std::nullopt;
        auto& s=slots_[h.slot];
        if(!s.live || s.generation!=h.generation) return std::nullopt;
        return s.payload;
    }
    bool erase(Handle h) {
        if(!get(h)) return false;
        auto& s=slots_[h.slot]; s.live=false;
        ++s.generation;
        if(s.generation==0) ++s.generation; // generation exhaustion needs wider IDs in production
        return true;
    }
};
int main() {
    Resources r; auto h1=r.create(4);
    assert(r.get(h1).value()==4);
    assert(r.erase(h1)); assert(!r.erase(h1));
    auto h2=r.create(7); assert(h1.slot==h2.slot);
    assert(h1.generation!=h2.generation && !r.get(h1));
    std::cout<<"stale resource handles rejected\n";
}
