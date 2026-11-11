// Group marked support masks using the maintained GL(5,2) canonicalizer.
// Compile with -I pointing at the archived imported_claude_round4/src.
#define main inherited_catalogue_main
#include "orbits_all.cpp"
#undef main

int main(int argc, char** argv) {
    if (argc != 2 && argc != 3) {
        std::cerr << "usage: group_affine_orbits ORBITS_ALL_TXT [M11_REPRESENTATIVES_TXT]\n";
        return 2;
    }
    std::ifstream catalogue(argv[1]);
    std::map<int, std::set<u32>> covering;
    int nonzero_count, cover;
    long stabilizer;
    u32 mask;
    while (catalogue >> nonzero_count >> mask >> stabilizer >> cover) {
        if (cover == 1 && nonzero_count >= 12 && nonzero_count <= 16) {
            covering[nonzero_count + 1].insert(mask);
        }
    }
    if (!catalogue.eof() || covering.size() != 5) {
        throw std::runtime_error("Incomplete marked catalogue");
    }
    std::map<u32, u32> affine_group;
    for (const auto& [support, masks] : covering) {
        auto remaining = masks;
        while (!remaining.empty()) {
            const u32 representative = *remaining.begin();
            const u32 full = representative | 1u;
            std::set<u32> group;
            for (unsigned hub = 0; hub < 32; ++hub) {
                if (!((full >> hub) & 1)) {
                    continue;
                }
                u32 translated = 0;
                for (unsigned a = 0; a < 32; ++a) {
                    if (a != hub && ((full >> a) & 1)) {
                        translated |= 1u << (a ^ hub);
                    }
                }
                group.insert(canon(translated).first);
            }
            if (*group.begin() != representative) {
                throw std::runtime_error("Invalid affine group minimum");
            }
            std::cout << support << ' ' << representative;
            for (u32 role : group) {
                if (remaining.erase(role) != 1) {
                    throw std::runtime_error("Affine grouping left the marked catalogue or overlapped");
                }
                affine_group.emplace(role, representative);
                std::cout << ' ' << role;
            }
            std::cout << '\n';
        }
    }
    if (argc == 3) {
        std::ifstream representatives(argv[2]);
        unsigned support, orbit;
        u32 full;
        while (representatives >> support >> orbit >> full) {
            if (full == 0 || __builtin_popcount(full) != static_cast<int>(support)) {
                throw std::runtime_error("Invalid maximum-11 representative");
            }
            const unsigned hub = __builtin_ctz(full);
            u32 translated = 0;
            for (unsigned a = 0; a < 32; ++a) {
                if (a != hub && ((full >> a) & 1)) {
                    translated |= 1u << (a ^ hub);
                }
            }
            const u32 marked = canon(translated).first;
            std::cout << "M11 " << support << ' ' << orbit << ' '
                      << affine_group.at(marked) << ' ' << marked << '\n';
        }
        if (!representatives.eof()) {
            throw std::runtime_error("Invalid maximum-11 input");
        }
    }

}
