// V2 extension of frozen V1 source46def4b2a670258f3da880c203ecc3df8b86c193b2cc8acd22496c7e98784e34.
// Adds the independently audited all-row paired-direction resource correction.
// Build: g++ -O3 -std=c++17 fast_resource_filter.cpp -lcrypto -o fast_resource_filter
// Input: exact native WITNESS/statistics stream. --profiles verifies every block.
// No output of this filter alone asserts complete maximum-fibre closure.
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <csignal>
#include <cstdio>
#include <cstdint>
#include <filesystem>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <openssl/evp.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

using namespace std;
namespace fs = std::filesystem;
static void require(bool yes, const string& message) { if (!yes) throw runtime_error(message); }

class Sha256 {
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    bool ended = false;
public:
    Sha256() { require(ctx && EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) == 1, "SHA256 init"); }
    ~Sha256() { EVP_MD_CTX_free(ctx); }
    void add(const string& text) { require(!ended && EVP_DigestUpdate(ctx, text.data(), text.size()) == 1, "SHA256 update"); }
    string finish() {
        require(!ended, "SHA256 finalized twice"); ended = true;
        unsigned char bytes[EVP_MAX_MD_SIZE]; unsigned count = 0;
        require(EVP_DigestFinal_ex(ctx, bytes, &count) == 1 && count == 32, "SHA256 final");
        ostringstream out; out << hex << setfill('0');
        for (unsigned i = 0; i < count; ++i) out << setw(2) << unsigned(bytes[i]);
        return out.str();
    }
};

static string file_hash(const fs::path& path) {
    ifstream in(path, ios::binary); require(bool(in), "Cannot read hash input: " + path.string());
    Sha256 hash; array<char, 1 << 16> buffer{};
    while (in) { in.read(buffer.data(), buffer.size()); if (in.gcount()) hash.add(string(buffer.data(), size_t(in.gcount()))); }
    require(in.eof(), "Read error hashing: " + path.string()); return hash.finish();
}

static string quote(const string& value) {
    string result = "\"";
    for (unsigned char c : value) {
        if (c == '"' || c == '\\') { result += '\\'; result += char(c); }
        else if (c == '\n') result += "\\n";
        else if (c == '\r') result += "\\r";
        else if (c == '\t') result += "\\t";
        else { require(c >= 32, "Unexpected control byte in JSON string"); result += char(c); }
    }
    return result + '"';
}

class HashedOutput {
    FILE* stream = nullptr;
    Sha256 hash;
    pid_t child = -1;
public:
    uint64_t bytes = 0;
    explicit HashedOutput(const fs::path& path, bool use_xz = false) {
        stream = fopen(path.c_str(), "wbx"); require(stream, "Cannot create: " + path.string());
        require(fcntl(fileno(stream), F_SETFD, FD_CLOEXEC) == 0, "Output close-on-exec failed");
        if (use_xz) {
            int pipefd[2]; require(pipe2(pipefd, O_CLOEXEC) == 0, "Compressor pipe failed"); child = fork(); require(child >= 0, "Compressor fork failed");
            if (child == 0) {
                if (dup2(pipefd[0], STDIN_FILENO) < 0 || dup2(fileno(stream), STDOUT_FILENO) < 0) _exit(126);
                close(pipefd[0]); close(pipefd[1]); fclose(stream);
                execl("/usr/bin/xz", "xz", "-1", "-c", static_cast<char*>(nullptr)); _exit(127);
            }
            close(pipefd[0]); fclose(stream); stream = fdopen(pipefd[1], "wb"); require(stream, "Compressor stream failed");
        }
        setvbuf(stream, nullptr, _IOFBF, 1 << 20);
    }
    ~HashedOutput() { if (stream) fclose(stream); if (child > 0) { int status = 0; waitpid(child, &status, 0); } }
    void add(const string& value) {
        hash.add(value); bytes += value.size();
        require(fwrite(value.data(), 1, value.size(), stream) == value.size(), "Output write failed");
    }
    string finish() {
        int status = fclose(stream); stream = nullptr; require(status == 0, "Output close failed");
        if (child > 0) { int result = 0; require(waitpid(child, &result, 0) == child, "Compressor wait failed"); child = -1; require(WIFEXITED(result) && WEXITSTATUS(result) == 0, "Compressor failed"); }
        return hash.finish();
    }
};

