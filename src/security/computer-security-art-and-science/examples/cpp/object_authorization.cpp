// Original, isolated C++17 exercise: never trust an object identifier alone.
#include <cassert>
#include <map>
#include <optional>
#include <string>
#include <utility>

struct Document {
    std::string tenant;
    std::string content;
};
using Documents = std::map<std::string, Document>;

std::optional<std::string> read_document(const Documents& documents,
                                         const std::string& tenant,
                                         const std::string& id)
{
    const auto it = documents.find(id);
    if (it == documents.end() || it->second.tenant != tenant) {
        return std::nullopt;
    }
    return it->second.content;
}

int main()
{
    const Documents docs{
        {"doc-a", {"tenant-a", "public synthetic example"}},
        {"doc-b", {"tenant-b", "private synthetic example"}}
    };
    assert(read_document(docs, "tenant-a", "doc-a").has_value());
    assert(!read_document(docs, "tenant-a", "doc-b").has_value());
    assert(!read_document(docs, "tenant-b", "doc-a").has_value());
    assert(!read_document(docs, "tenant-a", "missing").has_value());
}
