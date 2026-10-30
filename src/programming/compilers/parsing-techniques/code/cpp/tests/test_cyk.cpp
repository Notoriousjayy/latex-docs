#include "cyk.hpp"
#include <cassert>
#include <stdexcept>
#include <vector>
#include <iostream>
int main() {
    using namespace parsing;
    const std::vector<Rule> grammar={{"S",{"A","B"}},{"A",{"a"}},{"B",{"b"}}};
    assert(cyk_recognize(grammar,"S",{"a","b"}));
    assert(!cyk_recognize(grammar,"S",{"b","a"}));
    assert(!cyk_recognize(grammar,"S",{}));
    try { (void)cyk_recognize(grammar,"S",{"a","b"},1);assert(false); }
    catch (const std::length_error&) {}
    try { (void)cyk_recognize({{"S",{}}},"S",{});assert(false); }
    catch (const std::invalid_argument&) {}
    std::cout << "CYK test cases passed\n";
}