struct Scanner {
    const string& text; size_t pos = 0;
    explicit Scanner(const string& input) : text(input) {}
    void ws() { while (pos < text.size() && (text[pos] == ' ' || text[pos] == '\t' || text[pos] == '\r')) ++pos; }
    uint64_t integer() {
        ws(); require(pos < text.size() && text[pos] >= '0' && text[pos] <= '9', "Expected unsigned integer");
        uint64_t value = 0;
        while (pos < text.size() && text[pos] >= '0' && text[pos] <= '9') {
            unsigned digit = unsigned(text[pos++] - '0');
            require(value <= (numeric_limits<uint64_t>::max() - digit) / 10, "Integer overflow");
            value = 10 * value + digit;
        }
        return value;
    }
    int small() { uint64_t value = integer(); require(value <= 1000000, "Unexpectedly large field"); return int(value); }
    void exact(const string& expected) { ws(); require(text.compare(pos, expected.size(), expected) == 0, "Expected literal " + expected); pos += expected.size(); }
    bool take(char c) { ws(); if (pos < text.size() && text[pos] == c) { ++pos; return true; } return false; }
    void end() { ws(); require(pos == text.size(), "Trailing unparsed input"); }
    string word() {
        exact("\""); size_t first = pos;
        while (pos < text.size() && text[pos] != '"') { require(text[pos] != '\\', "Escaped native key unexpected"); ++pos; }
        require(pos < text.size(), "Unterminated key"); string result = text.substr(first, pos - first); ++pos; return result;
    }
};

struct Profile {
    uint64_t id = 0;
    int z = 0, support = 1, weight = 0;
    array<int, 64> groups{}; // index=32*(own_count>0)+weight
};

class Profiles {
    ifstream input;
    int maximum;
    bool previous = false;
    uint64_t previous_id = 0;
public:
    Profile current;
    bool active = false;
    explicit Profiles(const fs::path& path, int max) : input(path), maximum(max) { require(bool(input), "Cannot open profile file"); next(); }
    void next() {
        string line;
        if (!getline(input, line)) { require(input.eof(), "Profile file read error"); active = false; return; }
        require(!input.eof(), "Profile file has no terminating newline");
        Scanner scan(line); Profile row;
        row.id = scan.integer(); row.z = scan.small(); int count = scan.small(); row.weight = maximum;
        require(row.z <= 31 && count <= 64, "Profile domain");
        if (previous) require(row.id > previous_id, "Profile IDs must increase strictly");
        for (int i = 0; i < count; ++i) {
            int flag = scan.small(), weight = scan.small(), multiplicity = scan.small();
            require(flag <= 1 && weight >= 2 && weight <= maximum && multiplicity >= 1 && multiplicity <= 31, "Profile group domain");
            row.groups[32 * flag + weight] += multiplicity;
            row.support += multiplicity; row.weight += weight * multiplicity;
        }
        scan.end(); int positives = 0;
        for (int weight = 2; weight <= maximum; ++weight) positives += row.groups[32 + weight];
        require(row.support <= 32 && row.weight <= 93 && row.z == 31 - positives, "Profile support/weight/own-zero mismatch");
        previous = true; previous_id = row.id; current = row; active = true;
    }
};

