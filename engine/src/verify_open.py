#!/usr/bin/env python3
"""Live confirmation that a specific conjecture on a specific entry is still open.

Stricter than recheck.py: it looks for the exact conjecture line we settled, and it
flags ANY settlement wording anywhere on the entry, printing the hit so a human can
judge whether it refers to this conjecture or to a different one.
"""
import json, re, subprocess, sys, time

PROOF = re.compile(r"\bproof\b|\bproved\b|\bproven\b|is true|Kauers|Koutschan|"
                   r"has been shown|follows from|confirm\w*|verified|checked using|"
                   r"establish\w*|settled|no longer a conjecture|follows from the fact|"
                   r"immediate consequence|can be deduced|is a corollary|"
                   r"is now a theorem|now a theorem|this is a theorem|"
                   r"has been established|resolved by|closed by|"
                   r"is correct|are correct|follows easily|follows at once|"
                   r"follows immediately|derives from|is a consequence", re.I)

# A settlement is not always a PROOF, and it does not always name what it settles. A210247
# carries "Conjecture: a(n) = -a(n-28)" and, on the very next line, Robert Israel's "That is
# not quite true: the first counterexample is n=578." The openness test called it open twice
# over: none of the PROOF words appears, and the co-occurrence test above -- which asks the
# same line to say "conjecture" or "recurrence" -- rules out a refutation that refers to the
# claim by position, which is how most of them are written.
#
# This project came within one build of papering a disproof the entry already records. That
# is the exact credibility cost the binding rules exist to avoid, so refutation wording is
# read WITHOUT the co-occurrence requirement: these phrases are about a claim wherever they
# appear, and a false positive here drops a result rather than publishing a wrong one, which
# is the safe direction to err in.
REFUTED = re.compile(
    r"\bis false\b|\bare false\b|\bis not true\b|not quite true|\bfails at\b|"
    r"\bfails for\b|counterexample|\bdisproved\b|\bdisproven\b|\brefuted\b|"
    r"\bis incorrect\b|\bis wrong\b|\bdoes not hold\b|\bbreaks down at\b", re.I)


def fetch(a, tries=4):
    """OEIS occasionally returns an empty body; retry rather than call the entry gone."""
    last = None
    for i in range(tries):
        out = subprocess.run(["curl", "-sS", "-A", "Mozilla/5.0",
                              f"https://oeis.org/search?q=id:{a}&fmt=json"],
                             capture_output=True, text=True, timeout=90).stdout
        try:
            return json.loads(out)[0]
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"could not fetch {a}: {last}")


def norm(s):
    return re.sub(r"\s+", "", s.split(" - _")[0])


def check(a, conj):
    e = fetch(a)
    lines, said = [], []
    for k in ("comment", "formula", "link", "ext", "example"):
        lines += e.get(k) or []
        # an EXAMPLE line is the entry explaining its own terms, never a settlement. The one
        # false positive REFUTED produced over all 13,391 papered entries was A114584's
        # "the only counterexamples among the 9 Motzkin paths of length 4 are HUHD and UHDH",
        # which is the definition at work. So refutation wording is read everywhere a
        # settlement is actually recorded, and not there.
        if k != "example":
            said += e.get(k) or []
    present = any(norm(conj) in norm(l) for l in lines)
    hits = [l[:160] for l in lines
            if (PROOF.search(l) and re.search(r"conjectur|recurrence", l, re.I))]
    hits += [l[:160] for l in said if REFUTED.search(l) and l[:160] not in hits]
    return present, hits, e["time"][:10], e["revision"], e["name"], e.get("author", ""), \
        [int(v) for v in e["data"].split(",")], int(e["offset"].split(",")[0])


if __name__ == "__main__":
    todo = json.load(open(sys.argv[1]))          # {anum: conjecture text}
    out = {}
    for a, conj in sorted(todo.items()):
        try:
            present, hits, t, rev, name, auth, data, off = check(a, conj)
        except Exception as ex:
            print(f"{a}  FETCH FAILED {ex}")
            continue
        time.sleep(0.3)
        st = "OPEN" if (present and not hits) else ("GONE" if not present else "SETTLED?")
        print(f"{a}  {st}")
        for h in hits:
            print(f"      hit: {h}")
        if st == "OPEN":
            out[a] = {"conj": conj, "time": t, "revision": rev, "name": name,
                      "author": auth, "data": data, "offset": off}
    json.dump(out, open("open-check.json", "w"), indent=1, sort_keys=True)
    print(f"\nstill open: {len(out)} of {len(todo)}")
