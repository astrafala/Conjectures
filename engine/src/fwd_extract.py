#!/usr/bin/env python3
"""Recurrence conjectures written with FORWARD shifts, a(n+k), rather than a(n-k).

The main extractor only recognised the backward form, so this whole class of
conjecture was never attempted. Re-indexing n -> n+k turns them into the standard
form the prover already handles.
"""
import json, os, re, sys

ROOT = "/home/user/oeis/oeisdata/seq"
FWD = re.compile(r"Conjecture.*?a\(n\+\d+\)", re.I)


def back_index(conj):
    """Rewrite a(n+k) terms as a(n-j) by substituting n -> n - kmax."""
    body = re.sub(r"^\s*Conjecture[:.]\s*", "", conj, flags=re.I).split(" - _")[0]
    ks = [int(m) for m in re.findall(r"a\(n\+(\d+)\)", body)]
    if not ks:
        return None
    K = max(ks)
    out = re.sub(r"a\(n\+(\d+)\)",
                 lambda m: "a(n)" if int(m.group(1)) == K
                 else f"a(n-{K - int(m.group(1))})", body)
    out = out.replace("a(n+0)", f"a(n-{K})")
    out = re.sub(r"\ba\(n\)(?!\s*[-+*/)])", "a(n)", out)
    # a(n) with no shift becomes a(n-K)
    out = re.sub(r"(?<![+\-\d])a\(n\)", "@@", out)
    # careful: the true a(n) terms were produced above; restore them
    return None if "@@" in out else "Conjecture: " + out


def main():
    from local_extract import parse
    out = {}
    for d in sorted(os.listdir(ROOT)):
        dd = os.path.join(ROOT, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".seq"):
                continue
            p = os.path.join(dd, fn)
            txt = open(p, errors="ignore").read()
            if not FWD.search(txt):
                continue
            f = parse(p)
            anum = "A" + fn[1:7]
            conjs = []
            for tag in ("C", "F", "e"):
                for l in f.get(tag, []):
                    if FWD.search(l) and "=" in l and re.search(r"=\s*0", l):
                        conjs.append(l)
            if not conjs:
                continue
            gfs = [re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I).group(1).strip()
                   for l in f.get("F", [])
                   if re.match(r"G\.f\.\s*:?\s*(.+)", l.strip(), re.I)]
            data = "".join(f.get("S", []) + f.get("T", []) + f.get("U", []))
            try:
                terms = [int(t) for t in data.split(",") if t.strip()]
            except ValueError:
                continue
            off = int((f.get("O") or ["0"])[0].split(",")[0])
            out[anum] = {"name": (f.get("N") or [""])[0], "offset": off,
                         "data": terms, "conjs": conjs, "gfs": gfs,
                         "proof": None, "time": "", "revision": 0}
    json.dump(out, open("fwd-cache.json", "w"), indent=1, sort_keys=True)
    print(f"{len(out)} entries with forward-shift recurrence conjectures; "
          f"{sum(1 for v in out.values() if v['gfs'])} of them post a G.f.")


if __name__ == "__main__":
    main()
