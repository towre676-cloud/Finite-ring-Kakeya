// Backward DRAT checker (RUP lemmas only; RAT lemmas are reported as failures).
// Written for this project. Usage: dratback formula.cnf proof.drat
// Algorithm (core-first, as in drat-trim): forward pass adds every lemma without checking and
// propagates top-level units until a top-level conflict appears.  The conflict and its reasons are
// marked.  Lemmas are then removed in reverse order; each marked lemma is checked by reverse unit
// propagation against the clause database that existed just before it, and every clause used in
// that check is marked.  Unmarked lemmas are never relied on.
#include <bits/stdc++.h>
using namespace std;

struct Clause { vector<int> lits; bool alive = false; bool marked = false; bool lemma = false; };
static vector<Clause> db;
static int nv = 0;
static vector<signed char> val;
static vector<int> reason;          // clause index of the propagating clause, -1 for decisions
static vector<vector<int>> watches; // by literal code
static vector<int> trail;
static size_t qhead = 0;

static inline int code(int l) { return l > 0 ? 2 * l : 2 * (-l) + 1; }
static inline int value(int l) { int v = val[abs(l)]; return v == 0 ? 0 : ((l > 0) == (v > 0) ? 1 : -1); }
static void ensure(int v) { if (v > nv) { nv = v; val.resize(nv + 1, 0); reason.resize(nv + 1, -1); watches.resize(2 * nv + 2); } }
static void assign(int l, int r) { val[abs(l)] = l > 0 ? 1 : -1; reason[abs(l)] = r; trail.push_back(l); }
static void undo_to(size_t sz) { while (trail.size() > sz) { int l = trail.back(); trail.pop_back(); val[abs(l)] = 0; reason[abs(l)] = -1; } if (qhead > sz) qhead = sz; }

// returns conflicting clause index or -1
static int propagate() {
    while (qhead < trail.size()) {
        int fl = -trail[qhead++];
        auto &ws = watches[code(fl)];
        size_t i = 0, j = 0;
        for (; i < ws.size(); i++) {
            int ci = ws[i]; Clause &c = db[ci];
            if (!c.alive) continue;
            auto &L = c.lits;
            if (L[0] == fl) swap(L[0], L[1]);
            if (L[1] != fl) continue;           // stale watch entry
            if (value(L[0]) == 1) { ws[j++] = ci; continue; }
            bool moved = false;
            for (size_t k = 2; k < L.size(); k++) if (value(L[k]) != -1) { swap(L[1], L[k]); watches[code(L[1])].push_back(ci); moved = true; break; }
            if (moved) continue;
            ws[j++] = ci;
            if (value(L[0]) == -1) { for (i++; i < ws.size(); i++) ws[j++] = ws[i]; ws.resize(j); return ci; }
            assign(L[0], ci);
        }
        ws.resize(j);
    }
    return -1;
}

// attach clause: order literals so that watched ones are non-false when possible
static void attach(int ci) {
    Clause &c = db[ci]; auto &L = c.lits; c.alive = true;
    if (L.size() < 2) return;   // units handled through the trail
    stable_partition(L.begin(), L.end(), [](int l) { return value(l) != -1; });
    watches[code(L[0])].push_back(ci); watches[code(L[1])].push_back(ci);
}

// mark the clauses responsible for the falsity of every literal of clause ci (transitively)
static vector<char> seen;
static void analyze(int ci) {
    vector<int> stack;
    db[ci].marked = true;
    for (int l : db[ci].lits) stack.push_back(abs(l));
    while (!stack.empty()) {
        int v = stack.back(); stack.pop_back();
        if (seen[v]) continue; seen[v] = 1;
        int r = reason[v];
        if (r < 0) continue;
        db[r].marked = true;
        for (int l : db[r].lits) if (abs(l) != v) stack.push_back(abs(l));
    }
}
static void clear_seen() { fill(seen.begin(), seen.end(), 0); }

struct Step { int ci; bool del; size_t trail_before; bool applied; };

