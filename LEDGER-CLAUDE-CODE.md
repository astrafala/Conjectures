# PROMPT FOR NEW CLAUDE CODE SESSIONS (don't touch this part ever)

This is the **Claude Code** ledger. It replaces the Claude-chat ledger. Only Sections 1,
2 and 8 differ; the rules, results, dead list, hard list, toolkit and competition notes
are unchanged.

Read this whole file before doing anything. Everything below this prompt is the running
record from 28 completed results: the rules, what is already held, what is already dead,
what is known-hard, what actually works, and who else is racing me. Then start hunting.
Don't summarise the file back to me, don't ask what to target, don't explain your plan.
Begin.

**What I want.** Complete proofs or disproofs of open OEIS conjectures. Only statements
the entry itself labels `Conjecture:` count — see Hard Rule 1. Partial results are
useless to me; leave them out of the numbered set.

**First action, every session.** No longer "ask for links" — that was a chat-tool limit
and it is gone (Section 1). Instead: fetch the competition list (Section 7), then start
sweeping (Section 2). Never ask me to paste a URL.

**How to work.**
1. Fetch and read the real entry — definition, offset, first term, and the exact comment
   wording — BEFORE any mathematics. Not a snippet, not a summary. Variables are scoped
   by the sequence; reading a conjecture out of context can invert the result.
2. Check the entry hasn't already been settled. Conjectures from 2002-2012 are being
   cleared right now, within weeks. An old date proves nothing.
3. Search the literature for the mathematical objects, not the A-number.
4. For a disproof, compute before theorising. Scan the free parameter widely first.
5. Check whether the stated hypothesis is doing any work. Often the claim is true for a
   weaker reason, or the caveat is a classical theorem's hypothesis in disguise.
6. Prefer an iff-characterisation over a one-directional result.
7. Validate code against published values first. Compute the key object twice, by
   genuinely different algorithms.
8. Every number in a write-up must trace to an actual output — counts, bounds, worked
   examples, everything. Write the verification script separately from the paper and make
   it print every number the paper claims. That is how errors surface.

**Deliverables.** One PDF per completed result, named by sequential number plus verdict:
`29-PROOF.pdf`, `30-DISPROOF.pdf`. A-number inside the document, never in the filename.
Hand me the PDF only — not the .tex, not the .py. Deliver it **in the chat**, as an
attachment. After each find, also write out what the OEIS comment would look like in
plain-text house style; I don't post them, I just like seeing them. Keep this ledger
current as you go, and keep it short — add nulls to the dead list so they're never
rechecked twice.

**How to report.** Shortest possible. Simple language. Never explain the mathematics —
only what you did and what you need. Verdict, one line on what it is, any flag I should
act on, stop. No preamble, no plan, no recap of what I just said. If you need something
from me, say only the thing you need.

**On honesty.** Tell me plainly when something is null, elementary, or probably already
known. Don't upgrade "verified further" into "proved". Never pad the count to hit a
number I asked for — if I ask for three and you have one, tell me you have one. If a
claim depends on context you haven't verified, say so before writing it up, not after.
A withheld result costs me nothing; a wrong one costs me credibility. I have every result
checked by a separate instance, so flag anything you're less than certain about.

But once something is verified, state it plainly. The caution is for unverified claims,
not for conclusions you've actually checked. A correct result buried under caveats is
indistinguishable from a null.

**On the base rate.** Expect mostly nulls. That is correct, not failure. The seam is
being mined hard by several groups (Section 7) and the rate keeps falling. One clean
result is worth more than three forced ones.

---

# Conjecture-hunt ledger

Last updated 25 Aug 2026. Roster: **305 papers**, files `1-PROOF.pdf` … `305-PROOF.pdf`.
New results continue from **306-**.

---

## 0. HARD RULES

1. **Target must be labelled `Conjecture:` on the entry.** Not "It appears that",
   "Calculation suggests", "observed", "empirically", or a bare FORMULA line. The label
   is the whole test, regardless of how open or hard the claim is.
   Correctly excluded so far: A129453, A129455, A090494, A176898, A010051, A129439,
   A063289, A224479.
2. **Fetch the entry BEFORE doing any mathematics.** Learned the hard way on A070226:
   proved it from a search snippet, then found the proof already on the entry, posted
   19 days earlier. Snippets are stale.
3. **An old date means nothing.** Conjectures from 2002–2012 are being cleared right
   now, on a timescale of weeks.
4. **Never pad the count.** Report the true number. Say plainly when something is
   elementary, already known, or only a partial.
4b. **Counting: one settled conjecture = one result, even when many share one argument.**
   Decided 25 Aug 2026. A single theorem that closes twenty entries counts as twenty.
   Two consequences, both binding:
   - **Papers are written standalone.** No paper mentions the others, so each reads as a
     single submission. Attribution of a general statement and genuine prior-work notes
     stay in; a list of sibling entries does not.
   - **The overlap is still recorded here.** Say which blocks share an argument, so the
     roster is never handed over as more independent work than it is.
5. **Reports: shortest possible, no mathematics explained.** Verdict, one line on what
   it is, flags worth acting on, stop.

## 1. ACCESS (rewritten for Claude Code)

The chat-tool restriction is gone. **Do not ask the user to paste links.** Verified in
this environment on 25 Aug 2026:

- `curl` reaches OEIS directly. Constructed URLs are fine. `curl -sS -A "Mozilla/5.0"`.
- **The WebFetch tool gets 403 from oeis.org.** Use `curl` via Bash instead. WebFetch is
  still fine for arXiv, GitHub raw, and everything else.
- The JSON API works and is the right interface:
  `https://oeis.org/search?q=<query>&fmt=json&start=<n>`
  Returns a **bare JSON list** (not an object) of up to **10** entries per call. Fields:
  `number, name, offset, data, comment, formula, example, keyword, xref, link, author,
  reference, program, maple, mathematica, created, time, revision`.
- `&fmt=text` on the same URL prints `Showing 1-10 of <total>` — that is how to get the
  result count before deciding to sweep.
- `start=` paginates in steps of 10. Sweeping a few hundred results is cheap.
- Old bans are lifted: `/search?q=…` is allowed and is now the primary tool.
- Still avoid: `/history` pages and `?action=raw` (robots-blocked). `/wiki/Conjectures`
  is still a stub; ignore it.

## 2. HOW TO FIND TARGETS (rewritten for Claude Code)

Discovery is no longer the bottleneck. Sweep the API and filter locally.

