#pragma once
#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>

namespace parsing {
struct Rule {
    std::string lhs;
    std::vector<std::string> rhs;
};
// Deliberately strict-CNF recognizer. Empty input rejects. Throws on malformed
// grammars and resource budget violations; does not build a parse forest.
bool cyk_recognize(const std::vector<Rule>& rules, const std::string& start,
                   const std::vector<std::string>& tokens,
                   std::size_t max_tokens = 256, std::size_t max_cells = 65536);
}
