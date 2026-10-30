#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <new>
#include <vector>
class Arena {
    std::vector<std::byte> bytes_;
    std::size_t next_=0;
public:
    explicit Arena(std::size_t capacity):bytes_(capacity){}
    void* allocate(std::size_t n, std::size_t alignment) {
        if(alignment==0 || (alignment & (alignment-1))!=0) throw std::bad_alloc{};
        if(next_>bytes_.size()) throw std::bad_alloc{};
        const auto base=reinterpret_cast<std::uintptr_t>(bytes_.data());
        if(next_>std::numeric_limits<std::uintptr_t>::max()-base) throw std::bad_alloc{};
        auto current=base+next_;
        auto padding=(alignment-(current%alignment))%alignment;
        if(padding>bytes_.size()-next_) throw std::bad_alloc{};
        if(n>bytes_.size()-next_-padding) throw std::bad_alloc{};
        next_+=padding;
        void* out=bytes_.data()+next_;
        next_+=n;
        return out;
    }
    void reset() noexcept { next_=0; }  // invalidates every previous pointer!
};
int main() {
    Arena arena(128);
    auto* ptr=arena.allocate(8,32);
    assert(reinterpret_cast<std::uintptr_t>(ptr)%32==0);
    bool failed=false;
    try { arena.allocate(1024,8); } catch(const std::bad_alloc&) { failed=true; }
    assert(failed);
    arena.reset();
    auto* new_ptr=arena.allocate(16,16);
    assert(reinterpret_cast<std::uintptr_t>(new_ptr)%16==0);
    std::cout<<"arena: alignment, exhaustion and reset passed\n";
}
