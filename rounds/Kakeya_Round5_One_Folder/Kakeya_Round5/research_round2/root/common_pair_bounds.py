"""Frozen elementary pair-capacity and profile parsing helpers. No archive dependency."""

def maximum_sumset(p, q, improved=True):
    if improved and min(p, q) == 3:
        return min(16, p*q, max(p, q)+8)
    return min(16, p*q)

def read_profile(tokens):
    pid, zero, groups = tokens[:3]
    assert len(tokens) == 3+3*groups
    rows = []
    for j in range(groups):
        f, w, count = tokens[3+3*j:6+3*j]
        assert f in (0, 1) and 2 <= w <= 19 and count > 0
        rows.extend([(f, w)]*count)
    assert 19+sum(w for f, w in rows) == 93
    assert zero == 31-sum(f for f, w in rows)
    return pid, zero, rows