struct Moment { int w, j, s, q; };
static vector<Moment> parse_witness(const string& line, const Profile& expected, int maximum) {
    Scanner scan(line); scan.exact("WITNESS profile=");
    require(scan.integer() == expected.id, "Witness profile ID mismatch"); scan.exact("[");
    vector<Moment> rows; rows.reserve(expected.support - 1); array<int, 64> groups{};
    while (!scan.take(']')) {
        scan.exact("("); Moment row{};
        row.w = scan.small(); scan.exact(","); row.j = scan.small(); scan.exact(",");
        row.s = scan.small(); scan.exact(","); row.q = scan.small(); scan.exact(")");
        require(row.w >= 2 && row.w <= maximum && row.j <= row.w / 2 && row.s <= row.w / 2, "Moment row domain");
        require(rows.size() < 31, "Too many moment rows");
        groups[32 * int(row.j > 0) + row.w]++; rows.push_back(row);
    }
    scan.end(); require(int(rows.size()) + 1 == expected.support && groups == expected.groups, "Witness differs from complete profile groups");
    return rows;
}

static map<string, uint64_t> parse_stats(const string& line) {
    Scanner scan(line); scan.exact("{"); map<string, uint64_t> row;
    do { string key = scan.word(); scan.exact(":"); uint64_t value = scan.integer(); require(row.emplace(key, value).second, "Duplicate native statistic"); } while (scan.take(','));
    scan.exact("}"); scan.end();
    require(row.size() == 5 && row.count("profile") && row.count("nodes") && row.count("leaves") && row.count("moment_survivors") && row.count("geometry_survivors"), "Unexpected native statistics schema");
    return row;
}

struct Key {
    uint16_t mass = 0;
    uint8_t cap = 0, cutoff = 0;
    array<uint8_t, 16> heavy{};
    bool operator==(const Key& other) const { return mass == other.mass && cap == other.cap && cutoff == other.cutoff && heavy == other.heavy; }
    bool operator<(const Key& other) const { return tie(cutoff, cap, mass, heavy) < tie(other.cutoff, other.cap, other.mass, other.heavy); }
};
struct KeyHash {
    size_t operator()(const Key& key) const {
        uint64_t hash = 1469598103934665603ULL;
        auto add = [&](unsigned value) { hash ^= value; hash *= 1099511628211ULL; };
        add(key.mass & 255); add(key.mass >> 8); add(key.cap); add(key.cutoff);
        for (unsigned value : key.heavy) add(value);
        return size_t(hash);
    }
};

static bool use_exact_sumset = false;
static int sumset_cap(int a,int b){
 int value=min(16,a*b);
 if(use_exact_sumset){if(a>b)swap(a,b);if(a==3&&b>=5&&b<=7)return b+8;}
 return value;
}

struct LocalDP {
    unordered_map<Key, int, KeyHash> cache;
    uint64_t hits = 0, misses = 0;
    int value(int cap, int mass, const array<uint8_t, 16>& heavy, int cutoff) {
        require(cap >= 0 && cap <= 15 && mass >= 0 && mass <= 465 && cutoff >= 0 && cutoff <= 16, "DP domain");
        Key key{uint16_t(mass), uint8_t(cap), uint8_t(cutoff), heavy};
        auto found = cache.find(key); if (found != cache.end()) { ++hits; return found->second; }
        ++misses; constexpr int negative = -1000000000;
        vector<int> best(mass + 1, negative), next(mass + 1, negative); best[0] = 0; int limit = 0;
        for (int upper = 1; upper <= 15; ++upper) for (int repeat = 0; repeat < heavy[upper]; ++repeat) {
            int next_limit = min(mass, limit + cap); fill(next.begin(), next.begin() + next_limit + 1, negative);
            for (int used = 0; used <= limit; ++used) for (int tokens = 0; tokens <= min(cap, mass - used); ++tokens) {
                int score = best[used] + 2 * sumset_cap(upper, tokens) - cutoff * tokens;
                next[used + tokens] = max(next[used + tokens], score);
            }
            best.swap(next); limit = next_limit;
        }
        int answer = cutoff * mass + *max_element(best.begin(), best.begin() + limit + 1);
        cache.emplace(key, answer); return answer;
    }
};

enum class Correction { None, Plane, OwnPeriodic, PairedDirection };
struct Bound { int upper = 0, plain = 0, correction = 0, cutoff = 0, heavy_count = 0, candidate_count = 0, exceptions = 0; };