**The one catch: OEIS search ignores quotes and punctuation.** `"Conjecture:"` is parsed
as the two loose words `conjecture` and `valuation`, etc. So the literal label cannot be
isolated server-side. The method is:

1. Query the API with `conjecture` plus toolkit vocabulary (Section 6).
2. Read `fmt=text` for the total, then page through with `start=`.
3. **Filter locally** — keep only entries where a `comment` or `formula` string actually
   starts with the literal label `Conjecture`. That enforces Hard Rule 1 mechanically
   instead of by eye.
4. Triage the survivors from the already-fetched JSON. No extra fetch needed: the full
   comment text is already in the response.

Because step 3 is a script, **build the index the old ledger said was impossible.** Cache
swept results to a local file so a session never re-sweeps ground already covered, and
cross-check every hit against Section 4 (dead) and Section 7 (competition) before
spending any time on it.

Web search is now a backup, not the primary route. Keep it for literature on the
mathematical objects (How to work, step 3).

**Do not** browse adjacent-sequence links, and **do not** fetch sibling entries on spec —
a sibling entry is not a sibling conjecture (A062367 has none, though A062368 does).

**Good signal:** an entry whose FORMULA section restates its own COMMENTS conjecture.
Seen on A005329, A129364, A062368 — it means the claim is true, elementary, and still
unproved. A later contributor restates a standing conjecture as fact and nobody removes
the label. This is now cheap to detect in a sweep: compare the two fields in the JSON.

## 3. RESULTS HELD

