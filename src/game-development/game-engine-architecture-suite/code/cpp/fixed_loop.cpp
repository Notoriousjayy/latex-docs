#include <algorithm>
#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>

struct State { double x=0.0, velocity=3.0; int steps=0; };
void tick(State& s, double dt) { s.x+=s.velocity*dt; ++s.steps; }
State replay(const std::vector<int>& render_frames_ms) {
    // All inputs are integral microseconds to avoid accumulator rounding drift.
    constexpr int tick_us=10'000;
    int accumulator=0;
    State s;
    for(int frame_ms:render_frames_ms) {
        assert(frame_ms>=0);
        accumulator+=frame_ms*1000;
        while(accumulator>=tick_us) { tick(s, 0.01); accumulator-=tick_us; }
    }
    return s;
}
int main() {
    auto a=replay(std::vector<int>(100,10));
    auto b=replay(std::vector<int>(50,20));
    assert(a.steps==100 && b.steps==100);
    assert(std::abs(a.x-b.x)<1e-12);
    std::cout<<"ticks="<<a.steps<<" x="<<a.x<<"\n";
}
