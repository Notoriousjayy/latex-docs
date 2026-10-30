#include "cyk.hpp"
#include <map>
#include <set>
#include <utility>
namespace parsing {
bool cyk_recognize(const std::vector<Rule>& rules, const std::string& start,
                   const std::vector<std::string>& tokens,
                   std::size_t max_tokens, std::size_t max_cells) {
    using Strings = std::set<std::string>;
    Strings nonterminals;
    for (const auto& rule : rules) {
        if (rule.lhs.empty()) throw std::invalid_argument("empty LHS");
        nonterminals.insert(rule.lhs);
    }
    if (!nonterminals.count(start)) throw std::invalid_argument("undefined start");
    std::map<std::string, Strings> terminal_rules;
    std::map<std::pair<std::string,std::string>, Strings> binary_rules;
    for (const auto& rule : rules) {
        if (rule.rhs.size() == 1 && !rule.rhs[0].empty() && !nonterminals.count(rule.rhs[0])) {
            terminal_rules[rule.rhs[0]].insert(rule.lhs);
        } else if (rule.rhs.size() == 2 && nonterminals.count(rule.rhs[0]) && nonterminals.count(rule.rhs[1])) {
            binary_rules[{rule.rhs[0],rule.rhs[1]}].insert(rule.lhs);
        } else throw std::invalid_argument("strict CNF required");
    }
    const auto n = tokens.size();
    if (n > max_tokens || (n > 0 && n > (2*max_cells)/(n+1)))
        throw std::length_error("resource limit exceeded");
    if (n == 0) return false;
    std::vector<std::vector<Strings>> chart(n, std::vector<Strings>(n+1));
    for (std::size_t i=0;i<n;i++) {
        const auto it=terminal_rules.find(tokens[i]);
        if (it!=terminal_rules.end()) chart[i][i+1]=it->second;
    }
    for (std::size_t length=2;length<=n;length++) {
        for (std::size_t i=0;i+length<=n;i++) {
            const auto j=i+length;
            for (std::size_t k=i+1;k<j;k++) {
                for (const auto& a:chart[i][k]) for (const auto& b:chart[k][j]) {
                    const auto it=binary_rules.find({a,b});
                    if (it!=binary_rules.end()) chart[i][j].insert(it->second.begin(),it->second.end());
                }
            }
        }
    }
    return chart[0][n].count(start)>0;
}
}
