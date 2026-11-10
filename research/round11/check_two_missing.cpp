// Independent geometry check. Fix the missing directions to basis vectors 1,2,
// then enumerate every allowed occupancy of the eight plane cosets.
#include <array>
#include <cstdint>
#include <iostream>
#include <stdexcept>

constexpr std::array<unsigned, 7> choices{0, 1, 2, 4, 8, 9, 6};

class Enumeration {
public:
    void visit(unsigned coset, unsigned count, std::uint32_t heavy) {
        if (count > 10 || count + 2 * (8 - coset) < 10) {
            return;
        }
        if (coset == 8) {
            check(heavy);
            return;
        }
        for (unsigned choice : choices) {
            const unsigned points = choice == 0 ? 0 : (choice == 9 || choice == 6 ? 2 : 1);
            visit(coset + 1, count + points, heavy | (std::uint32_t{choice} << (4 * coset)));
        }
    }

    void print() const {
        if (tested != 1141504 || exact == 0) {
            throw std::runtime_error("Unexpected size of independent enumeration");
        }
        std::cout << "Fixed-pair heavy sets checked = " << tested << '\n'
                  << "With exactly two missing differences = " << exact << '\n'
                  << "All heavy vertices meet a unique edge outside the missing plane\n";
    }

private:
    std::uint64_t tested = 0;
    std::uint64_t exact = 0;

    void check(std::uint32_t heavy) {
        ++tested;
        std::uint32_t touched = 0;
        bool more_missing = false;
        for (unsigned d = 3; d < 32; ++d) {
            std::uint32_t endpoints = 0;
            unsigned pairs = 0;
            for (unsigned a = 0; a < 32; ++a) {
                const unsigned b = a ^ d;
                if (a < b && ((heavy >> a) & 1) && ((heavy >> b) & 1)) {
                    ++pairs;
                    endpoints |= (std::uint32_t{1} << a) | (std::uint32_t{1} << b);
                }
            }
            more_missing |= (pairs == 0);
            if (d != 3 && pairs == 1) {
                touched |= endpoints;
            }
        }
        if (!more_missing) {
            ++exact;
            if (touched != heavy) {
                throw std::runtime_error("Counterexample to the private-edge geometry");
            }
        }
    }
};

int main() {
    Enumeration enumeration;
    enumeration.visit(0, 0, 0);
    enumeration.print();
}
