#include "calculator.hpp"
#include <limits>
#include <stdexcept>
namespace ci {
int add(int a, int b) {
    long long r = static_cast<long long>(a) + static_cast<long long>(b);
    if (r > std::numeric_limits<int>::max() || r < std::numeric_limits<int>::min())
        throw std::overflow_error("sum overflow");
    return static_cast<int>(r);
}
int factorial(int n) {
    if (n < 0 || n > 12) throw std::out_of_range("factorial bound");
    int r = 1;
    for (int i = 2; i <= n; ++i) r *= i;
    return r;
}
}
