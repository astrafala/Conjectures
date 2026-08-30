#!/usr/bin/env python3
"""Collect everything the new engines proved, filter it, and lay out the build.

Three filters, in this order, because each is cheaper than the next to get wrong:
  * a conjecture that already has a paper is a duplicate, not a result;
  * a conjecture whose own line carries settlement wording is dropped outright;
  * a conjecture on an entry with settlement wording elsewhere is PRINTED for reading,
    never dropped automatically -- on this roster that distinction has cut both ways.
"""
import glob, json, os, re, sys
from wording_scan import WIDE, lines_of, norm

GROUPS = {
    "hyper":  ("hyper-[0-9].json", "closedform-direct"),
    "parity": ("parity-[0-9].json", "parity"),
    "regf":   ("regf-[0-9].json", "regf"),
    "zeilb":  ("zeilb-[0-9].json", "telescoping-boundary"),
    "zeil":   ("zeil2-[0-9].json", "telescoping"),
    "decide": ("decide-[0-9].json", "decide"),
    "holo":   ("holo-[0-9].json", "holonomic"),
    "decide2": ("decide2-[0-9].json", "decide"),
    "ore2":   ("ore2-results.json", "ore"),
    "equate": ("equate-[0-9].json", "equate"),
}


EXCLUDE = ("hyper-", "parity-", "regf-", "zeilb-", "zeil2-", "zeil-", "harvest",
           "decide-", "decide2-", "holo-", "disprove-", "spec-dis",
           "ore2-", "equate-", "field-", "recheck-",
           "new-proved", "new-dup", "diagnose", "gfwhy", "census", "wording-hits")


def existing():
    """(anum, normalised conjecture) pairs that already have a paper.

    Only sources that actually produced papers count. Scanning every json in the
    directory does not work: the new engines' own result files carry anum and conj too,
    so everything new would match itself and the harvest would come out empty.
    """
    out = set()
    for f in ("rec-open.json", "egf-open.json", "logexp-open.json", "cf-open.json"):
        if not os.path.exists(f):
            continue
        try:
            for a, v in json.load(open(f)).items():
                if isinstance(v, dict) and v.get("conj"):
                    out.add((a, norm(v["conj"])))
        except Exception:
            pass
    for f in glob.glob("*.json"):
        if any(f.startswith(p) for p in EXCLUDE):
            continue
        try:
            rows = json.load(open(f))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for s in rows:
            if not (isinstance(s, dict) and s.get("anum") and s.get("conj")
                    and "num" in s):
                continue
            num = s["num"]
            if (os.path.exists(f"papers-old-numbering/{num}-PROOF.pdf")
                    or os.path.exists(f"papers-old-numbering/{num}-DISPROOF.pdf")):
                out.add((s["anum"], norm(s["conj"])))
    return out


def main():
    have = existing()
    # entries whose settlement hit was read and judged to settle THIS conjecture
    manual = json.load(open("settled-manual.json")) \
        if os.path.exists("settled-manual.json") else {}
    rows, dup, dropped, toread = [], [], [], []
    for g, (pat, engine) in GROUPS.items():
        d = {}
        for f in glob.glob(pat):
            d.update(json.load(open(f)))
        for key, v in sorted(d.items()):
            if v.get("status") != "PROVED":
                continue
            a, conj = v["anum"], v["conj"]
            if (a, norm(conj)) in have:
                dup.append((key, g))
                continue
            if a in manual:
                dropped.append((key, g, "read and judged settled: " + manual[a]))
                continue
            ls = lines_of(a) or []
            self_hit = [l for l in ls if WIDE.search(l) and norm(conj)[:60] in norm(l)]
            if self_hit:
                dropped.append((key, g, self_hit[0]))
                continue
            other = [l for l in ls if WIDE.search(l)
                     and re.search(r"conjectur|recurrence", l, re.I)]
            v["engine"] = engine
            v["group"] = g
            rows.append(v)
            if other:
                toread.append((key, g, other[:2]))
    # one paper per (entry, conjecture); the same conjecture found by two engines is one
    seen, uniq = set(), []
    for v in rows:
        k = (v["anum"], norm(v["conj"]))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(v)
    print(f"{len(dup)} duplicates of papers already held")
    print(f"{len(dropped)} dropped: the conjecture line itself carries settlement wording")
    for k, g, l in dropped:
        print(f"    {k} [{g}]  {l[:130]}")
    print(f"\n{len(uniq)} candidate results")
    if toread:
        print(f"\n{len(toread)} of them sit on an entry with settlement wording "
              f"elsewhere -- READ THESE:")
        for k, g, ls in toread:
            print(f"--- {k} [{g}]")
            for l in ls:
                print(f"       {l[:200]}")
    json.dump(uniq, open("harvest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