| file | verdict | entry | conjecture | contributor |
|---|---|---|---|---|
| 1 | PROOF | A047926 | count of `a²+b²+c² = 9^k` equals `(3^k+2k−1)/4` | Seidov 2012 |
| 2 | DISPROOF | A008365 | 13-rough ⟺ `n²⁴ mod 2310 ∈ {1,421,631,841}` | Detlefs 2011 |
| 3 | PROOF | A000040 | `k^f(n) ≡ 1 mod P_n` ⟺ `k` is `p_{n+1}`-rough | Detlefs 2014 |
| 4 | PROOF | A008364 | 11-rough ⟺ `n⁶ mod 210 ∈ {1,169}` | Detlefs 2011 |
| 5 | DISPROOF | A000040 | primes ⟺ Fermat base 2 **and** `F(n) ≡ ±1 mod n` | Detlefs 2014 |
| 6 | PROOF | A059324 | no primes `(p, q>p²)` with `q−p² = 6n−4` | Lallouet 2008 |
| 7 | PROOF | A000040 | primes ⟺ `n!·H_n ≡ n−1 mod n` | Detlefs 2010 |
| 8 | PROOF | A061002 | `den(H_p/H_{p−1})/num(H_{p−1}/p²) = p³` | Detlefs 2013 |
| 9 | PROOF | A063305 | `a(n) = 18n−41`, dim of newforms `Γ_1(32)` | Luschny 2012 |
| 10 | PROOF | A000071 | `F(k^n)−1` strong divisibility sequence, `k` odd | Bala 2022 |
| 11 | PROOF | A000139 | `a(n)` odd iff `n` odd Fibbinary | Bala 2025 |
| 12 | DISPROOF | A000364 | `a(n) mod k` periodic, period dividing `phi(k)` | Bala 2023 |
| 13 | PROOF | A059970 | nim-factorial `(2^n−1) = 1` | Layman 2001 |
| 14 | PROOF | A059970 | nim-factorial `(2^n+2^(n−1)−1) = 2` | Layman 2001 |
| 15 | PROOF | A036284 | `(x³+1)^(2^(n−1)−1)` divides `a(n)` in GF(2)[X] | Karttunen 1998 |
| 16 | PROOF | A036284 | Conjecture 2: one extra `(x+1)` factor | Karttunen 1998 |
| 17 | PROOF | A092287 | rectangular gcd product valuation | Kaydalov 2019 |
| 18 | PROOF | A129454 | `ord_p = Σ floor((n−1)/p^s)^3` — off-by-one fixed | Bala 2007 |
| 19 | PROOF | A129365 | Conjecture A: `a(n)` always integer | Bala 2007 |
| 20 | PROOF | A129365 | Conjecture D: de Polignac-shaped formula | Bala 2007 |
| 21 | PROOF | A037096 | `(x+1)^(3·2^(n−2)−1)` divides `a(n)` | Karttunen 1999 |
| 22 | PROOF | A037097 | `(x+1)^(2^(n−2)−1)` divides `a(n)`, exact | Karttunen 1999 |
| 23 | PROOF | A087726 | `a(n) = n²` iff `n` squarefree | Branman 2013 |
| 24 | PROOF | A063321 | closed form, dim of newforms `Γ_1(48)` | Luschny 2012 |
| 25 | PROOF | A063337 | `a(n) = 72n−155`, dim of newforms `Γ_1(64)` | Luschny 2012 |
| 26 | PROOF | A005329 | 2-factorials = inverse binomial transform of A075272 | Layman 2002 |
| 27 | PROOF | A129364 | `a(n)` divides A092287(n) | Bala 2007 |
| 28 | PROOF | A062368 | third inverse Möbius transform of `4^omega(n)` | Mathar 2012 |
| 29 | PROOF | A358272 | `a(n) = Σ_{k≤n} gcd(k,n)·λ(gcd(k,n))` | Schulte 2022 |
| 30 | PROOF | A358319 | `a(n) = Σ_{k≤n} gcd(k,n)·A076479(gcd(k,n))` | Schulte 2022 |
| 31 | PROOF | A327123 | `a(n) = Σ_{k≤n} sin(gcd(k,n)π/2)`; also corrects the entry | Yanev–Kotesovec 2024 |
| 32 | PROOF | A000670 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 33 | PROOF | A002050 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 34 | PROOF | A004123 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 35 | PROOF | A006531 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 36 | PROOF | A052895 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 37 | PROOF | A064618 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 38 | PROOF | A080253 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 39 | PROOF | A162314 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 40 | PROOF | A167137 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 41 | PROOF | A259533 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 42 | PROOF | A301921 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 43 | PROOF | A305550 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 44 | PROOF | A306082 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 45 | PROOF | A316142 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 46 | PROOF | A316143 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 47 | PROOF | A316144 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 48 | PROOF | A320352 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 49 | PROOF | A354242 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 50 | PROOF | A354253 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 51 | PROOF | A355409 | mod-`m` period divides `φ(m)`; e.g.f. `G(e^x−1)`, `G` integral | Bala |
| 52 | PROOF | A025268 | conjectured P-recursive recurrence | Mathar |
| 53 | PROOF | A025272 | conjectured P-recursive recurrence | Mathar |
| 54 | PROOF | A025756 | conjectured P-recursive recurrence | Mathar |
| 55 | PROOF | A025757 | conjectured P-recursive recurrence | Mathar |
| 56 | PROOF | A051292 | conjectured P-recursive recurrence | Mathar |
| 57 | PROOF | A054341 | conjectured P-recursive recurrence | Mathar |
| 58 | PROOF | A064088 | conjectured P-recursive recurrence | Mathar |
| 59 | PROOF | A064089 | conjectured P-recursive recurrence | Mathar |
| 60 | PROOF | A064090 | conjectured P-recursive recurrence | Mathar |
| 61 | PROOF | A064091 | conjectured P-recursive recurrence | Mathar |
| 62 | PROOF | A064092 | conjectured P-recursive recurrence | Mathar |
| 63 | PROOF | A080243 | conjectured P-recursive recurrence | Mathar |
| 64 | PROOF | A090413 | conjectured P-recursive recurrence | Mathar |
| 65 | PROOF | A097188 | conjectured P-recursive recurrence | Mathar |
| 66 | PROOF | A097331 | conjectured P-recursive recurrence | Mathar |
| 67 | PROOF | A098520 | conjectured P-recursive recurrence | Mathar |
| 68 | PROOF | A098521 | conjectured P-recursive recurrence | Mathar |
| 69 | PROOF | A098662 | conjectured P-recursive recurrence | Mathar |
| 70 | PROOF | A099363 | conjectured P-recursive recurrence | Mathar |
| 71 | PROOF | A100095 | conjectured P-recursive recurrence | Mathar |
| 72 | PROOF | A100096 | conjectured P-recursive recurrence | Mathar |
| 73 | PROOF | A100097 | conjectured P-recursive recurrence | Mathar |
| 74 | PROOF | A100098 | conjectured P-recursive recurrence | Mathar |
| 75 | PROOF | A100099 | conjectured P-recursive recurrence | Mathar |
| 76 | PROOF | A100193 | conjectured P-recursive recurrence | Mathar |
| 77 | PROOF | A102879 | conjectured P-recursive recurrence | Mathar |
| 78 | PROOF | A102880 | conjectured P-recursive recurrence | Mathar |
| 79 | PROOF | A104722 | conjectured P-recursive recurrence | Mathar |
| 80 | PROOF | A105695 | conjectured P-recursive recurrence | Mathar |
| 81 | PROOF | A105864 | conjectured P-recursive recurrence | Mathar |
| 82 | PROOF | A109263 | conjectured P-recursive recurrence | Mathar |
| 83 | PROOF | A110199 | conjectured P-recursive recurrence | Mathar |
| 84 | PROOF | A114121 | conjectured P-recursive recurrence | Mathar |
| 85 | PROOF | A114190 | conjectured P-recursive recurrence | Mathar |
| 86 | PROOF | A114464 | conjectured P-recursive recurrence | Mathar |
| 87 | PROOF | A141353 | conjectured P-recursive recurrence | Mathar |
| 88 | PROOF | A154623 | conjectured P-recursive recurrence | Mathar |
| 89 | PROOF | A157003 | conjectured P-recursive recurrence | Mathar |
| 90 | PROOF | A157021 | conjectured P-recursive recurrence | Mathar |
| 91 | PROOF | A157100 | conjectured P-recursive recurrence | Mathar |
| 92 | PROOF | A162548 | conjectured P-recursive recurrence | Mathar |
| 93 | PROOF | A166696 | conjectured P-recursive recurrence | Mathar |
| 94 | PROOF | A171416 | conjectured P-recursive recurrence | Mathar |
| 95 | PROOF | A174808 | conjectured P-recursive recurrence | Mathar |
| 96 | PROOF | A184018 | conjectured P-recursive recurrence | Mathar |
| 97 | PROOF | A185089 | conjectured P-recursive recurrence | Mathar |
| 98 | PROOF | A186341 | conjectured P-recursive recurrence | Mathar |
| 99 | PROOF | A188312 | conjectured P-recursive recurrence | Mathar |
| 100 | PROOF | A188314 | conjectured P-recursive recurrence | Mathar |
| 101 | PROOF | A003440 | conjectured P-recursive recurrence | Mathar |
| 102 | PROOF | A014533 | conjectured P-recursive recurrence | Mathar |
| 103 | PROOF | A025244 | conjectured P-recursive recurrence | Mathar |
| 104 | PROOF | A025245 | conjectured P-recursive recurrence | Mathar |
| 105 | PROOF | A025248 | conjectured P-recursive recurrence | Mathar |
| 106 | PROOF | A025251 | conjectured P-recursive recurrence | Mathar |
| 107 | PROOF | A025567 | conjectured P-recursive recurrence | Mathar |
| 108 | PROOF | A026030 | conjectured P-recursive recurrence | Mathar |
| 109 | PROOF | A026135 | conjectured P-recursive recurrence | Mathar |
| 110 | PROOF | A048775 | conjectured P-recursive recurrence | Mathar |
| 111 | PROOF | A055217 | conjectured P-recursive recurrence | Mathar |
| 112 | PROOF | A059279 | conjectured P-recursive recurrence | Mathar |
| 113 | PROOF | A068551 | conjectured P-recursive recurrence | Mathar |
| 114 | PROOF | A071717 | conjectured P-recursive recurrence | Mathar |
| 115 | PROOF | A073155 | conjectured P-recursive recurrence | Mathar |
| 116 | PROOF | A082134 | conjectured P-recursive recurrence | Mathar |
| 117 | PROOF | A089324 | conjectured P-recursive recurrence | Mathar |
| 118 | PROOF | A091699 | conjectured P-recursive recurrence | Mathar |
| 119 | PROOF | A097192 | conjectured P-recursive recurrence | Mathar |
| 120 | PROOF | A101500 | conjectured P-recursive recurrence | Mathar |
| 121 | PROOF | A101602 | conjectured P-recursive recurrence | Mathar |
| 122 | PROOF | A102318 | conjectured P-recursive recurrence | Mathar |
| 123 | PROOF | A102319 | conjectured P-recursive recurrence | Mathar |
| 124 | PROOF | A105865 | conjectured P-recursive recurrence | Mathar |
| 125 | PROOF | A105872 | conjectured P-recursive recurrence | Mathar |
| 126 | PROOF | A108296 | conjectured P-recursive recurrence | Mathar |
| 127 | PROOF | A108600 | conjectured P-recursive recurrence | Mathar |
| 128 | PROOF | A108623 | conjectured P-recursive recurrence | Mathar |
| 129 | PROOF | A112700 | conjectured P-recursive recurrence | Mathar |
| 130 | PROOF | A114191 | conjectured P-recursive recurrence | Mathar |
| 131 | PROOF | A114194 | conjectured P-recursive recurrence | Mathar |
| 132 | PROOF | A114584 | conjectured P-recursive recurrence | Mathar |
| 133 | PROOF | A114589 | conjectured P-recursive recurrence | Mathar |
| 134 | PROOF | A114590 | conjectured P-recursive recurrence | Mathar |
| 135 | PROOF | A114851 | conjectured P-recursive recurrence | Mathar |
| 136 | PROOF | A115256 | conjectured P-recursive recurrence | Mathar |
| 137 | PROOF | A116881 | conjectured P-recursive recurrence | Mathar |
| 138 | PROOF | A118974 | conjectured P-recursive recurrence | Mathar |
| 139 | PROOF | A122920 | conjectured P-recursive recurrence | Mathar |
| 140 | PROOF | A124431 | conjectured P-recursive recurrence | Mathar |
| 141 | PROOF | A126568 | conjectured P-recursive recurrence | Mathar |
| 142 | PROOF | A126931 | conjectured P-recursive recurrence | Mathar |
| 143 | PROOF | A127154 | conjectured P-recursive recurrence | Mathar |
| 144 | PROOF | A127361 | conjectured P-recursive recurrence | Mathar |
| 145 | PROOF | A128723 | conjectured P-recursive recurrence | Mathar |
| 146 | PROOF | A128732 | conjectured P-recursive recurrence | Mathar |
| 147 | PROOF | A128734 | conjectured P-recursive recurrence | Mathar |
| 148 | PROOF | A128743 | conjectured P-recursive recurrence | Mathar |
| 149 | PROOF | A128746 | conjectured P-recursive recurrence | Mathar |
| 150 | PROOF | A128750 | conjectured P-recursive recurrence | Mathar |
| 151 | PROOF | A132364 | conjectured P-recursive recurrence | Mathar |
| 152 | PROOF | A132900 | conjectured P-recursive recurrence | Mathar |
| 153 | PROOF | A133306 | conjectured P-recursive recurrence | Mathar |
| 154 | PROOF | A134389 | conjectured P-recursive recurrence | Mathar |
| 155 | PROOF | A135334 | conjectured P-recursive recurrence | Mathar |
| 156 | PROOF | A141342 | conjectured P-recursive recurrence | Mathar |
| 157 | PROOF | A141351 | conjectured P-recursive recurrence | Mathar |
| 158 | PROOF | A143013 | conjectured P-recursive recurrence | Mathar |
| 159 | PROOF | A143954 | conjectured P-recursive recurrence | Mathar |
| 160 | PROOF | A143955 | conjectured P-recursive recurrence | Mathar |
| 161 | PROOF | A151483 | conjectured P-recursive recurrence | Mathar |
| 162 | PROOF | A157418 | conjectured P-recursive recurrence | Mathar |
| 163 | PROOF | A159771 | conjectured P-recursive recurrence | Mathar |
| 164 | PROOF | A160823 | conjectured P-recursive recurrence | Mathar |
| 165 | PROOF | A162481 | conjectured P-recursive recurrence | Mathar |
| 166 | PROOF | A165201 | conjectured P-recursive recurrence | Mathar |
| 167 | PROOF | A165203 | conjectured P-recursive recurrence | Mathar |
| 168 | PROOF | A165537 | conjectured P-recursive recurrence | Mathar |
| 169 | PROOF | A165540 | conjectured P-recursive recurrence | Mathar |
| 170 | PROOF | A166135 | conjectured P-recursive recurrence | Mathar |
| 171 | PROOF | A166300 | conjectured P-recursive recurrence | Mathar |
| 172 | PROOF | A166587 | conjectured P-recursive recurrence | Mathar |
| 173 | PROOF | A166694 | conjectured P-recursive recurrence | Mathar |
| 174 | PROOF | A168503 | conjectured P-recursive recurrence | Mathar |
| 175 | PROOF | A171556 | conjectured P-recursive recurrence | Mathar |
| 176 | PROOF | A173993 | conjectured P-recursive recurrence | Mathar |
| 177 | PROOF | A174013 | conjectured P-recursive recurrence | Mathar |
| 178 | PROOF | A174107 | conjectured P-recursive recurrence | Mathar |
| 179 | PROOF | A176332 | conjectured P-recursive recurrence | Mathar |
| 180 | PROOF | A176479 | conjectured P-recursive recurrence | Mathar |
| 181 | PROOF | A176605 | conjectured P-recursive recurrence | Mathar |
| 182 | PROOF | A179648 | conjectured P-recursive recurrence | Mathar |
| 183 | PROOF | A182401 | conjectured P-recursive recurrence | Mathar |
| 184 | PROOF | A182879 | conjectured P-recursive recurrence | Mathar |
| 185 | PROOF | A182881 | conjectured P-recursive recurrence | Mathar |
| 186 | PROOF | A182887 | conjectured P-recursive recurrence | Mathar |
| 187 | PROOF | A182904 | conjectured P-recursive recurrence | Mathar |
| 188 | PROOF | A184120 | conjectured P-recursive recurrence | Mathar |
| 189 | PROOF | A186940 | conjectured P-recursive recurrence | Mathar |
| 190 | PROOF | A188482 | conjectured P-recursive recurrence | Mathar |
| 191 | PROOF | A185020 | conjectured P-recursive recurrence | Mathar |
| 192 | PROOF | A000781 | conjectured P-recursive recurrence | Mathar |
| 193 | PROOF | A050168 | conjectured P-recursive recurrence | Mathar |
| 194 | PROOF | A071684 | conjectured P-recursive recurrence | Mathar |
| 195 | PROOF | A081207 | conjectured P-recursive recurrence | Mathar |
| 196 | PROOF | A102882 | conjectured P-recursive recurrence | Mathar |
| 197 | PROOF | A157125 | conjectured P-recursive recurrence | Mathar |
| 198 | PROOF | A026029 | conjectured P-recursive recurrence | Mathar |
| 199 | PROOF | A026031 | conjectured P-recursive recurrence | Mathar |
| 200 | PROOF | A101596 | conjectured P-recursive recurrence | Mathar |
| 201 | PROOF | A025257 | conjectured P-recursive recurrence | Mathar |
| 202 | PROOF | A126180 | conjectured P-recursive recurrence | Mathar |
| 203 | PROOF | A126322 | conjectured P-recursive recurrence | Mathar |
| 204 | PROOF | A126323 | conjectured P-recursive recurrence | Mathar |
| 205 | PROOF | A135335 | conjectured P-recursive recurrence | Mathar |
| 206 | PROOF | A136304 | conjectured P-recursive recurrence | Mathar |
| 207 | PROOF | A189053 | conjectured P-recursive recurrence | Mathar |
| 208 | PROOF | A189176 | conjectured P-recursive recurrence | Mathar |
| 209 | PROOF | A190166 | conjectured P-recursive recurrence | Mathar |
| 210 | PROOF | A190724 | conjectured P-recursive recurrence | Mathar |
| 211 | PROOF | A190725 | conjectured P-recursive recurrence | Mathar |
| 212 | PROOF | A190736 | conjectured P-recursive recurrence | Mathar |
| 213 | PROOF | A191307 | conjectured P-recursive recurrence | Mathar |
| 214 | PROOF | A191309 | conjectured P-recursive recurrence | Mathar |
| 215 | PROOF | A191313 | conjectured P-recursive recurrence | Mathar |
| 216 | PROOF | A191319 | conjectured P-recursive recurrence | Mathar |
| 217 | PROOF | A191398 | conjectured P-recursive recurrence | Mathar |
| 218 | PROOF | A191526 | conjectured P-recursive recurrence | Mathar |
| 219 | PROOF | A191531 | conjectured P-recursive recurrence | Mathar |
| 220 | PROOF | A191585 | conjectured P-recursive recurrence | Mathar |
| 221 | PROOF | A191786 | conjectured P-recursive recurrence | Mathar |
| 222 | PROOF | A191790 | conjectured P-recursive recurrence | Mathar |
| 223 | PROOF | A191796 | conjectured P-recursive recurrence | Mathar |
| 224 | PROOF | A191993 | conjectured P-recursive recurrence | Mathar |
| 225 | PROOF | A208355 | conjectured P-recursive recurrence | Mathar |
| 226 | PROOF | A210496 | conjectured P-recursive recurrence | Mathar |
| 227 | PROOF | A217333 | conjectured P-recursive recurrence | Mathar |
| 228 | PROOF | A217711 | conjectured P-recursive recurrence | Mathar |
| 229 | PROOF | A220902 | conjectured P-recursive recurrence | Mathar |
| 230 | PROOF | A225887 | conjectured P-recursive recurrence | Mathar |
| 231 | PROOF | A226434 | conjectured P-recursive recurrence | Mathar |
| 232 | PROOF | A228770 | conjectured P-recursive recurrence | Mathar |
| 233 | PROOF | A228771 | conjectured P-recursive recurrence | Mathar |
| 234 | PROOF | A254314 | conjectured P-recursive recurrence | Mathar |
| 235 | PROOF | A257072 | conjectured P-recursive recurrence | Mathar |
| 236 | PROOF | A257178 | conjectured P-recursive recurrence | Mathar |
| 237 | PROOF | A257290 | conjectured P-recursive recurrence | Mathar |
| 238 | PROOF | A257300 | conjectured P-recursive recurrence | Mathar |
| 239 | PROOF | A257388 | conjectured P-recursive recurrence | Mathar |
| 240 | PROOF | A257515 | conjectured P-recursive recurrence | Mathar |
| 241 | PROOF | A257838 | conjectured P-recursive recurrence | Mathar |
| 242 | PROOF | A270661 | conjectured P-recursive recurrence | Mathar |
| 243 | PROOF | A270724 | conjectured P-recursive recurrence | Mathar |
| 244 | PROOF | A278472 | conjectured P-recursive recurrence | Mathar |
| 245 | PROOF | A279014 | conjectured P-recursive recurrence | Mathar |
| 246 | PROOF | A025175 | conjectured P-recursive recurrence | Mathar |
| 247 | PROOF | A025249 | conjectured P-recursive recurrence | Mathar |
| 248 | PROOF | A025256 | conjectured P-recursive recurrence | Mathar |
| 249 | PROOF | A025269 | conjectured P-recursive recurrence | Mathar |
| 250 | PROOF | A025270 | conjectured P-recursive recurrence | Mathar |
| 251 | PROOF | A025275 | conjectured P-recursive recurrence | Mathar |
| 252 | PROOF | A025754 | conjectured P-recursive recurrence | Mathar |
| 253 | PROOF | A025755 | conjectured P-recursive recurrence | Mathar |
| 254 | PROOF | A026027 | conjectured P-recursive recurrence | Mathar |
| 255 | PROOF | A063395 | conjectured P-recursive recurrence | Mathar |
| 256 | PROOF | A067299 | conjectured P-recursive recurrence | Mathar |
| 257 | PROOF | A072100 | conjectured P-recursive recurrence | Mathar |
| 258 | PROOF | A097180 | conjectured P-recursive recurrence | Mathar |
| 259 | PROOF | A097189 | conjectured P-recursive recurrence | Mathar |
| 260 | PROOF | A098519 | conjectured P-recursive recurrence | Mathar |
| 261 | PROOF | A098664 | conjectured P-recursive recurrence | Mathar |
| 262 | PROOF | A101601 | conjectured P-recursive recurrence | Mathar |
| 263 | PROOF | A103821 | conjectured P-recursive recurrence | Mathar |
| 264 | PROOF | A105849 | conjectured P-recursive recurrence | Mathar |
| 265 | PROOF | A106271 | conjectured P-recursive recurrence | Mathar |
| 266 | PROOF | A106272 | conjectured P-recursive recurrence | Mathar |
| 267 | PROOF | A110198 | conjectured P-recursive recurrence | Mathar |
| 268 | PROOF | A112703 | conjectured P-recursive recurrence | Mathar |
| 269 | PROOF | A116383 | conjectured P-recursive recurrence | Mathar |
| 270 | PROOF | A118093 | conjectured P-recursive recurrence | Mathar |
| 271 | PROOF | A119012 | conjectured P-recursive recurrence | Mathar |
| 272 | PROOF | A127363 | conjectured P-recursive recurrence | Mathar |
| 273 | PROOF | A133305 | conjectured P-recursive recurrence | Mathar |
| 274 | PROOF | A133307 | conjectured P-recursive recurrence | Mathar |
| 275 | PROOF | A133308 | conjectured P-recursive recurrence | Mathar |
| 276 | PROOF | A141222 | conjectured P-recursive recurrence | Mathar |
| 277 | PROOF | A164586 | conjectured P-recursive recurrence | Mathar |
| 278 | PROOF | A166078 | conjectured P-recursive recurrence | Mathar |
| 279 | PROOF | A166588 | conjectured P-recursive recurrence | Mathar |
| 280 | PROOF | A167481 | conjectured P-recursive recurrence | Mathar |
| 281 | PROOF | A174195 | conjectured P-recursive recurrence | Mathar |
| 282 | PROOF | A181933 | conjectured P-recursive recurrence | Mathar |
| 283 | PROOF | A185087 | conjectured P-recursive recurrence | Mathar |
| 284 | PROOF | A188460 | conjectured P-recursive recurrence | Mathar |
| 285 | PROOF | A192480 | conjectured P-recursive recurrence | Mathar |
| 286 | PROOF | A194724 | conjectured P-recursive recurrence | Mathar |
| 287 | PROOF | A210064 | conjectured P-recursive recurrence | Mathar |
| 288 | PROOF | A211278 | conjectured P-recursive recurrence | Mathar |
| 289 | PROOF | A215973 | conjectured P-recursive recurrence | Mathar |
| 290 | PROOF | A218185 | conjectured P-recursive recurrence | Mathar |
| 291 | PROOF | A227081 | conjectured P-recursive recurrence | Mathar |
| 292 | PROOF | A262768 | conjectured P-recursive recurrence | Mathar |
| 293 | PROOF | A273351 | conjectured P-recursive recurrence | Mathar |
| 294 | PROOF | A274295 | conjectured P-recursive recurrence | Mathar |
| 295 | PROOF | A115967 | conjectured P-recursive recurrence | Mathar |
| 296 | PROOF | A182892 | conjectured P-recursive recurrence | Mathar |
| 297 | PROOF | A182894 | conjectured P-recursive recurrence | Mathar |
| 298 | PROOF | A000483 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 299 | PROOF | A001712 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 300 | PROOF | A002867 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 301 | PROOF | A034863 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 302 | PROOF | A051524 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 303 | PROOF | A081046 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 304 | PROOF | A081052 | conjectured P-recursive recurrence (e.g.f.) | Mathar |
| 305 | PROOF | A111779 | conjectured P-recursive recurrence (e.g.f.) | Mathar |

