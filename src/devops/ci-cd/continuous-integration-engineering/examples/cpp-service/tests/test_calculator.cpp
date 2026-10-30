#include "calculator.hpp"
#include <exception>
#include <limits>
#include <stdexcept>
int main() {
    if (ci::add(2, 3) != 5 || ci::factorial(5) != 120) return 1;
    try { (void)ci::factorial(-1); return 2; }
    catch (const std::out_of_range&) {}
    try { (void)ci::add(std::numeric_limits<int>::max(), 1); return 3; }
    catch (const std::overflow_error&) {}
    return 0;
}