static bool read_clause(FILE *f, vector<int> &out, bool &del) {
    out.clear(); del = false; int c;
    while ((c = fgetc(f)) != EOF) {
        if (c == 'c' || c == 'p') { while ((c = fgetc(f)) != EOF && c != '\n') {} continue; }
        if (isspace(c)) continue;
        if (c == 'd') { del = true; continue; }
        ungetc(c, f); int x;
        if (fscanf(f, "%d", &x) != 1) return false;
        if (x == 0) return true;
        out.push_back(x);
    }
    return false;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: dratback formula proof\n"); return 2; }
    unordered_map<string, vector<int>> index;   // canonical key -> alive clause indices
    auto key = [](vector<int> L) { sort(L.begin(), L.end()); L.erase(unique(L.begin(), L.end()), L.end()); string s; for (int l : L) { s += to_string(l); s += ' '; } return s; };
    FILE *f = fopen(argv[1], "r"); if (!f) return 2;
    vector<int> L; bool del; long norig = 0;
    bool conflict = false; int confl = -1;
    while (read_clause(f, L, del)) {
        for (int l : L) ensure(abs(l));
        sort(L.begin(), L.end()); L.erase(unique(L.begin(), L.end()), L.end());
        int ci = db.size(); db.push_back({L, false, false, false}); norig++;
        index[key(L)].push_back(ci);
        if (conflict) { db[ci].alive = true; continue; }
        if (L.empty()) { conflict = true; confl = ci; db[ci].alive = true; continue; }
        attach(ci);
        if (L.size() == 1) {
            if (value(L[0]) == -1) { conflict = true; confl = ci; }
            else if (value(L[0]) == 0) assign(L[0], ci);
        } else if (value(db[ci].lits[0]) == -1) { conflict = true; confl = ci; }
        else if (value(db[ci].lits[1]) == -1 && value(db[ci].lits[0]) == 0) assign(db[ci].lits[0], ci);
        if (!conflict) { int c = propagate(); if (c >= 0) { conflict = true; confl = c; } }
    }
    fclose(f);
    seen.assign(nv + 2, 0);
    vector<Step> steps;
    FILE *p = fopen(argv[2], "r"); if (!p) return 2;
    long nlem = 0, ndel = 0;
    while (!conflict && read_clause(p, L, del)) {
        for (int l : L) ensure(abs(l));
        if (seen.size() < (size_t)nv + 2) seen.resize(nv + 2, 0);
        sort(L.begin(), L.end()); L.erase(unique(L.begin(), L.end()), L.end());
        if (del) {
            ndel++;
            auto it = index.find(key(L));
            if (it == index.end() || it->second.empty()) continue;   // deleting unknown clause: ignore
            int ci = it->second.back();
            bool isreason = false;
            for (int l : db[ci].lits) if (value(l) == 1 && reason[abs(l)] == ci) isreason = true;
            if (isreason || db[ci].lits.size() <= 1) continue;      // keep unit/reason clauses (sound: more clauses)
            it->second.pop_back(); db[ci].alive = false;
            steps.push_back({ci, true, trail.size(), true});
            continue;
        }
        nlem++;
        int ci = db.size(); db.push_back({L, false, false, true});
        index[key(L)].push_back(ci);
        steps.push_back({ci, false, trail.size(), true});
        if (L.empty()) { db[ci].alive = true; conflict = true; confl = ci; break; }
        attach(ci);
        if (L.size() == 1) {
            if (value(L[0]) == -1) { conflict = true; confl = ci; break; }
            if (value(L[0]) == 0) assign(L[0], ci);
        } else {
            if (value(db[ci].lits[0]) == -1) { conflict = true; confl = ci; break; }
            if (value(db[ci].lits[1]) == -1 && value(db[ci].lits[0]) == 0) assign(db[ci].lits[0], ci);
        }
        int c = propagate(); if (c >= 0) { conflict = true; confl = c; break; }
    }
    fclose(p);
    if (!conflict) { printf("s NOT VERIFIED (no conflict reached)\n"); return 1; }
    seen.resize(nv + 2, 0);
    // mark final conflict
    if (db[confl].lits.empty()) {
        // empty lemma: it must itself be RUP, i.e. top-level propagation conflicts; check below as a lemma
        db[confl].marked = true;
    } else { clear_seen(); analyze(confl); }
    long checked = 0;
    // backward pass
    for (long s = (long)steps.size() - 1; s >= 0; s--) {
        Step &st = steps[s];
        int ci = st.ci;
        if (st.del) { attach(ci); continue; }
        // remove lemma ci and every assignment made at or after its addition
        db[ci].alive = false;
        undo_to(st.trail_before);
        if (!db[ci].marked) continue;
        // RUP check against current database
        checked++;
        size_t base = trail.size();
        bool ok = false; int cc = -1;
        for (int l : db[ci].lits) {
            int v = value(l);
            if (v == 1) {   // lemma already satisfied at top level: implied by the reason chain of l
                ok = true; int r = reason[abs(l)];
                if (r < 0) { ok = false; break; }
                clear_seen(); analyze(r);
                break;
            }
            if (v == 0) assign(-l, -1);
        }
        if (!ok) { qhead = base; cc = propagate(); if (cc >= 0) { ok = true; clear_seen(); analyze(cc); } }
        undo_to(base); qhead = base;
        if (!ok) { printf("s NOT VERIFIED (lemma %d not RUP)\n", ci); return 1; }
    }
    printf("s VERIFIED lemmas=%ld deletions=%ld checked=%ld\n", nlem, ndel, checked);
    return 0;
}