### Caveats to disclose when handing these over

- **Papers 1, 3, 18, 22 are disproofs wearing a proof's filename.** The posted statement
  is false as written; each paper corrects the indexing/wording first, then proves the
  intended reading. Never present them without that.
- **19 and 27 are the same mathematics** on two entries (A129365 = A092287/A129364).
  Both papers say so. Not independent results.
- **13/14, 15/16 are pairs sharing one proof**; the second of each costs one extra line.
- **9, 24, 25:** the whole A063xxx family is **off by one** — the entry name says
  "weight n", the data is the weight-(n−1) value. First term is `−1`, an impossible
  dimension, a sentinel for weight 1 (which has no formula). A proof aimed at the name
  rather than the data would conclude these are false. Each paper states this first.
- **Paper 20 is exposed.** A129365 Conjecture D is in the Lean benchmark (as are B and C,
  already taken). Papers 13–19, 21–28 are clear of it. Re-verified 25 Aug 2026 against
  the live list: A129365 is the only one of the 28 that appears.
- **Paper 4:** a 2014 comment already asserted it true with a verification recipe; the
  paper adds the proof and the reason for the two residues. Thinner novelty.
- **Papers 52–305 share one method** (254 entries; 298–305 use the e.g.f. variant). Mathar's conjectured holonomic
  recurrences. Each is settled by the same three steps: the entry's algebraic g.f. lies in
  `Q(x)[√D]`; the recurrence is equivalent to the residual `B(x) = Σ_i x^i (p_i(θ+i)A)(x)`
  being a polynomial; `B` is computed exactly in that field. Only the entry's `G.f.` and
  the coefficient polynomials differ. Every one was additionally checked by evaluating the
  recurrence on the entry's own published terms in integer arithmetic, and every entry was
  re-fetched live before use to confirm it was still labelled and unproved.