static Bound bound_at(const vector<Moment>& rows, int cutoff, Correction mode, LocalDP& dp) {
    Bound bound; bound.cutoff = cutoff; array<uint8_t, 16> heavy{};
    vector<int> heavy_caps, gains;
    for (const auto& row : rows) if (row.s > cutoff) { ++heavy[row.s]; heavy_caps.push_back(row.s); }
    bound.heavy_count = int(heavy_caps.size());
    for (size_t i = 0; i < heavy_caps.size(); ++i) for (size_t j = 0; j < i; ++j) bound.plain += 2 * sumset_cap(heavy_caps[i], heavy_caps[j]);
    for (const auto& row : rows) if (row.s <= cutoff) {
        int mass = row.w * (row.w - 1) / 2 - row.j;
        int full = dp.value(row.s, mass, heavy, cutoff); bound.plain += full;
        bool eligible = mode == Correction::PairedDirection ||
                        (mode == Correction::OwnPeriodic ? 2 * row.j == row.w :
                         mode == Correction::Plane && cutoff >= 2 && row.w == 4 && row.j == 2 && row.s == 2);
        if (eligible) {
            int budget;
            if (mode == Correction::PairedDirection) {
                int delta = row.w / 2 - row.j;
                require(delta >= 0, "Negative own-direction defect");
                budget = min(mass, (mass + delta * bound.heavy_count) / 2);
            } else {
                require(mass % 2 == 0, "Own-periodic pair mass must be even");
                budget = mass / 2;
            }
            int restricted = dp.value(row.s, budget, heavy, cutoff) + cutoff * (mass - budget);
            require(restricted <= full, "Restricted DP exceeds full DP"); gains.push_back(full - restricted);
        }
    }
    sort(gains.begin(), gains.end(), greater<int>()); bound.candidate_count = int(gains.size());
    bound.exceptions = min(int(gains.size()), bound.heavy_count * (bound.heavy_count - 1) / 2);
    for (size_t i = size_t(bound.exceptions); i < gains.size(); ++i) bound.correction += gains[i];
    bound.upper = bound.plain - bound.correction; require(bound.upper >= 0, "Negative resource upper bound"); return bound;
}

static int required_capacity(const vector<Moment>& rows, int maximum) {
    int positive = 0, ones = 0;
    for (const auto& row : rows) { positive += row.j > 0; ones += row.j == 1; }
    int complement = 32 - maximum;
    return 16 * (31 - positive) + complement * ones - min(complement * (complement - 1) / 2, (complement / 2) * ones);
}

// Exact minimum over the necessary hub-count interval and total pair mass.
// Marginal benefits of increasing one count are nonincreasing. Selecting the
// largest benefits has a prefix-respecting selection with the same value.
static int full_hub_capacity_demand(const vector<Moment>& rows, int maximum) {
    array<int, 17> own{}; own[0] = 31 - int(rows.size());
    for (const auto& row : rows) ++own[row.j];
    int low = max(0, maximum - 16), high = maximum / 2;
    int budget = maximum * (maximum - 1) / 2 - 31 * low;
    require(budget >= 0 && budget <= 31 * (high - low), "Hub spectrum budget domain");
    int baseline = 0; array<int, 17> benefits{};
    for (int j = 0; j <= 16; ++j) if (own[j]) {
        int previous = 16 - sumset_cap(j, low); baseline += own[j] * previous;
        for (int h = low + 1; h <= high; ++h) {
            int current = 16 - sumset_cap(j, h);
            benefits[previous - current] += own[j]; previous = current;
        }
    }
    int benefit = 0;
    for (int gain = 16; gain >= 0; --gain) {
        int take = min(budget, benefits[gain]); budget -= take; benefit += take * gain;
    }
    require(budget == 0, "Hub spectrum did not allocate its full mass");
    int result = baseline - benefit;
    require(result >= required_capacity(rows, maximum), "Full hub demand weaker than old demand");
    return result;
}

