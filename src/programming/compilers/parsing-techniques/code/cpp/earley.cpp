#include "earley.hpp"
#include <map>
#include <set>
#include <stdexcept>
#include <utility>
#include <tuple>
#include <vector>
namespace parsing {
namespace {
struct Item {
    std::string lhs;
    std::vector<std::string> rhs;
    std::size_t dot=0, origin=0;
    bool operator<(const Item& o) const {
        return std::tie(lhs,rhs,dot,origin) < std::tie(o.lhs,o.rhs,o.dot,o.origin);
    }
};
}
bool earley_recognize(const std::vector<Rule>& grammar,const std::string& start,
                      const std::vector<std::string>& tokens,
                      std::size_t max_tokens,std::size_t max_items) {
    std::map<std::string,std::vector<std::vector<std::string>>> productions;
    for (const auto& rule: grammar) {
        if (rule.lhs.empty()) throw std::invalid_argument("empty LHS");
        productions[rule.lhs].push_back(rule.rhs);
    }
    if (!productions.count(start)) throw std::invalid_argument("undefined start");
    if (tokens.size() > max_tokens) throw std::length_error("token limit exceeded");
    auto root = start + "'";
    while (productions.count(root)) root += "'";
    const auto n=tokens.size();
    std::vector<std::set<Item>> chart(n+1);
    Item initial{root,{start},0,0};
    chart[0].insert(initial);
    std::size_t total_items=1;
    for (std::size_t pos=0;pos<=n;pos++) {
        std::vector<Item> agenda(chart[pos].begin(),chart[pos].end());
        auto add=[&](std::size_t dest, const Item& item) {
            if (chart[dest].insert(item).second) {
                if (++total_items > max_items) throw std::length_error("item limit exceeded");
                if (dest==pos) agenda.push_back(item);
            }
        };
        for (std::size_t ix=0;ix<agenda.size();ix++) {
            const auto item=agenda[ix];
            if (item.dot==item.rhs.size()) {
                // Completion, including nullable zero-span completion.
                const auto candidates=std::vector<Item>(chart[item.origin].begin(),chart[item.origin].end());
                for (const auto& waiting:candidates)
                    if (waiting.dot < waiting.rhs.size() && waiting.rhs[waiting.dot]==item.lhs)
                        add(pos,{waiting.lhs,waiting.rhs,waiting.dot+1,waiting.origin});
            } else {
                const auto& next=item.rhs[item.dot];
                const auto predict=productions.find(next);
                if (predict!=productions.end()) {
                    for (const auto& rhs:predict->second) add(pos,{next,rhs,0,pos});
                    // Late arrival of a waiting item after nullable completion.
                    const auto completed=std::vector<Item>(chart[pos].begin(),chart[pos].end());
                    for (const auto& done:completed)
                        if (done.lhs==next && done.dot==done.rhs.size() && done.origin==pos)
                            add(pos,{item.lhs,item.rhs,item.dot+1,item.origin});
                } else if (pos<n && next==tokens[pos]) {
                    add(pos+1,{item.lhs,item.rhs,item.dot+1,item.origin});
                }
            }
        }
    }
    return chart[n].count({root,{start},1,0})!=0;
}
}