- **Papers 32–51 share one theorem.** Twenty entries, one proof: e.g.f. `G(e^x−1)` with
  `G` integral ⇒ eventually periodic mod `m` with period dividing `φ(m)`. Only the
  identification of `G` differs. **You decided these count as twenty results**, and the
  papers are written standalone — no paper mentions the others, so each reads as a single
  submission. Know the overlap yourself when handing them over together.
  **A000436 is deliberately NOT claimed** — its e.g.f. `cos x/cos 3x` is not of the
  required form, but its recovered coefficients are integral as far as computed, so it is
  left open in the paper. Do not count it.
- **31 flags a live error on A327123.** Eldar's posted multiplicative formula gives
  `a(p^e) = 1` for `p ≡ 1 mod 4`; the correct value is `p^e`. It contradicts the entry's
  own DATA from n=5. The conjecture is unaffected.
- **29 and 30 are one piece of mathematics applied twice.** Both are the gcd-sum lemma
  `Σ_{k≤n} f(gcd(k,n)) = (f∗φ)(n)` plus a local-factor computation; only the local
  computation differs. Both papers say so. Not independent results.
- **29 and 30 are elementary, and both entries already carry the answer unlabelled.**
  A358272 has Oudra's formula `a(n) = Σ_{d|n} λ(d)·d·φ(n/d)` (May 2025); A358319 has
  "Equals Dirichlet convolution of A000010 and n·A076479". Each is one application of
  the lemma from the conjecture. Disclose this — the novelty is thin.