static string result_row(uint64_t ordinal, uint64_t profile, int support, int required, const Bound& b, bool excluded, const vector<Moment>* moments = nullptr) {
    string row = "{\"row\":" + to_string(ordinal) + ",\"profile\":" + to_string(profile) + ",\"support\":" + to_string(support)
        + ",\"required_capacity\":" + to_string(required) + ",\"upper_twice\":" + to_string(b.upper)
        + ",\"cutoff\":" + to_string(b.cutoff) + ",\"plain_upper_twice\":" + to_string(b.plain)
        + ",\"correction_twice\":" + to_string(b.correction) + ",\"heavy_count\":" + to_string(b.heavy_count)
        + ",\"correction_candidate_count\":" + to_string(b.candidate_count) + ",\"exceptional_allowance\":" + to_string(b.exceptions)
        + ",\"excluded\":" + (excluded ? "true" : "false");
    if (moments) {
        row += ",\"types\":["; bool first = true;
        for (const auto& t : *moments) { if (!first) row += ','; first = false; row += '[' + to_string(t.w) + ',' + to_string(t.j) + ',' + to_string(t.s) + ',' + to_string(t.q) + ']'; }
        row += ']';
    }
    return row + "}\n";
}

template<class T> static string integer_map(const map<int, T>& values) {
    string result = "{"; bool first = true;
    for (const auto& [key, value] : values) { if (!first) result += ','; first = false; result += quote(to_string(key)) + ':' + to_string(value); }
    return result + '}';
}

struct Options {
    int maximum = 0; fs::path profiles, prefix, source, joint_source;
    Correction correction = Correction::OwnPeriodic; string correction_name = "own-periodic";
    bool full_hub_demand = false;
    bool tee = false, compress = false;
};

static Options options(int argc, char** argv) {
    Options opts;
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--tee-native") { opts.tee = true; continue; }
        if (arg == "--compress") { opts.compress = true; continue; }
        require(i + 1 < argc, "Missing argument after " + arg); string value = argv[++i];
        if (arg == "--maximum") opts.maximum = stoi(value);
        else if (arg == "--profiles") opts.profiles = value;
        else if (arg == "--prefix") opts.prefix = value;
        else if (arg == "--source") opts.source = value;
        else if (arg == "--joint-source") opts.joint_source = value;
        else if (arg == "--demand") {
            require(value == "weak" || value == "full-hub-mass", "Unknown demand mode");
            opts.full_hub_demand = value == "full-hub-mass";
        }
        else if (arg == "--correction") {
            opts.correction_name = value;
            if (value == "none") opts.correction = Correction::None;
            else if (value == "plane") opts.correction = Correction::Plane;
            else if (value == "own-periodic") opts.correction = Correction::OwnPeriodic;
            else if (value == "paired-direction") opts.correction = Correction::PairedDirection;
            else throw runtime_error("Unknown correction: " + value);
        } else throw runtime_error("Unknown option: " + arg);
    }
    require(opts.maximum >= 2 && opts.maximum <= 31 && !opts.profiles.empty() && !opts.prefix.empty(), "Require --maximum2..31 --profiles FILE --prefix PATH");
    return opts;
}

