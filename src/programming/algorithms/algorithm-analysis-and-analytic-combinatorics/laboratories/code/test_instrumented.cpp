#define ANALYSIS_LIB_ONLY
#include "instrumented_analysis.cpp"
#include <iostream>
int main() {
    for (int n=0; n<=7; ++n) {
        std::vector<int> p(static_cast<std::size_t>(n));
        std::iota(p.begin(), p.end(), 0);
        do {
            auto a=p, b=p;
            (void)merge_sort(a);
            const auto result=insertion_sort(b);
            if (!std::is_sorted(a.begin(), a.end()) ||
                !std::is_sorted(b.begin(), b.end()) ||
                result.shifts != inversion_oracle(p)) {
                std::cerr << "sort/inversion invariant failure at n=" << n << "\n";
                return 1;
            }
        } while (std::next_permutation(p.begin(), p.end()));
    }
    for (auto b : {1U, 4U, 16U}) {
        const auto result=occupancy(512,b,71);
        if (result.colliding_pairs > 512ULL*511/2) {
            std::cerr << "occupancy invariant failure\n";
            return 1;
        }
    }
    std::cout << "All C++ invariants passed\n";
    return 0;
}
