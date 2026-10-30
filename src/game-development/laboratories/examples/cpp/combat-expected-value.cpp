#include <cassert>
#include <cmath>
#include <vector>
#include <utility>
struct Moments { double mean; double variance; };
Moments moments(const std::vector<std::pair<double,double>>& outcomes) {
    double total = 0, mean = 0, variance = 0;
    for (auto const& [x,p] : outcomes) { total += p; mean += x*p; }
    assert(std::abs(total - 1.0) < 1e-10);
    for (auto const& [x,p] : outcomes) variance += p*(x-mean)*(x-mean);
    return {mean,variance};
}
int main() {
    auto a=moments({{3,.85},{0,.15}}),b=moments({{6,.45},{0,.55}});
    assert(std::abs(a.mean-2.55)<1e-10);
    assert(std::abs(b.mean-2.70)<1e-10);
    assert(b.variance>a.variance);
}