int main(int argc, char** argv) {
    ios::sync_with_stdio(false); cin.tie(nullptr); signal(SIGPIPE, SIG_IGN);
    fs::path summary_path;
    try {
        Options opts = options(argc, argv); auto started = chrono::steady_clock::now();
        fs::path directory = opts.prefix.parent_path(); if (!directory.empty()) fs::create_directories(directory);
        string extension = opts.compress ? ".xz" : "";
        vector<string> suffixes = {".results.jsonl" + extension, ".remaining.jsonl" + extension,
                                  ".remaining.native.txt" + extension, ".local_dp.jsonl" + extension, ".summary.json"};
        for (const auto& suffix : suffixes) require(!fs::exists(opts.prefix.string() + suffix), "Refusing to overwrite existing output: " + opts.prefix.string() + suffix);
        summary_path = opts.prefix.string() + ".summary.json";
        string profiles_hash = file_hash(opts.profiles);
        Profiles profiles(opts.profiles, opts.maximum);
        HashedOutput results(opts.prefix.string() + ".results.jsonl" + extension, opts.compress),
                     remaining(opts.prefix.string() + ".remaining.jsonl" + extension, opts.compress),
                     native_remaining(opts.prefix.string() + ".remaining.native.txt" + extension, opts.compress);
        Sha256 raw_hash; LocalDP dp; uint64_t input_bytes = 0, witnesses = 0, block = 0, completed_profiles = 0;
        map<int, uint64_t> profile_counts, witness_counts, excluded_counts, remaining_counts, cutoff_counts;
        map<int, int> minimum_gaps;
        map<string, uint64_t> statistics;
        const array<int, 17> cutoff_order = {2, 1, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
        string line;
        while (getline(cin, line)) {
            require(!cin.eof(), "Native stream lacks final newline");
            require(profiles.active, "Native stream has extra data after all profiles");
            string raw = line + '\n'; raw_hash.add(raw); input_bytes += raw.size(); if (opts.tee) cout.write(raw.data(), streamsize(raw.size()));
            if (line.rfind("WITNESS ", 0) == 0) {
                auto moments = parse_witness(line, profiles.current, opts.maximum);
                int demand = opts.full_hub_demand ? full_hub_capacity_demand(moments, opts.maximum) : required_capacity(moments, opts.maximum);
                Bound best; best.upper = numeric_limits<int>::max(); bool excluded = false;
                for (int cutoff : cutoff_order) {
                    Bound bound = bound_at(moments, cutoff, opts.correction, dp);
                    if (bound.upper < best.upper || (bound.upper == best.upper && cutoff < best.cutoff)) best = bound;
                    if (bound.upper < 2 * demand) { best = bound; excluded = true; break; }
                }
                int support = profiles.current.support;
                results.add(result_row(witnesses, profiles.current.id, support, demand, best, excluded));
                ++witnesses; ++block; ++witness_counts[support]; ++cutoff_counts[best.cutoff];
                if (excluded) {
                    ++excluded_counts[support]; int gap = 2 * demand - best.upper;
                    if (!minimum_gaps.count(support) || gap < minimum_gaps[support]) minimum_gaps[support] = gap;
                } else {
                    ++remaining_counts[support]; remaining.add(result_row(witnesses - 1, profiles.current.id, support, demand, best, false, &moments)); native_remaining.add(raw);
                }
            } else {
                auto stats = parse_stats(line);
                require(stats["profile"] == profiles.current.id && stats["geometry_survivors"] == block, "Native block/profile count mismatch");
                require(stats["moment_survivors"] >= block, "Native moment count below printed witness count");
                for (const auto& [name, value] : stats) if (name != "profile") statistics[name] += value;
                ++profile_counts[profiles.current.support]; ++completed_profiles; block = 0; profiles.next();
            }
        }
        require(cin.eof() && !profiles.active && block == 0, "Incomplete native stream; not every input profile finished");
        if (opts.tee) { cout.flush(); require(bool(cout), "Native tee output failed"); }
        string native_hash = raw_hash.finish(), result_hash = results.finish(), remaining_hash = remaining.finish(), remaining_native_hash = native_remaining.finish();
        HashedOutput local(opts.prefix.string() + ".local_dp.jsonl" + extension, opts.compress);
        vector<pair<Key, int>> keys(dp.cache.begin(), dp.cache.end()); sort(keys.begin(), keys.end(), [](const auto& a, const auto& b) { return a.first < b.first; });
        for (const auto& [key, value] : keys) {
            string row = "{\"cutoff\":" + to_string(key.cutoff) + ",\"cap\":" + to_string(key.cap) + ",\"mass\":" + to_string(key.mass) + ",\"heavy_caps\":[";
            bool first = true;
            for (int h = 1; h <= 15; ++h) for (int n = 0; n < key.heavy[h]; ++n) { if (!first) row += ','; first = false; row += to_string(h); }
            row += "],\"value_twice\":" + to_string(value) + "}\n"; local.add(row);
        }
        string local_hash = local.finish(); double seconds = chrono::duration<double>(chrono::steady_clock::now() - started).count();
        ostringstream summary;
        summary << "{\n\"status\":\"COMPLETE_NATIVE_STREAM_RESOURCE_FILTER\",\n\"maximum\":" << opts.maximum
                << ",\n\"weight_upper_bound\":93,\n\"correction\":" << quote(opts.correction_name)
                << ",\n\"demand_mode\":" << quote(opts.full_hub_demand ? "full-hub-mass" : "weak")
                << ",\n\"output_compression\":" << quote(opts.compress ? "xz" : "none")
                << ",\n\"complete_input_profile_blocks\":" << completed_profiles << ",\n\"witness_rows\":" << witnesses
                << ",\n\"profiles_by_support\":" << integer_map(profile_counts) << ",\n\"witnesses_by_support\":" << integer_map(witness_counts)
                << ",\n\"excluded_by_support\":" << integer_map(excluded_counts) << ",\n\"remaining_by_support\":" << integer_map(remaining_counts)
                << ",\n\"minimum_exclusion_doubled_gap_by_support\":" << integer_map(minimum_gaps) << ",\n\"selected_cutoff_histogram\":" << integer_map(cutoff_counts)
                << ",\n\"native_statistics\":{";
        bool first = true; for (const auto& [name, value] : statistics) { if (!first) summary << ','; first = false; summary << quote(name) << ':' << value; }
        summary << "},\n\"profiles_sha256\":" << quote(profiles_hash) << ",\n\"raw_native_sha256\":" << quote(native_hash)
                << ",\n\"raw_native_bytes\":" << input_bytes << ",\n\"results_sha256\":" << quote(result_hash)
                << ",\n\"remaining_json_sha256\":" << quote(remaining_hash) << ",\n\"remaining_native_sha256\":" << quote(remaining_native_hash)
                << ",\n\"local_dp_sha256\":" << quote(local_hash) << ",\n\"local_dp_instances\":" << dp.cache.size()
                << ",\n\"local_dp_cache_hits\":" << dp.hits << ",\n\"local_dp_cache_misses\":" << dp.misses
                << ",\n\"elapsed_seconds\":" << setprecision(9) << seconds << ",\n\"compiler\":" << quote(__VERSION__);
        if (!opts.source.empty()) summary << ",\n\"filter_source_sha256\":" << quote(file_hash(opts.source));
        if (!opts.joint_source.empty()) summary << ",\n\"joint_source_sha256\":" << quote(file_hash(opts.joint_source));
        summary << ",\n\"cutoff_policy\":\"2,1,3,0,4..16; stop at first strict valid exclusion; otherwise retain minimum bound\""
                << ",\n\"scope\":\"Necessary arithmetic exclusions for this exact complete native profile stream; survivors are necessary moment profiles, not actual configurations\""
                << ",\n\"maximum_stratum_closed_by_filter_alone\":false,\n\"unrestricted_n5_closed\":false\n}\n";
        ofstream out(summary_path); out << summary.str(); out.close(); require(bool(out), "Cannot write summary");
        cerr << "COMPLETE profiles=" << completed_profiles << " witnesses=" << witnesses << " remaining=";
        uint64_t nremaining = 0; for (const auto& [support, count] : remaining_counts) nremaining += count;
        cerr << nremaining << " seconds=" << seconds << '\n';
        return 0;
    } catch (const exception& error) {
        cerr << "ERROR: " << error.what() << '\n';
        if (!summary_path.empty() && !fs::exists(summary_path)) { ofstream out(summary_path); out << "{\"status\":\"INCOMPLETE_OR_INVALID_NO_COMPOSITION\",\"error\":" << quote(error.what()) << ",\"maximum_stratum_closed_by_filter_alone\":false}\n"; }
        return 2;
    }
}
