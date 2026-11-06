// Independent complete Q_max(12) check in F_2^5.
// This program reads no census, orbit list, or earlier producer output.
// It counts affine planes directly from triples and independently accumulates
// unordered-pair differences. Completeness uses affine-basis normalization.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <stdexcept>
#include <vector>

struct Result {
    int rank;
    uint64_t visited = 0;
    int max_energy = -1;
    int max_planes = -1;
    uint64_t maximizers = 0;
    std::vector<int> witness;
    std::map<int,uint64_t> energy_histogram;
};

static void examine(std::vector<int> a, Result& result) {
    std::sort(a.begin(),a.end());
    if (a.size()!=12) throw std::runtime_error("wrong set size");
    uint32_t mask=0;
    for (int x:a) mask |= uint32_t(1)<<x;
    std::array<int,32> pair_counts{};
    for (int i=0;i<12;++i)
        for (int j=i+1;j<12;++j)
            ++pair_counts[a[i]^a[j]];
    int pair_mass=0, energy=0;
    for(int d=1;d<32;++d) {
        pair_mass+=pair_counts[d];
        energy+=pair_counts[d]*pair_counts[d];
    }
    if(pair_mass!=66) throw std::runtime_error("wrong pair mass");
    // A binary affine plane has four distinct points with xor zero.
    // For its three smallest points, the fourth exceeds the third.
    // Exactly this triple is counted; no division or pair-count formula.
    int planes=0;
    for(int i=0;i<12;++i)
        for(int j=i+1;j<12;++j)
            for(int k=j+1;k<12;++k) {
                int fourth=a[i]^a[j]^a[k];
                if(fourth>a[k] && (mask & (uint32_t(1)<<fourth))) ++planes;
            }
    if(energy!=66+6*planes) throw std::runtime_error("energy/plane disagreement");
    ++result.visited;
    ++result.energy_histogram[energy];
    if(energy>result.max_energy) {
        result.max_energy=energy;
        result.max_planes=planes;
        result.maximizers=1;
        result.witness=a;
    } else if(energy==result.max_energy) ++result.maximizers;
}

static void choose(const std::vector<int>& extra, int next, int remaining,
                   std::vector<int>& selected, Result& result) {
    if(!remaining) { examine(selected,result); return; }
    for(int i=next;i+remaining<=int(extra.size());++i) {
        selected.push_back(extra[i]);
        choose(extra,i+1,remaining-1,selected,result);
        selected.pop_back();
    }
}

static Result run(int rank) {
    Result result; result.rank=rank;
    std::vector<int> fixed{0};
    for(int j=0;j<rank;++j) fixed.push_back(1<<j);
    std::vector<int> extra;
    for(int x=0;x<(1<<rank);++x)
        if(std::find(fixed.begin(),fixed.end(),x)==fixed.end()) extra.push_back(x);
    choose(extra,0,12-int(fixed.size()),fixed,result);
    const uint64_t expected=rank==4?330:230230;
    if(result.visited!=expected) throw std::runtime_error("incomplete enumeration");
    return result;
}

static void print(const Result& r) {
    std::cout << "{\"affine_rank\":" << r.rank
              << ",\"normalized_sets_checked\":" << r.visited
              << ",\"maximum_energy\":" << r.max_energy
              << ",\"maximum_affine_planes\":" << r.max_planes
              << ",\"normalized_maximizers\":" << r.maximizers
              << ",\"witness\":[";
    for(size_t i=0;i<r.witness.size();++i) {
        if(i) std::cout<<','; std::cout<<r.witness[i];
    }
    std::cout << "],\"energy_histogram\":{";
    bool first=true;
    for(const auto& entry:r.energy_histogram) {
        if(!first) std::cout<<','; first=false;
        std::cout<<'"'<<entry.first<<"\":"<<entry.second;
    }
    std::cout<<"}}";
}

int main() {
    try {
        Result r4=run(4),r5=run(5);
        std::cout<<"{\"status\":\"PASS\",\"scope\":\"all twelve-point subsets of F2^5 by affine-basis normalization\",\"reads_prior_census\":false,\"ranks\":[";
        print(r4); std::cout<<','; print(r5);
        std::cout<<"],\"maximum_energy\":"<<std::max(r4.max_energy,r5.max_energy)
                 <<",\"total_normalized_sets_checked\":"<<r4.visited+r5.visited
                 <<",\"independent_counters\":[\"direct unordered-pair differences\",\"direct affine-plane triple completion\"]}\n";
    } catch(const std::exception& e) {
        std::cerr<<e.what()<<'\n'; return 1;
    }
}