## 4. DEAD — do not revisit

Already resolved on the live entry, or carrying no conjecture at all.

Resolved: A050295, A067274, A072592, A067793, A067745, A008364 (Dec 20 comment),
A000040 (Dec 2011 and the *first* Sep 2010 criterion), A000010/A006519/A000215 (Fried
2025), A063170 (Amdeberhan–Callan–Moll 2012), A092287 square case (Greathouse 2013),
A092143, A129365 B and C (Adamczewski 2026), A005251 (Fried 2025), A039004 (Hendel 2015
+ Israel disproof), A034496 (Noe 2010), **A070226 (Eldar, 6 Aug 2026)**, A098016,
**A067336 (Nguyen Tuan Anh, Mar 2025)**, **A155867 (recurrence derived on the entry)**,
**A006472 (Himane, arXiv:2404.08646, 2024)**, **A000680 (Fried, Nov 2025)**,
**A384531 (Radcliffe, June 2025 — proof linked from the entry itself, label not removed;
same gcd-sum family as 29/30, do not mistake it for open)**.

No conjecture on the entry: A051190, A224479, A036286, A059971, A364812, A224497,
A027871, A062367, A136380 (and the whole A136378–A136386 block), A063318, A063369,
A063224, A129439.

## 5. HARD — needs a new idea

