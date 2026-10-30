#pragma once
#include "cyk.hpp"
#include <cstddef>
#include <string>
#include <vector>
namespace parsing {
// Earley recognition, including epsilon rules and left recursion.
// Returns membership only; no parse forest is constructed.
bool earley_recognize(const std::vector<Rule>& grammar,
                      const std::string& start,
                      const std::vector<std::string>& tokens,
                      std::size_t max_tokens = 256,
                      std::size_t max_items = 100000);
}
