// Exhaustive normalized marked-support census. No affine-orbit file is used.
// Build: g++ -O3 -std=c++17 build_unique_edge_role_census.cpp -o build_unique_edge_role_census
// Run: ./build_unique_edge_role_census > UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <vector>

struct Entry {
    std::uint64_t multiplicity = 0;
    std::uint32_t witness = 0;
};

struct Census {
    int size;
    std::uint64_t visited = 0, covering = 0;
    std::vector<int> points{0, 1, 2, 4, 8, 16};
    std::vector<int> choices;
    std::map<std::array<int, 4>, Entry> patterns;

    explicit Census(int n) : size(n) {
        for (int x = 0; x < 32; ++x) {
            bool fixed = false;
            for (int y : points) fixed |= (x == y);
            if (!fixed) choices.push_back(x);
        }
    }

    void leaf() {
        ++visited;
        std::uint32_t mask = 0;
        for (int x : points) mask |= std::uint32_t(1) << x;
        int pairs[32] = {};
        for (int i = 0; i < size; ++i)
            for (int j = 0; j < i; ++j) ++pairs[points[i] ^ points[j]];
        for (int d = 1; d < 32; ++d) if (!pairs[d]) return;
        ++covering;
        std::uint32_t forced_large = 0;
        for (int i = 0; i < size; ++i) {
            for (int j = 0; j < i; ++j) {
                int d = points[i] ^ points[j];
                if (!(mask & (std::uint32_t(1) << d)) && pairs[d] == 1) {
                    forced_large |= std::uint32_t(1) << points[i];
                    forced_large |= std::uint32_t(1) << points[j];
                }
            }
        }
        std::array<int, 4> role{};
        for (int x : points) {
            if (!x) continue;
            int type = int((forced_large >> x) & 1U) + 2 * int(pairs[x] == 1);
            ++role[type];
        }
        Entry& e = patterns[role];
        if (!e.multiplicity) e.witness = mask;
        ++e.multiplicity;
    }

    void visit(int next, int need) {
        if (!need) { leaf(); return; }
        for (int i = next; i <= int(choices.size()) - need; ++i) {
            points.push_back(choices[i]);
            visit(i + 1, need - 1);
            points.pop_back();
        }
    }

    void print() const {
        std::cout << "{\"normalized_sets_visited\":" << visited
                  << ",\"covering_normalized_sets\":" << covering
                  << ",\"patterns\":[";
        bool first = true;
        for (const auto& [role, e] : patterns) {
            if (!first) std::cout << ',';
            first = false;
            std::cout << "{\"counts\":[" << role[0] << ',' << role[1] << ','
                      << role[2] << ',' << role[3]
                      << "],\"normalized_multiplicity\":" << e.multiplicity
                      << ",\"witness_mask\":" << e.witness << '}';
        }
        std::cout << "]}";
    }
};

int main() {
    Census a(11), b(12);
    a.visit(0, 5);
    b.visit(0, 6);
    std::cout << "{\"schema\":\"unique-edge-role-census-v1\","
                 "\"normalization_base\":[0,1,2,4,8,16],"
                 "\"role_order\":[\"neither\",\"large_only\",\"sole_hub_only\",\"both\"],"
                 "\"supports\":{\"11\":";
    a.print();
    std::cout << ",\"12\":";
    b.print();
    std::cout << "}}\n";
}