| entry | obstruction |
|---|---|
| A051924 | converse is a Wolstenholme-composite problem, open |
| A000984 | McIntosh's conjecture, open |
| A000006 | equivalent to Legendre's conjecture |
| A001146 | converse is an `n \| 2ⁿ−1` problem |
| A049048 | scanned all composites `≤10^7` and all pairs `m<n≤200`; every gcd prime, so no composite modulus. Counterexample needs two primes `>n`; exists heuristically but enormous |
| A054979 | contains "3 divides n" as a sub-claim — open, only a `10^664` lower bound |
| A082613 | search statement on palindromes; terms `~5·10^12` by n=27, verified to n=50 |
| A036840/A036845 | equivalent to boundedness of the `sigma(phi(x))` orbit |
| A057856 | literal form false by parity; intended form is generalized-Fermat primality, terms pairwise coprime so no covering argument |
| A060318 | huge stated bound; base-3 digit condition on `2^k`, Erdős-adjacent (unverified) |
| A001227 | needs three further entry definitions just to state; deep area |
| A281180 A281183 A281184 A281440 | Bala's `φ(k)²` periodicity; e.g.f.s are series reversions of trig integrals, not `G(e^x−1)` — different mechanism, untouched |
| A298826 | conjectures relate to each other but the base definition (A298825/n) is tied to Hardy–Littlewood / twin primes; only partials available |
| A000436 A000657 A002105 A012780 A126156 A143138 A143139 | same φ(k) periodicity wording as paper 32 but e.g.f. NOT of the form `G(e^x−1)` — outside that theorem, still open |

## 6. TOOLKIT — what actually closes things

- **Layer-cake counting** for gcd/lcm/min/max: `v_p(gcd(x_1..x_d)) = #{s : p^s divides
  all}`. Sum over a box, swap order, conditions separate. This *is* Legendre in `d`
  dimensions. Closed 17, 18, 19, 20, 27. Pair with nested floors
  `floor(n/(kq)) = floor(floor(n/q)/k)` and `M² − Σ k·floor(M/k) = Σ (M mod k)`.
- **Transform conjectures, two forms.** "X is the binomial transform of Y" → e.g.f.s,
  where the transform is multiplication by `e^x`; rewrite each side's own recurrence as a
  functional equation and check they differ by that factor (paper 26). "X is the k-th
  Möbius transform of Y" or "Dirichlet convolution of…" → both sides multiplicative, so
  compare local factors at one prime (paper 28). **Highest win rate of anything here.**
- **Bit columns:** find a symmetry of the column, read off a polynomial factor. Halved
  period gives `(x+1)^(L/2)`; a half-period flip `b(k+q) = 1−b(k)` gives `(x+1)^(3q−1)`.
  Works because `x^(2^j)+1 = (x+1)^(2^j)` in characteristic 2. Closed 15, 16, 21, 22.
- **Finite fields / nimbers:** numbers below `2^(2^k)` form a field; consecutive integers
  from 0 form an `F_2`-subspace; product of all nonzero elements is 1 in characteristic 2;
  `prod_{b in K}(z+b) = z^|K| + z`. Closed 13, 14.
- **Legendre + Kummer** for any parity or valuation claim (paper 11).
- **Wilson/Wolstenholme in disguise:** criteria built from `n!`, `H_n`, Stirling numbers
  or double factorials collapse to `(n−1)! mod n` (papers 7, 8).
- **For a disproof, compute first.** Scan the free parameter widely before theorising.
- **Conjectured recurrences → a residual polynomial.** For `Σ_i p_i(n) a(n−i) = 0` with
  g.f. `A`, set `θ = x·d/dx`; then `Σ_n (Σ_i p_i(n)a(n−i)) x^n = Σ_i x^i (p_i(θ+i)A)(x)`.
  The conjecture holds for all `n > d` iff that residual is a polynomial of degree `d`.
  When `A` is algebraic of degree 2, write `A = u + v√D`: the field is closed under `θ`,
  so the test is exact rational-function cancellation — no series truncation, no numerics.
  Extend the field when needed: several entries need `Q(x)[√D1,√D2]`, where `θ` is still
  diagonal in the basis of square-root products, so the same test works unchanged.
  **This is the highest-yield tool in the file: 194 entries.**

  **Forget the search API. Clone the database.** `git clone --depth 1
  https://github.com/oeis/oeisdata` gives every entry as a text file (~3 GB, 398,648
  sequences, all fields). No login, no 200-result cap, no query guessing — grep it.
  `local_extract.py` does the extraction. This should be the FIRST move of any session.

  **Measured landscape of the whole database (25 Aug 2026):**
  - **15,585** labelled `Conjecture` lines across **13,760** entries. That is the universe.
  - **1,192** are P-recursive recurrences. Of those, **555** carry a `G.f.` line, **78**
    only an `E.g.f.`, **14** a loosely-worded one, and **623** have no generating
    function at all — those are out of reach of this method.
  - So the attackable set for the residual method is about **647**, and it converts at
    roughly 50%. Ceiling: **~330 papers**, not thousands.
  - The other big classes are **1,804** conjectured closed forms and **462** conjectured
    generating functions. Untouched, different methods needed, yield unknown.
  - Everything else (primality, permutation, finiteness, asymptotics) is not mechanically
    attackable.

  **Two soundness traps, both found the hard way — keep the guards.**
  1. *Polynomiality must actually be tested.* The residual test asks whether `B` is a
     polynomial. Checking only that its denominator is constant lets a transcendental
     residual through (`log(1-x)` has denominator 1). `is_polynomial` now calls
     `.is_polynomial(x)` on the result. Re-running all 255 proofs under the fixed test
     cost 2 of them.
  2. *Nested radicals must be refused.* `sqrt((2 - 2*sqrt(1-4*x) - 3*x)/x)` is degree 4
     but NOT multiquadratic — the reductions assume independent radicands and silently
     mis-reduce it. `_has_nested_radical` now rejects such expressions in both fields.
     This is what invalidated the original paper 170 (A166135); its conjecture still
     holds on every published term, but the proof was wrong, so it was withdrawn and the
     slot rebuilt from A107231. **A166135 remains open — do not count it.**

  **E.g.f. variant.** For entries giving an e.g.f., re-index the recurrence forward
  (`n = m+r`, `j = r-i`) so shifts become derivatives rather than integrals; then
  `B = Sum_j q_j(theta)[A^(j)]` and the same polynomiality test applies. Only 8 of 65
  such entries close: most e.g.f.s in this class are transcendental (`exp`, `log`,
  `cosh`) and fall outside an algebraic method entirely. Watch for two traps: parse `^(1/2)` as an exact rational or the
  arithmetic silently goes floating-point, and always confirm the posted `G.f.` really
  reproduces the entry's DATA before trusting it — that check is what catches a mangled
  parse. Most of the work is reading OEIS's `G.f.` lines: strip trailing prose and
  periods, resolve `c(x)`/`C(x)` (Catalan) and `M(x)` (Motzkin) and inline `where C=...`
  definitions, and allow the posted g.f. to be shifted by a few powers of `x` against the
  entry's own indexing.

