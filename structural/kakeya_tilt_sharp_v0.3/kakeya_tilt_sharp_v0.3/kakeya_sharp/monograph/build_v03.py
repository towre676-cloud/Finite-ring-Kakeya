"""Fill the v0.3 monograph template from the JSON receipts."""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
res = os.path.join(here, "..", "results")


def load_cases():
    final = {}
    for name in ["log_heavy_n4_sq.txt", "log_heavy_n4_pass2.txt", "log_heavy_n4_pass3.txt"]:
        p = os.path.join(res, name)
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            key = tuple(r["B"])
            prev = final.get(key)
            if prev is None or prev["status"] == "UNKNOWN":
                r["pass"] = name
                final[key] = r
    orbits = json.load(open(os.path.join(res, "heavy_orbits_n4_ub45.json")))
    rows = []
    for o in orbits:
        r = final.get(tuple(o["B"]))
        rows.append((o, r))
    return rows


def table(rows):
    out = ['<div class="tbl"><table>',
           '<thead><tr><th>$h$</th><th>$d$</th><th>orbit size</th><th>representative $B$</th><th>verdict</th><th>time (s)</th></tr></thead><tbody>']
    closed = 0
    for o, r in sorted(rows, key=lambda t: (t[0]["h"], t[0]["d"], t[0]["B"])):
        if r is None:
            v, cls, t = "not run", "op", "—"
        elif r["status"] == "INFEASIBLE":
            v, cls, t = "closed", "ok", f'{r["seconds"]:.1f}'; closed += 1
        else:
            v, cls, t = "open", "op", f'{r["seconds"]:.0f}'
        B = "{" + ",".join(str(b) for b in o["B"]) + "}"
        out.append(f'<tr><td>{o["h"]}</td><td>{o["d"]}</td><td>{o["orbit_size"]:,}</td><td><code>{B}</code></td><td class="{cls}">{v}</td><td>{t}</td></tr>')
    out.append('</tbody></table></div>')
    return "\n".join(out), closed, len(rows)


if __name__ == "__main__":
    rows = load_cases()
    tbl, closed, total = table(rows)
    para = (f'<p>Residues are written as integers whose binary digits are the coordinates. '
            f'<span class="label cert">Certified VI.6.1.</span> {closed} of the {total} admissible heavy-support orbits are closed: '
            f'no Kakeya set of at most 45 points without a full fibre has its heavy support in those orbits, in either ring. ')
    if closed == total:
        para += 'Together with VI.4.1 this proves $k(R,4)=46$ in both rings.</p>'
        n4nofull, n4k = "$\\ge 46$", "46"
    else:
        para += (f'<span class="label open">Open:</span> the remaining {total - closed} orbits returned no verdict within the stated time. '
                 'Where $d=15$, the set $B+B$ already meets every direction, so Corollary 11 imposes no lower bound on the number of 2-point fibres and the 45-point budget can be spent entirely on medium heavy fibres; this is the regime the counting and energy cuts control least. '
                 'Closing them settles $k(R,4)=46$ in both rings.</p>')
        n4nofull, n4k = "open (" + f"{closed}/{total} orbits closed" + ")", "$46$ iff open orbits close"
    src = open(os.path.join(here, "template_v03.html")).read()
    src = src.replace("<!--HEAVY_TABLE-->", tbl + "\n" + para)
    src = src.replace("LEDGER_N4_NOFULL", n4nofull).replace("LEDGER_N4_K", n4k)
    open(os.path.join(here, "Kakeya_Full_Fibre_Half_v0.3.html"), "w").write(src)
    print(json.dumps({"closed": closed, "total": total}))
