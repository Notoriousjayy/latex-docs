#include <cassert>
#include <stdexcept>
#include <string>
struct Game { std::string mode = "menu"; int health = 3; };
Game apply(Game s, const std::string& action) {
    if (s.mode == "menu" && action == "start") s.mode = "playing";
    else if (s.mode == "playing" && action == "pause") s.mode = "paused";
    else if (s.mode == "paused" && action == "resume") s.mode = "playing";
    else if (s.mode == "playing" && action == "finish") s.mode = "won";
    else throw std::invalid_argument("invalid transition");
    return s;
}
int main() {
    Game initial;
    auto s = apply(initial, "start");
    assert(s.mode == "playing" && s.health == 3);
    bool rejected = false;
    try { (void)apply(s, "resume"); } catch (const std::invalid_argument&) { rejected = true; }
    assert(rejected);
    assert(apply(apply(s, "pause"), "resume").mode == s.mode);
}