### Signals worth opening
Garbled or self-contradictory wording; an idle hypothesis (check whether the caveat is
load-bearing, or is a classical theorem's hypothesis in disguise); a contributor stating
several instances of one pattern; a homemade object with no literature; FORMULA
restating COMMENTS.

### Discipline that caught real errors
Write the verification script separately from the paper and print every number the paper
claims. Implement the core operation twice by different algorithms. Check the entry's
offset and first term before assuming the indexing.

## 7. COMPETITION — assume it is closing fast

- **Lean benchmark of formalised open OEIS conjectures.** List at
  `github.com/google-deepmind/formal-conjectures`, branch `auto_oeis`, file
  `FormalConjectures/OEIS/Auto/THEOREM_MAPPING.txt`. Fetchable directly with WebFetch or
  curl on the raw.githubusercontent URL — no pasting needed. DeepMind proved 44
  (~May 2026); Adamczewski/Epoch resolved **147 of 492** at ~$50 each (arXiv:2608.11941,
  12 Aug 2026). Hits get annotated onto OEIS within days. **Fetch this list first each
  session and treat everything on it as gone.**
  *Open discrepancy (25 Aug 2026): that file currently yields 151 unique A-numbers, not
  492. Either a different file holds the full set or the branch moved. Unresolved.*
- **Tong Niu** — one-conjecture papers, 2026. Already taken: A002627, A025166, A176677,
  A214615, A045406, A001711, A348410. Route: generating function → first-order ODE →
  read off the recurrence, plus a "homogenisation" trick for `a(n) = p(n)a(n−1) + q(n)`
  which they say clears an entire class. **Assume easy recurrence conjectures are gone.**
- **Also active:** Sela Fried (dozens at once, 2024–25), Amiram Eldar (clearing entries
  in real time), MechMath. Kauers–Koutschan is picked clean.

Our edge is elsewhere: valuation counting, finite fields, bit columns, transforms.

## 8. WHERE FILES LIVE (Claude Code only)

**The session container is wiped when the session ends.** Anything not committed and
pushed is gone. So:

- This ledger lives in the GitHub repo and gets committed every time it changes.
- Finished PDFs get delivered in chat **and** committed to the repo, under `papers/`.
  The repo is the complete archive — papers 1–28 are already there.
- Google Drive folder **"OEIS Conjecture Results"**, id `1aI4ENDG73Yubbes7X1EmzOWcQFJP1zXa`.
  Every new numbered result gets uploaded there as soon as it is finished. Only finished
  proofs and disproofs go in — nothing partial, nothing exploratory.
- Nothing important stays only in the container.

**Drive cannot take the papers. Measured, 25 Aug 2026 — do not retry.** The connector
accepts file content only as base64 text typed inline in the tool call, so every upload
has to pass through a single response. Tested directly: a 92,000-character upload
overruns the per-response output cap. A LaTeX paper is 150–240KB, i.e. 200,000–320,000
base64 characters. It does not fit, and at that length a single mistyped character
would corrupt the PDF anyway.

- Small uploads do work — verified end to end with a 388-byte PDF. The folder is live.
- Recompression does not rescue it: of a 155KB paper, 74KB is embedded Computer Modern
  subsets, and that overhead is roughly fixed no matter the page count. `pikepdf`
  recompression saved 0.3%. Dropping T1 encoding or hyperref made it *bigger*.
- The only way under the line would be abandoning Computer Modern for base-14 fonts
  (Times/Helvetica), which changes the look. **Not acceptable — format matches the
  existing 28.**
- **So: the GitHub repo is the archive.** `git add` has no size limit and all 28 are
  already in `papers/`. Commit every new paper there. The user drags files to Drive
  themselves when they want them there.

## 9. HOW TO BUILD A PAPER

`pdflatex` is not in the image. Install it first:
`apt-get update -qq && apt-get install -y -qq --no-install-recommends texlive-latex-base
texlive-latex-recommended texlive-science texlive-fonts-recommended`

House format, taken from the existing 28 — match it:

- `article`, 11pt, a4paper, 1in margins, `amsmath/amssymb/amsthm`, `hyperref` with
  `colorlinks`. Computer Modern. Produced by pdfTeX.
- Title states the result and names the A-number. Author: Adrian Perez Fontelles,
  Independent researcher, then the date.
- Optional MSC line (papers 2 and 11 carry one).
- Abstract: the object, who conjectured it and when, and one sentence on the method.
- §1 "The conjecture" or "The sequence(s) and the conjecture" — give the definition, the
  first terms, then **quote the conjecture verbatim in a `quote` block with the
  contributor's name and date**, and state that it is still open as of the entry's
  "Last modified" line.
- Middle sections carry the mathematics, one idea per section.
- A "Verification" or "Computational verification" section near the end, reporting the
  ranges actually checked.
- "Concluding remarks" where there is something to say, then `thebibliography`, always
  citing the OEIS entry and the relevant comment by author and date.
- 3–5 pages. Explain every step — these are written to be read, not compressed.

Then: deliver the PDF in chat, and commit it to `papers/`.
