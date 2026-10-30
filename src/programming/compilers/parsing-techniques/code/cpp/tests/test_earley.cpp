#include "earley.hpp"
#include <cassert>
#include <iostream>
#include <stdexcept>
int main() {
    using namespace parsing;
    const std::vector<Rule> balanced={{"S",{"a","S","b"}},{"S",{}}};
    assert(earley_recognize(balanced,"S",{}));
    assert(earley_recognize(balanced,"S",{"a","b"}));
    assert(earley_recognize(balanced,"S",{"a","a","b","b"}));
    assert(!earley_recognize(balanced,"S",{"a","a","b"}));
    assert(!earley_recognize(balanced,"S",{"a","b","b"}));
    const std::vector<Rule> nullable={{"S",{"A","A"}},{"A",{}}};
    assert(earley_recognize(nullable,"S",{}));
    const std::vector<Rule> cycle={{"S",{"A"}},{"A",{"A"}},{"A",{}}};
    assert(earley_recognize(cycle,"S",{}));
    assert(!earley_recognize(cycle,"S",{"a"}));
    try { (void)earley_recognize(balanced,"S",{"a","b"},1);assert(false); }
    catch (const std::length_error&) {}
    std::cout << "Earley test cases passed\n";
}
