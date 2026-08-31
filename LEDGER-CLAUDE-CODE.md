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

Last updated 31 Aug 2026. Roster: **620 papers** (615 proofs, 5 disproofs), files `1-PROOF.pdf` … `620-PROOF.pdf`, **numbered by how hard the result was**: 1 is the hardest.
`rank-map.json` records the previous numbering. New results are ranked in, not appended.

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

| rank | verdict | entry | what the proof required |
|---|---|---|---|
| 1 | PROOF | A063305 | a separate argument for that one problem |
| 2 | PROOF | A063337 | a separate argument for that one problem |
| 3 | PROOF | A063321 | a separate argument for that one problem |
| 4 | PROOF | A061002 | a separate argument for that one problem |
| 5 | PROOF | A129365 | a separate argument for that one problem |
| 6 | PROOF | A129454 | a separate argument for that one problem |
| 7 | PROOF | A092287 | a separate argument for that one problem |
| 8 | PROOF | A129364 | a separate argument for that one problem |
| 9 | PROOF | A036284 | a separate argument for that one problem |
| 10 | PROOF | A036284 | a separate argument for that one problem |
| 11 | PROOF | A037097 | a separate argument for that one problem |
| 12 | PROOF | A037096 | a separate argument for that one problem |
| 13 | PROOF | A059970 | a separate argument for that one problem |
| 14 | PROOF | A059970 | a separate argument for that one problem |
| 15 | PROOF | A352117 | a separate argument for that one problem |
| 16 | PROOF | A305404 | a separate argument for that one problem |
| 17 | PROOF | A062368 | a separate argument for that one problem |
| 18 | PROOF | A005329 | a separate argument for that one problem |
| 19 | PROOF | A000071 | a separate argument for that one problem |
| 20 | PROOF | A000139 | a separate argument for that one problem |
| 21 | PROOF | A000040 | a separate argument for that one problem |
| 22 | PROOF | A087726 | a separate argument for that one problem |
| 23 | PROOF | A059324 | a separate argument for that one problem |
| 24 | PROOF | A047926 | a separate argument for that one problem |
| 25 | PROOF | A358272 | a separate argument for that one problem |
| 26 | PROOF | A358319 | a separate argument for that one problem |
| 27 | PROOF | A327123 | a separate argument for that one problem |
| 28 | DISPROOF | A000364 | a separate argument for that one problem |
| 29 | DISPROOF | A000040 | a separate argument for that one problem |
| 30 | DISPROOF | A008365 | a separate argument for that one problem |
| 31 | PROOF | A000670 | one theorem, proved once and applied to twenty entries |
| 32 | PROOF | A002050 | one theorem, proved once and applied to twenty entries |
| 33 | PROOF | A004123 | one theorem, proved once and applied to twenty entries |
| 34 | PROOF | A006531 | one theorem, proved once and applied to twenty entries |
| 35 | PROOF | A052895 | one theorem, proved once and applied to twenty entries |
| 36 | PROOF | A064618 | one theorem, proved once and applied to twenty entries |
| 37 | PROOF | A079144 | e.g.f. G(e^x-1) with G integral: a(n) mod k is an integer combination of n -> i^n |
| 38 | PROOF | A079144 | the same reduction, plus x^(p^r) = x^(p^(r-1)) mod p^r, for every shift |
| 39 | PROOF | A080253 | one theorem, proved once and applied to twenty entries |
| 40 | PROOF | A158690 | e.g.f. G(e^x-1) with G integral: a(n) mod k is an integer combination of n -> i^n |
| 41 | PROOF | A158690 | the same reduction, plus x^(p^r) = x^(p^(r-1)) mod p^r, for every shift |
| 42 | PROOF | A162314 | one theorem, proved once and applied to twenty entries |
| 43 | PROOF | A167137 | one theorem, proved once and applied to twenty entries |
| 44 | PROOF | A259533 | one theorem, proved once and applied to twenty entries |
| 45 | PROOF | A301921 | one theorem, proved once and applied to twenty entries |
| 46 | PROOF | A305550 | one theorem, proved once and applied to twenty entries |
| 47 | PROOF | A306082 | one theorem, proved once and applied to twenty entries |
| 48 | PROOF | A316142 | one theorem, proved once and applied to twenty entries |
| 49 | PROOF | A316143 | one theorem, proved once and applied to twenty entries |
| 50 | PROOF | A316144 | one theorem, proved once and applied to twenty entries |
| 51 | PROOF | A320352 | one theorem, proved once and applied to twenty entries |
| 52 | PROOF | A354242 | one theorem, proved once and applied to twenty entries |
| 53 | PROOF | A354253 | one theorem, proved once and applied to twenty entries |
| 54 | PROOF | A355409 | one theorem, proved once and applied to twenty entries |
| 55 | PROOF | A032098 | a conjectured closed form or g.f., proved against a recurrence derived from the entry |
| 56 | PROOF | A266072 | a conjectured closed form or g.f., proved against a recurrence derived from the entry |
| 57 | PROOF | A084703 | an entry equated to an m-section of another entry, decided from both entries' facts |
| 58 | PROOF | A111403 | an entry equated to an m-section of another entry, decided from both entries' facts |
| 59 | PROOF | A155543 | an entry equated to an m-section of another entry, decided from both entries' facts |
| 60 | PROOF | A208545 | a conjectured closed form or g.f., proved against a recurrence derived from the entry |
| 61 | PROOF | A227161 | a conjectured closed form or g.f., proved against a recurrence derived from the entry |
| 62 | PROOF | A393856 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 63 | PROOF | A393857 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 64 | PROOF | A393858 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 65 | PROOF | A393859 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 66 | DISPROOF | A141135 | a conjecture shown FALSE, with the recurrence that holds instead |
| 67 | DISPROOF | A076217 | a conjecture shown FALSE, with the recurrence that holds instead |
| 68 | PROOF | A129833 | creative telescoping with the boundary and range corrections carried through |
| 69 | PROOF | A306948 | creative telescoping with the boundary and range corrections carried through |
| 70 | PROOF | A129833 | creative telescoping with the boundary and range corrections carried through |
| 71 | PROOF | A000180 | creative telescoping with the boundary and range corrections carried through |
| 72 | PROOF | A127905 | a recurrence derived from the summand by creative telescoping |
| 73 | PROOF | A045742 | a recurrence derived from the summand by creative telescoping |
| 74 | PROOF | A243585 | a recurrence derived from the summand by creative telescoping |
| 75 | PROOF | A026005 | a recurrence derived from the summand by creative telescoping |
| 76 | PROOF | A359643 | the generating function derived from a coefficient-extraction definition |
| 77 | PROOF | A156894 | the generating function derived from a coefficient-extraction definition |
| 78 | PROOF | A156894 | the generating function derived from a coefficient-extraction definition |
| 79 | PROOF | A371753 | the generating function derived from a coefficient-extraction definition |
| 80 | PROOF | A226751 | the generating function derived from a coefficient-extraction definition |
| 81 | PROOF | A386830 | the generating function derived from a coefficient-extraction definition |
| 82 | PROOF | A172025 | the generating function derived from a coefficient-extraction definition |
| 83 | PROOF | A348410 | the generating function derived from a coefficient-extraction definition |
| 84 | PROOF | A243764 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 85 | PROOF | A243760 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 86 | PROOF | A285195 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 87 | PROOF | A243814 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 88 | PROOF | A055392 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 89 | PROOF | A025758 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 90 | PROOF | A308726 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 91 | PROOF | A243022 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 92 | PROOF | A168506 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 93 | PROOF | A239425 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 94 | PROOF | A025757 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 95 | PROOF | A242566 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 96 | PROOF | A270530 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 97 | PROOF | A101478 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 98 | PROOF | A025756 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 99 | PROOF | A097180 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 100 | PROOF | A097189 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 101 | PROOF | A127632 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 102 | PROOF | A130655 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 103 | PROOF | A166135 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 104 | PROOF | A212696 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 105 | PROOF | A261196 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 106 | PROOF | A270530 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 107 | PROOF | A185010 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 108 | PROOF | A185020 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 109 | PROOF | A200312 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 110 | PROOF | A025754 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 111 | PROOF | A097188 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 112 | PROOF | A097192 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 113 | PROOF | A158826 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 114 | PROOF | A159769 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 115 | PROOF | A294159 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 116 | PROOF | A392976 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 117 | PROOF | A162972 | a transcendental e.g.f., in a differential module over Q(x) |
| 118 | PROOF | A001465 | a transcendental e.g.f., in a differential module over Q(x) |
| 119 | PROOF | A085387 | a transcendental e.g.f., in a differential module over Q(x) |
| 120 | PROOF | A096471 | a transcendental e.g.f., in a differential module over Q(x) |
| 121 | PROOF | A000704 | a transcendental e.g.f., in a differential module over Q(x) |
| 122 | PROOF | A001724 | a transcendental e.g.f., in a differential module over Q(x) |
| 123 | PROOF | A066052 | a transcendental e.g.f., in a differential module over Q(x) |
| 124 | PROOF | A097204 | a transcendental e.g.f., in a differential module over Q(x) |
| 125 | PROOF | A053532 | a transcendental e.g.f., in a differential module over Q(x) |
| 126 | PROOF | A306948 | a transcendental e.g.f., in a differential module over Q(x) |
| 127 | PROOF | A000483 | a transcendental e.g.f., in a differential module over Q(x) |
| 128 | PROOF | A000276 | a transcendental e.g.f., in a differential module over Q(x) |
| 129 | PROOF | A002104 | a transcendental e.g.f., in a differential module over Q(x) |
| 130 | PROOF | A002538 | a transcendental e.g.f., in a differential module over Q(x) |
| 131 | PROOF | A066052 | a transcendental e.g.f., in a differential module over Q(x) |
| 132 | PROOF | A073591 | a transcendental e.g.f., in a differential module over Q(x) |
| 133 | PROOF | A108704 | a transcendental e.g.f., in a differential module over Q(x) |
| 134 | PROOF | A110322 | a transcendental e.g.f., in a differential module over Q(x) |
| 135 | PROOF | A185369 | a transcendental e.g.f., in a differential module over Q(x) |
| 136 | PROOF | A000276 | a transcendental e.g.f., in a differential module over Q(x) |
| 137 | PROOF | A000774 | a transcendental e.g.f., in a differential module over Q(x) |
| 138 | PROOF | A094905 | a transcendental e.g.f., in a differential module over Q(x) |
| 139 | PROOF | A098557 | a transcendental e.g.f., in a differential module over Q(x) |
| 140 | PROOF | A051560 | a transcendental e.g.f., in a differential module over Q(x) |
| 141 | PROOF | A129149 | a transcendental e.g.f., in a differential module over Q(x) |
| 142 | PROOF | A187252 | a transcendental e.g.f., in a differential module over Q(x) |
| 143 | PROOF | A005654 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 144 | PROOF | A116385 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 145 | PROOF | A005558 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 146 | PROOF | A065942 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 147 | PROOF | A081181 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 148 | PROOF | A081204 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 149 | PROOF | A005558 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 150 | PROOF | A005559 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 151 | PROOF | A005560 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 152 | PROOF | A005561 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 153 | PROOF | A005562 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 154 | PROOF | A081204 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 155 | PROOF | A081205 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 156 | PROOF | A213801 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 157 | PROOF | A006231 | a posted closed form against a derived holonomic recurrence |
| 158 | PROOF | A213203 | a posted closed form compared against the posted generating function |
| 159 | PROOF | A242429 | a posted closed form compared against the posted generating function |
| 160 | PROOF | A026018 | a posted closed form compared against the posted generating function |
| 161 | PROOF | A092634 | a posted closed form compared against the posted generating function |
| 162 | PROOF | A026026 | a posted closed form compared against the posted generating function |
| 163 | PROOF | A052227 | a posted closed form compared against the posted generating function |
| 164 | PROOF | A228329 | a posted closed form compared against the posted generating function |
| 165 | PROOF | A259457 | a posted closed form compared against the posted generating function |
| 166 | PROOF | A268554 | a posted closed form compared against the posted generating function |
| 167 | PROOF | A102319 | several independent square roots |
| 168 | PROOF | A115256 | several independent square roots |
| 169 | PROOF | A157125 | several independent square roots |
| 170 | PROOF | A102318 | several independent square roots |
| 171 | PROOF | A107587 | several independent square roots |
| 172 | PROOF | A218185 | several independent square roots |
| 173 | PROOF | A025567 | several independent square roots |
| 174 | PROOF | A071684 | several independent square roots |
| 175 | PROOF | A179648 | several independent square roots |
| 176 | PROOF | A184120 | several independent square roots |
| 177 | PROOF | A026163 | several independent square roots |
| 178 | PROOF | A102318 | several independent square roots |
| 179 | PROOF | A101500 | several independent square roots |
| 180 | PROOF | A102319 | several independent square roots |
| 181 | PROOF | A107587 | several independent square roots |
| 182 | PROOF | A072100 | several independent square roots |
| 183 | PROOF | A025567 | several independent square roots |
| 184 | PROOF | A334509 | an identity between different entries |
| 185 | PROOF | A298022 | an identity between different entries |
| 186 | PROOF | A273676 | an identity between different entries |
| 187 | PROOF | A273832 | an identity between different entries |
| 188 | PROOF | A319371 | an identity between different entries |
| 189 | PROOF | A110320 | an identity between different entries |
| 190 | PROOF | A309878 | an identity between different entries |
| 191 | PROOF | A315520 | an identity between different entries |
| 192 | PROOF | A346370 | an identity between different entries |
| 193 | PROOF | A176126 | the residual test over one square root, or none |
| 194 | PROOF | A191625 | the residual test over one square root, or none |
| 195 | PROOF | A186341 | the residual test over one square root, or none |
| 196 | PROOF | A026743 | the residual test over one square root, or none |
| 197 | PROOF | A191786 | the residual test over one square root, or none |
| 198 | PROOF | A210496 | the residual test over one square root, or none |
| 199 | PROOF | A182892 | the residual test over one square root, or none |
| 200 | PROOF | A270724 | the residual test over one square root, or none |
| 201 | PROOF | A190171 | the residual test over one square root, or none |
| 202 | PROOF | A257515 | the residual test over one square root, or none |
| 203 | PROOF | A190788 | the residual test over one square root, or none |
| 204 | PROOF | A095981 | the residual test over one square root, or none |
| 205 | PROOF | A212205 | the residual test over one square root, or none |
| 206 | PROOF | A270661 | the residual test over one square root, or none |
| 207 | PROOF | A157021 | the residual test over one square root, or none |
| 208 | PROOF | A165537 | the residual test over one square root, or none |
| 209 | PROOF | A166287 | the residual test over one square root, or none |
| 210 | PROOF | A174013 | the residual test over one square root, or none |
| 211 | PROOF | A178072 | the residual test over one square root, or none |
| 212 | PROOF | A182894 | the residual test over one square root, or none |
| 213 | PROOF | A114584 | the residual test over one square root, or none |
| 214 | PROOF | A164586 | the residual test over one square root, or none |
| 215 | PROOF | A189053 | the residual test over one square root, or none |
| 216 | PROOF | A182904 | the residual test over one square root, or none |
| 217 | PROOF | A274295 | the residual test over one square root, or none |
| 218 | PROOF | A226434 | the residual test over one square root, or none |
| 219 | PROOF | A257104 | the residual test over one square root, or none |
| 220 | PROOF | A108600 | the residual test over one square root, or none |
| 221 | PROOF | A114851 | the residual test over one square root, or none |
| 222 | PROOF | A125306 | the residual test over one square root, or none |
| 223 | PROOF | A166290 | the residual test over one square root, or none |
| 224 | PROOF | A228770 | the residual test over one square root, or none |
| 225 | PROOF | A257300 | the residual test over one square root, or none |
| 226 | PROOF | A089324 | the residual test over one square root, or none |
| 227 | PROOF | A104625 | the residual test over one square root, or none |
| 228 | PROOF | A113956 | the residual test over one square root, or none |
| 229 | PROOF | A116383 | the residual test over one square root, or none |
| 230 | PROOF | A162548 | the residual test over one square root, or none |
| 231 | PROOF | A173993 | the residual test over one square root, or none |
| 232 | PROOF | A244886 | the residual test over one square root, or none |
| 233 | PROOF | A157003 | the residual test over one square root, or none |
| 234 | PROOF | A162482 | the residual test over one square root, or none |
| 235 | PROOF | A163493 | the residual test over one square root, or none |
| 236 | PROOF | A191398 | the residual test over one square root, or none |
| 237 | PROOF | A135582 | the residual test over one square root, or none |
| 238 | PROOF | A139376 | the residual test over one square root, or none |
| 239 | PROOF | A346074 | the residual test over one square root, or none |
| 240 | PROOF | A190166 | the residual test over one square root, or none |
| 241 | PROOF | A025251 | the residual test over one square root, or none |
| 242 | PROOF | A228771 | the residual test over one square root, or none |
| 243 | PROOF | A025268 | the residual test over one square root, or none |
| 244 | PROOF | A025272 | the residual test over one square root, or none |
| 245 | PROOF | A162475 | the residual test over one square root, or none |
| 246 | PROOF | A385252 | the residual test over one square root, or none |
| 247 | PROOF | A114464 | the residual test over one square root, or none |
| 248 | PROOF | A127154 | the residual test over one square root, or none |
| 249 | PROOF | A135335 | the residual test over one square root, or none |
| 250 | PROOF | A165540 | the residual test over one square root, or none |
| 251 | PROOF | A171416 | the residual test over one square root, or none |
| 252 | PROOF | A188314 | the residual test over one square root, or none |
| 253 | PROOF | A247170 | the residual test over one square root, or none |
| 254 | PROOF | A254314 | the residual test over one square root, or none |
| 255 | PROOF | A270661 | the residual test over one square root, or none |
| 256 | PROOF | A003440 | the residual test over one square root, or none |
| 257 | PROOF | A110521 | the residual test over one square root, or none |
| 258 | PROOF | A114190 | the residual test over one square root, or none |
| 259 | PROOF | A116387 | the residual test over one square root, or none |
| 260 | PROOF | A128096 | the residual test over one square root, or none |
| 261 | PROOF | A135052 | the residual test over one square root, or none |
| 262 | PROOF | A157021 | the residual test over one square root, or none |
| 263 | PROOF | A160823 | the residual test over one square root, or none |
| 264 | PROOF | A166287 | the residual test over one square root, or none |
| 265 | PROOF | A174808 | the residual test over one square root, or none |
| 266 | PROOF | A185089 | the residual test over one square root, or none |
| 267 | PROOF | A186940 | the residual test over one square root, or none |
| 268 | PROOF | A190736 | the residual test over one square root, or none |
| 269 | PROOF | A219314 | the residual test over one square root, or none |
| 270 | PROOF | A100095 | the residual test over one square root, or none |
| 271 | PROOF | A100097 | the residual test over one square root, or none |
| 272 | PROOF | A191313 | the residual test over one square root, or none |
| 273 | PROOF | A191790 | the residual test over one square root, or none |
| 274 | PROOF | A273351 | the residual test over one square root, or none |
| 275 | PROOF | A278472 | the residual test over one square root, or none |
| 276 | PROOF | A108296 | the residual test over one square root, or none |
| 277 | PROOF | A116391 | the residual test over one square root, or none |
| 278 | PROOF | A110198 | the residual test over one square root, or none |
| 279 | PROOF | A182879 | the residual test over one square root, or none |
| 280 | PROOF | A182887 | the residual test over one square root, or none |
| 281 | PROOF | A135925 | the residual test over one square root, or none |
| 282 | PROOF | A007901 | the residual test over one square root, or none |
| 283 | PROOF | A025256 | the residual test over one square root, or none |
| 284 | PROOF | A025258 | the residual test over one square root, or none |
| 285 | PROOF | A000781 | the residual test over one square root, or none |
| 286 | PROOF | A025245 | the residual test over one square root, or none |
| 287 | PROOF | A025257 | the residual test over one square root, or none |
| 288 | PROOF | A025269 | the residual test over one square root, or none |
| 289 | PROOF | A025270 | the residual test over one square root, or none |
| 290 | PROOF | A025275 | the residual test over one square root, or none |
| 291 | PROOF | A032096 | the residual test over one square root, or none |
| 292 | PROOF | A102880 | the residual test over one square root, or none |
| 293 | PROOF | A111053 | the residual test over one square root, or none |
| 294 | PROOF | A152120 | the residual test over one square root, or none |
| 295 | PROOF | A159771 | the residual test over one square root, or none |
| 296 | PROOF | A166694 | the residual test over one square root, or none |
| 297 | PROOF | A166696 | the residual test over one square root, or none |
| 298 | PROOF | A191796 | the residual test over one square root, or none |
| 299 | PROOF | A217711 | the residual test over one square root, or none |
| 300 | PROOF | A278023 | the residual test over one square root, or none |
| 301 | PROOF | A279014 | the residual test over one square root, or none |
| 302 | PROOF | A000483 | the residual test over one square root, or none |
| 303 | PROOF | A026030 | the residual test over one square root, or none |
| 304 | PROOF | A026031 | the residual test over one square root, or none |
| 305 | PROOF | A048775 | the residual test over one square root, or none |
| 306 | PROOF | A116409 | the residual test over one square root, or none |
| 307 | PROOF | A126322 | the residual test over one square root, or none |
| 308 | PROOF | A128750 | the residual test over one square root, or none |
| 309 | PROOF | A143955 | the residual test over one square root, or none |
| 310 | PROOF | A165203 | the residual test over one square root, or none |
| 311 | PROOF | A168505 | the residual test over one square root, or none |
| 312 | PROOF | A176605 | the residual test over one square root, or none |
| 313 | PROOF | A181933 | the residual test over one square root, or none |
| 314 | PROOF | A191585 | the residual test over one square root, or none |
| 315 | PROOF | A215973 | the residual test over one square root, or none |
| 316 | PROOF | A234269 | the residual test over one square root, or none |
| 317 | PROOF | A236407 | the residual test over one square root, or none |
| 318 | PROOF | A270363 | the residual test over one square root, or none |
| 319 | PROOF | A098521 | the residual test over one square root, or none |
| 320 | PROOF | A100096 | the residual test over one square root, or none |
| 321 | PROOF | A100099 | the residual test over one square root, or none |
| 322 | PROOF | A105849 | the residual test over one square root, or none |
| 323 | PROOF | A105864 | the residual test over one square root, or none |
| 324 | PROOF | A105865 | the residual test over one square root, or none |
| 325 | PROOF | A108308 | the residual test over one square root, or none |
| 326 | PROOF | A114194 | the residual test over one square root, or none |
| 327 | PROOF | A115967 | the residual test over one square root, or none |
| 328 | PROOF | A117186 | the residual test over one square root, or none |
| 329 | PROOF | A120010 | the residual test over one square root, or none |
| 330 | PROOF | A124431 | the residual test over one square root, or none |
| 331 | PROOF | A124431 | the residual test over one square root, or none |
| 332 | PROOF | A126568 | the residual test over one square root, or none |
| 333 | PROOF | A132364 | the residual test over one square root, or none |
| 334 | PROOF | A141342 | the residual test over one square root, or none |
| 335 | PROOF | A155051 | the residual test over one square root, or none |
| 336 | PROOF | A157002 | the residual test over one square root, or none |
| 337 | PROOF | A157100 | the residual test over one square root, or none |
| 338 | PROOF | A166076 | the residual test over one square root, or none |
| 339 | PROOF | A166300 | the residual test over one square root, or none |
| 340 | PROOF | A168503 | the residual test over one square root, or none |
| 341 | PROOF | A174107 | the residual test over one square root, or none |
| 342 | PROOF | A174169 | the residual test over one square root, or none |
| 343 | PROOF | A176332 | the residual test over one square root, or none |
| 344 | PROOF | A184018 | the residual test over one square root, or none |
| 345 | PROOF | A188312 | the residual test over one square root, or none |
| 346 | PROOF | A188482 | the residual test over one square root, or none |
| 347 | PROOF | A191782 | the residual test over one square root, or none |
| 348 | PROOF | A217333 | the residual test over one square root, or none |
| 349 | PROOF | A257072 | the residual test over one square root, or none |
| 350 | PROOF | A261681 | the residual test over one square root, or none |
| 351 | PROOF | A073155 | the residual test over one square root, or none |
| 352 | PROOF | A105524 | the residual test over one square root, or none |
| 353 | PROOF | A114589 | the residual test over one square root, or none |
| 354 | PROOF | A114590 | the residual test over one square root, or none |
| 355 | PROOF | A162481 | the residual test over one square root, or none |
| 356 | PROOF | A174783 | the residual test over one square root, or none |
| 357 | PROOF | A188460 | the residual test over one square root, or none |
| 358 | PROOF | A188464 | the residual test over one square root, or none |
| 359 | PROOF | A190725 | the residual test over one square root, or none |
| 360 | PROOF | A191526 | the residual test over one square root, or none |
| 361 | PROOF | A191531 | the residual test over one square root, or none |
| 362 | PROOF | A211278 | the residual test over one square root, or none |
| 363 | PROOF | A026327 | the residual test over one square root, or none |
| 364 | PROOF | A081207 | the residual test over one square root, or none |
| 365 | PROOF | A102882 | the residual test over one square root, or none |
| 366 | PROOF | A182881 | the residual test over one square root, or none |
| 367 | PROOF | A191309 | the residual test over one square root, or none |
| 368 | PROOF | A191319 | the residual test over one square root, or none |
| 369 | PROOF | A191790 | the residual test over one square root, or none |
| 370 | PROOF | A273351 | the residual test over one square root, or none |
| 371 | PROOF | A025248 | the residual test over one square root, or none |
| 372 | PROOF | A025249 | the residual test over one square root, or none |
| 373 | PROOF | A026017 | the residual test over one square root, or none |
| 374 | PROOF | A071717 | the residual test over one square root, or none |
| 375 | PROOF | A081672 | the residual test over one square root, or none |
| 376 | PROOF | A104722 | the residual test over one square root, or none |
| 377 | PROOF | A109263 | the residual test over one square root, or none |
| 378 | PROOF | A118093 | the residual test over one square root, or none |
| 379 | PROOF | A118974 | the residual test over one square root, or none |
| 380 | PROOF | A121320 | the residual test over one square root, or none |
| 381 | PROOF | A126323 | the residual test over one square root, or none |
| 382 | PROOF | A128723 | the residual test over one square root, or none |
| 383 | PROOF | A135334 | the residual test over one square root, or none |
| 384 | PROOF | A141351 | the residual test over one square root, or none |
| 385 | PROOF | A141353 | the residual test over one square root, or none |
| 386 | PROOF | A163824 | the residual test over one square root, or none |
| 387 | PROOF | A165201 | the residual test over one square root, or none |
| 388 | PROOF | A279014 | the residual test over one square root, or none |
| 389 | PROOF | A026027 | the residual test over one square root, or none |
| 390 | PROOF | A026135 | the residual test over one square root, or none |
| 391 | PROOF | A050168 | the residual test over one square root, or none |
| 392 | PROOF | A059279 | the residual test over one square root, or none |
| 393 | PROOF | A063395 | the residual test over one square root, or none |
| 394 | PROOF | A071722 | the residual test over one square root, or none |
| 395 | PROOF | A082134 | the residual test over one square root, or none |
| 396 | PROOF | A097331 | the residual test over one square root, or none |
| 397 | PROOF | A100193 | the residual test over one square root, or none |
| 398 | PROOF | A103973 | the residual test over one square root, or none |
| 399 | PROOF | A106181 | the residual test over one square root, or none |
| 400 | PROOF | A108623 | the residual test over one square root, or none |
| 401 | PROOF | A126180 | the residual test over one square root, or none |
| 402 | PROOF | A128732 | the residual test over one square root, or none |
| 403 | PROOF | A134389 | the residual test over one square root, or none |
| 404 | PROOF | A143013 | the residual test over one square root, or none |
| 405 | PROOF | A143954 | the residual test over one square root, or none |
| 406 | PROOF | A157418 | the residual test over one square root, or none |
| 407 | PROOF | A158196 | the residual test over one square root, or none |
| 408 | PROOF | A158197 | the residual test over one square root, or none |
| 409 | PROOF | A191585 | the residual test over one square root, or none |
| 410 | PROOF | A257290 | the residual test over one square root, or none |
| 411 | PROOF | A054341 | the residual test over one square root, or none |
| 412 | PROOF | A071715 | the residual test over one square root, or none |
| 413 | PROOF | A090413 | the residual test over one square root, or none |
| 414 | PROOF | A090826 | the residual test over one square root, or none |
| 415 | PROOF | A091699 | the residual test over one square root, or none |
| 416 | PROOF | A098664 | the residual test over one square root, or none |
| 417 | PROOF | A099363 | the residual test over one square root, or none |
| 418 | PROOF | A100098 | the residual test over one square root, or none |
| 419 | PROOF | A105872 | the residual test over one square root, or none |
| 420 | PROOF | A119975 | the residual test over one square root, or none |
| 421 | PROOF | A121724 | the residual test over one square root, or none |
| 422 | PROOF | A121725 | the residual test over one square root, or none |
| 423 | PROOF | A126931 | the residual test over one square root, or none |
| 424 | PROOF | A126932 | the residual test over one square root, or none |
| 425 | PROOF | A127361 | the residual test over one square root, or none |
| 426 | PROOF | A127363 | the residual test over one square root, or none |
| 427 | PROOF | A155051 | the residual test over one square root, or none |
| 428 | PROOF | A166078 | the residual test over one square root, or none |
| 429 | PROOF | A166587 | the residual test over one square root, or none |
| 430 | PROOF | A166588 | the residual test over one square root, or none |
| 431 | PROOF | A176006 | the residual test over one square root, or none |
| 432 | PROOF | A185087 | the residual test over one square root, or none |
| 433 | PROOF | A190724 | the residual test over one square root, or none |
| 434 | PROOF | A225887 | the residual test over one square root, or none |
| 435 | PROOF | A227081 | the residual test over one square root, or none |
| 436 | PROOF | A257178 | the residual test over one square root, or none |
| 437 | PROOF | A257388 | the residual test over one square root, or none |
| 438 | PROOF | A257838 | the residual test over one square root, or none |
| 439 | PROOF | A001712 | the residual test over one square root, or none |
| 440 | PROOF | A025175 | the residual test over one square root, or none |
| 441 | PROOF | A025577 | the residual test over one square root, or none |
| 442 | PROOF | A026023 | the residual test over one square root, or none |
| 443 | PROOF | A055217 | the residual test over one square root, or none |
| 444 | PROOF | A081052 | the residual test over one square root, or none |
| 445 | PROOF | A103821 | the residual test over one square root, or none |
| 446 | PROOF | A107231 | the residual test over one square root, or none |
| 447 | PROOF | A110199 | the residual test over one square root, or none |
| 448 | PROOF | A116406 | the residual test over one square root, or none |
| 449 | PROOF | A128734 | the residual test over one square root, or none |
| 450 | PROOF | A191307 | the residual test over one square root, or none |
| 451 | PROOF | A278472 | the residual test over one square root, or none |
| 452 | PROOF | A034863 | the residual test over one square root, or none |
| 453 | PROOF | A128652 | the residual test over one square root, or none |
| 454 | PROOF | A174195 | the residual test over one square root, or none |
| 455 | PROOF | A192480 | the residual test over one square root, or none |
| 456 | PROOF | A158495 | the residual test over one square root, or none |
| 457 | PROOF | A189176 | the residual test over one square root, or none |
| 458 | PROOF | A194724 | the residual test over one square root, or none |
| 459 | PROOF | A210474 | the residual test over one square root, or none |
| 460 | PROOF | A262768 | the residual test over one square root, or none |
| 461 | PROOF | A026029 | the residual test over one square root, or none |
| 462 | PROOF | A064088 | the residual test over one square root, or none |
| 463 | PROOF | A064089 | the residual test over one square root, or none |
| 464 | PROOF | A064090 | the residual test over one square root, or none |
| 465 | PROOF | A064091 | the residual test over one square root, or none |
| 466 | PROOF | A064092 | the residual test over one square root, or none |
| 467 | PROOF | A067299 | the residual test over one square root, or none |
| 468 | PROOF | A068551 | the residual test over one square root, or none |
| 469 | PROOF | A080243 | the residual test over one square root, or none |
| 470 | PROOF | A114191 | the residual test over one square root, or none |
| 471 | PROOF | A116881 | the residual test over one square root, or none |
| 472 | PROOF | A122920 | the residual test over one square root, or none |
| 473 | PROOF | A132864 | the residual test over one square root, or none |
| 474 | PROOF | A133305 | the residual test over one square root, or none |
| 475 | PROOF | A133306 | the residual test over one square root, or none |
| 476 | PROOF | A133307 | the residual test over one square root, or none |
| 477 | PROOF | A133308 | the residual test over one square root, or none |
| 478 | PROOF | A141222 | the residual test over one square root, or none |
| 479 | PROOF | A154623 | the residual test over one square root, or none |
| 480 | PROOF | A157328 | the residual test over one square root, or none |
| 481 | PROOF | A158196 | the residual test over one square root, or none |
| 482 | PROOF | A158197 | the residual test over one square root, or none |
| 483 | PROOF | A191993 | the residual test over one square root, or none |
| 484 | PROOF | A225034 | the residual test over one square root, or none |
| 485 | PROOF | A242172 | the residual test over one square root, or none |
| 486 | PROOF | A002867 | the residual test over one square root, or none |
| 487 | PROOF | A014533 | the residual test over one square root, or none |
| 488 | PROOF | A051524 | the residual test over one square root, or none |
| 489 | PROOF | A071264 | the residual test over one square root, or none |
| 490 | PROOF | A081046 | the residual test over one square root, or none |
| 491 | PROOF | A098519 | the residual test over one square root, or none |
| 492 | PROOF | A098520 | the residual test over one square root, or none |
| 493 | PROOF | A101596 | the residual test over one square root, or none |
| 494 | PROOF | A101601 | the residual test over one square root, or none |
| 495 | PROOF | A101602 | the residual test over one square root, or none |
| 496 | PROOF | A111779 | the residual test over one square root, or none |
| 497 | PROOF | A112703 | the residual test over one square root, or none |
| 498 | PROOF | A119012 | the residual test over one square root, or none |
| 499 | PROOF | A128057 | the residual test over one square root, or none |
| 500 | PROOF | A128746 | the residual test over one square root, or none |
| 501 | PROOF | A132900 | the residual test over one square root, or none |
| 502 | PROOF | A151483 | the residual test over one square root, or none |
| 503 | PROOF | A167481 | the residual test over one square root, or none |
| 504 | PROOF | A171556 | the residual test over one square root, or none |
| 505 | PROOF | A176479 | the residual test over one square root, or none |
| 506 | PROOF | A182401 | the residual test over one square root, or none |
| 507 | PROOF | A208355 | the residual test over one square root, or none |
| 508 | PROOF | A210064 | the residual test over one square root, or none |
| 509 | PROOF | A240558 | the residual test over one square root, or none |
| 510 | PROOF | A141771 | the residual test over one square root, or none |
| 511 | PROOF | A176606 | the residual test over one square root, or none |
| 512 | PROOF | A176607 | the residual test over one square root, or none |
| 513 | PROOF | A176609 | the residual test over one square root, or none |
| 514 | PROOF | A176610 | the residual test over one square root, or none |
| 515 | PROOF | A176611 | the residual test over one square root, or none |
| 516 | PROOF | A176675 | the residual test over one square root, or none |
| 517 | PROOF | A176749 | the residual test over one square root, or none |
| 518 | PROOF | A176750 | the residual test over one square root, or none |
| 519 | PROOF | A176751 | the residual test over one square root, or none |
| 520 | PROOF | A176752 | the residual test over one square root, or none |
| 521 | PROOF | A176753 | the residual test over one square root, or none |
| 522 | PROOF | A176754 | the residual test over one square root, or none |
| 523 | PROOF | A176755 | the residual test over one square root, or none |
| 524 | PROOF | A176756 | the residual test over one square root, or none |
| 525 | PROOF | A176757 | the residual test over one square root, or none |
| 526 | PROOF | A176759 | the residual test over one square root, or none |
| 527 | PROOF | A176828 | the residual test over one square root, or none |
| 528 | PROOF | A176829 | the residual test over one square root, or none |
| 529 | PROOF | A176830 | the residual test over one square root, or none |
| 530 | PROOF | A176832 | the residual test over one square root, or none |
| 531 | PROOF | A176854 | the residual test over one square root, or none |
| 532 | PROOF | A176855 | the residual test over one square root, or none |
| 533 | PROOF | A176856 | the residual test over one square root, or none |
| 534 | PROOF | A176857 | the residual test over one square root, or none |
| 535 | PROOF | A176858 | the residual test over one square root, or none |
| 536 | PROOF | A176859 | the residual test over one square root, or none |
| 537 | PROOF | A176952 | the residual test over one square root, or none |
| 538 | PROOF | A176953 | the residual test over one square root, or none |
| 539 | PROOF | A176956 | the residual test over one square root, or none |
| 540 | PROOF | A176957 | the residual test over one square root, or none |
| 541 | PROOF | A176958 | the residual test over one square root, or none |
| 542 | PROOF | A176959 | the residual test over one square root, or none |
| 543 | PROOF | A176962 | the residual test over one square root, or none |
| 544 | PROOF | A176964 | the residual test over one square root, or none |
| 545 | PROOF | A176966 | the residual test over one square root, or none |
| 546 | PROOF | A176967 | the residual test over one square root, or none |
| 547 | PROOF | A177123 | the residual test over one square root, or none |
| 548 | PROOF | A177124 | the residual test over one square root, or none |
| 549 | PROOF | A177125 | the residual test over one square root, or none |
| 550 | PROOF | A177126 | the residual test over one square root, or none |
| 551 | PROOF | A177127 | the residual test over one square root, or none |
| 552 | PROOF | A177128 | the residual test over one square root, or none |
| 553 | PROOF | A177129 | the residual test over one square root, or none |
| 554 | PROOF | A177130 | the residual test over one square root, or none |
| 555 | PROOF | A177131 | the residual test over one square root, or none |
| 556 | PROOF | A177163 | the residual test over one square root, or none |
| 557 | PROOF | A177165 | the residual test over one square root, or none |
| 558 | PROOF | A177166 | the residual test over one square root, or none |
| 559 | PROOF | A177167 | the residual test over one square root, or none |
| 560 | PROOF | A177168 | the residual test over one square root, or none |
| 561 | PROOF | A177169 | the residual test over one square root, or none |
| 562 | PROOF | A177170 | the residual test over one square root, or none |
| 563 | PROOF | A177171 | the residual test over one square root, or none |
| 564 | PROOF | A177172 | the residual test over one square root, or none |
| 565 | PROOF | A177175 | the residual test over one square root, or none |
| 566 | PROOF | A177177 | the residual test over one square root, or none |
| 567 | PROOF | A177178 | the residual test over one square root, or none |
| 568 | PROOF | A177179 | the residual test over one square root, or none |
| 569 | PROOF | A177180 | the residual test over one square root, or none |
| 570 | PROOF | A177181 | the residual test over one square root, or none |
| 571 | PROOF | A177182 | the residual test over one square root, or none |
| 572 | PROOF | A177183 | the residual test over one square root, or none |
| 573 | PROOF | A177184 | the residual test over one square root, or none |
| 574 | PROOF | A177185 | the residual test over one square root, or none |
| 575 | PROOF | A177197 | the residual test over one square root, or none |
| 576 | PROOF | A177198 | the residual test over one square root, or none |
| 577 | PROOF | A177199 | the residual test over one square root, or none |
| 578 | PROOF | A177200 | the residual test over one square root, or none |
| 579 | PROOF | A177203 | the residual test over one square root, or none |
| 580 | PROOF | A081670 | the known side is the entry's NAME rather than a formula line |
| 581 | PROOF | A085781 | the known side is the entry's NAME rather than a formula line |
| 582 | PROOF | A026019 | the known side is the entry's NAME rather than a formula line |
| 583 | PROOF | A052183 | the known side is the entry's NAME rather than a formula line |
| 584 | PROOF | A052204 | the known side is the entry's NAME rather than a formula line |
| 585 | PROOF | A157713 | the known side is the entry's NAME rather than a formula line |
| 586 | PROOF | A334511 | a posted closed form decided by the theory of hypergeometric terms |
| 587 | PROOF | A333905 | a posted closed form decided by the theory of hypergeometric terms |
| 588 | PROOF | A049486 | a posted closed form decided by the theory of hypergeometric terms |
| 589 | PROOF | A267879 | a posted closed form decided by the theory of hypergeometric terms |
| 590 | PROOF | A267802 | a posted closed form decided by the theory of hypergeometric terms |
| 591 | PROOF | A267847 | a posted closed form decided by the theory of hypergeometric terms |
| 592 | PROOF | A034267 | a posted closed form decided by the theory of hypergeometric terms |
| 593 | PROOF | A126501 | a posted closed form decided by the theory of hypergeometric terms |
| 594 | PROOF | A128153 | a posted closed form decided by the theory of hypergeometric terms |
| 595 | PROOF | A212938 | a posted closed form decided by the theory of hypergeometric terms |
| 596 | PROOF | A220250 | a posted closed form decided by the theory of hypergeometric terms |
| 597 | PROOF | A248434 | a posted closed form decided by the theory of hypergeometric terms |
| 598 | PROOF | A258547 | a posted closed form decided by the theory of hypergeometric terms |
| 599 | PROOF | A272706 | a posted closed form decided by the theory of hypergeometric terms |
| 600 | PROOF | A126089 | complete annihilation, tested in the Ore algebra Q(n)[N] |
| 601 | PROOF | A025271 | division of one posted operator by another |
| 602 | PROOF | A138164 | division of one posted operator by another |
| 603 | PROOF | A143017 | division of one posted operator by another |
| 604 | PROOF | A159772 | division of one posted operator by another |
| 605 | PROOF | A000986 | division of one posted operator by another |
| 606 | PROOF | A022917 | division of one posted operator by another |
| 607 | PROOF | A217447 | division of one posted operator by another |
| 608 | PROOF | A226302 | division of one posted operator by another |
| 609 | PROOF | A245088 | division of one posted operator by another |
| 610 | PROOF | A026165 | division of one posted operator by another |
| 611 | PROOF | A185966 | division of one posted operator by another |
| 612 | PROOF | A200753 | division of one posted operator by another |
| 613 | PROOF | A217358 | division of one posted operator by another |
| 614 | PROOF | A228960 | division of one posted operator by another |
| 615 | PROOF | A003435 | division of one posted operator by another |
| 616 | PROOF | A228331 | division of one posted operator by another |
| 617 | PROOF | A273019 | division of one posted operator by another |
| 618 | PROOF | A386834 | division of one posted operator by another |
| 619 | PROOF | A228330 | division of one posted operator by another |
| 620 | PROOF | A228333 | division of one posted operator by another |

### What the ranking means

Papers are numbered by how hard the result was, 1 hardest. The tiers, and where they fall:

| ranks | what the proof required |
|---|---|
| 1-30 | a separate argument found for that one problem |
| 31-50 | one theorem (Bala periodicity), proved once and applied to twenty entries |
| 51-52 | a conjectured closed form or generating function, proved by deriving a recurrence from what the entry asserts |
| 53-56 | a conjecture shown FALSE, with the correct recurrence derived and proved |
| 57-61 | telescoping over a range whose summand does not vanish at the ends |
| 52-55 | a recurrence derived from the summand by creative telescoping, then divided |
| 56-61 | the generating function itself derived, from a coefficient-extraction definition |
| 62-96 | a decision procedure over a generating function the entry already posts |
| 97-109 | a posted closed form, split on the parity of n, decided by hypergeometric-term theory |
| 110-118 | the same without the parity split |
| 119- | the rest of the decision procedures over a posted generating function |

So **ranks 1-61 are the ones with mathematics on the page**. Everything below that is a
real proof of a genuinely open conjecture, but the argument lives in the engine rather
than in the paper.

Ranks 97-118 are new and are the first results here that use **no generating function at
all**. The entry posts a closed form; a closed form is a sum of hypergeometric terms;
shift quotients of such terms are rational, similar terms group, and dissimilar ones are
linearly independent over the rational functions. So the conjecture becomes one
rational-function identity per similarity class, and cancellation decides each. That makes
it a decision procedure, not a search: it returns a proof or a refutation. Where the closed
form contains a floor, it is not a hypergeometric term at all and the argument does not
start; splitting on the parity of `n` repairs that, and both halves must then hold.

Ranks 55-60 are new. Those entries define the sequence only as `a(n) = [x^n] f(x)g(x)^n`
and post no generating function at all, so there was nothing for the older engines to
test. Reading the extraction as a contour integral and summing the geometric series
gives `A(t) = f(x(t))/(1 - t g'(x(t)))` where `x = t g(x)`; eliminating `x` by a
resultant produces the minimal polynomial, and the conjecture is then decided in that
algebraic function field. The generating function is derived, not quoted, which is why
these rank above the mechanical range.

Within the mechanical range the order is: recurrence derived from the summand by
telescoping, the boundary-corrected form first; generating function derived from a
coefficient-extraction definition; general algebraic function field; transcendental e.g.f.;
closed form split on parity; closed form directly; transcendental e.g.f.; several independent
square roots; identity between entries; the standard residual test; closed form against
the posted g.f.; and last, one posted operator dividing another -- honestly the
shallowest thing here, since both recurrences were already on the entry. Inside each tier
the order is by the size of the object handled: order of the recurrence first, then degree
of the residual.

`rank-map.json` records what each paper was numbered before. A new result is ranked into
position, not appended.


### Caveats to disclose when handing these over

- **Six withdrawn on 30 Aug 2026, and the one-letter gap that hid them.** The detector
  matched `verified` but not `verifies`, and `proved` but not `proves`. Six entries
  settle their conjecture in exactly those words:
  A081923 (Bala, 2013 -- Zeilberger's algorithm on Walsh's sum gives a first-order
  recurrence, "using this it is easy to verify that a(n) satisfies the second-order
  recurrence ... conjectured above"), A162477 (Munarini, 2017 -- "using this form of the
  g.f., it is straightforward to prove the above conjectured recurrence"), A093387 (a
  full proof on the entry, worked through both parities), A106271 and A106272
  (Hadjicostas, 2019 -- generating-function proofs ending "which proves the conjecture"),
  A155587 (Hadjicostas, 2020 -- "implies R. J. Mathar's conjecture"). A seventh,
  A156894, was caught before it was ever added: Bala, 2015, "the Maple command
  sumrecursion ... verifies this recurrence". The pattern now matches `verif\w*`,
  `prove[sndg]?`, `proving`, `shown`, `shows`, `sumrecursion`, `Zeilberger`, `deduce\w*`
  and `by induction`, and the whole roster was re-scanned against a local clone of the
  OEIS rather than by sampling.

- **What the same re-scan looked at and kept, with the wording, so it can be re-judged.**
  Twenty-two papers were flagged and read. Kept: A107587 (two papers) -- *"conjecture is
  true for n = 0..800; checked by Gennady Eremin"* is a finite check and settles nothing.
  A162548 and A185089 -- *"(Formula verified and used for computations. - Fung Lam)"*
  claims no proof and gives no method; the recurrence was used to extend the b-file.
  A346370 -- the entry says *"[verification needed]"*, which is the opposite. A163493 and
  A211278 -- both link Ekhad-Zeilberger, *"See subpages for rigorous derivations of g.f.,
  recurrence"*, but that is boilerplate about the authors' own recurrence and both
  Mathar conjectures postdate it and remain labelled conjectures. A228960 -- Bala's
  `sumrecursion` note proves *Kotesovec's* order-3 recurrence, not Mathar's order-4 one;
  that paper divides the second by the first, so the proved input makes it stronger, not
  weaker. A000071, A000139, A000040 (two papers), A087726, A129365, A000670 -- every hit
  is a different conjecture on the same entry (Hendel on McGarvey's floor formula,
  Zeilberger on West's enumeration, Wilson's theorem, Schmidt's squarefree half which
  the paper itself credits, Adamczewski on Conjectures B and C where the paper does A,
  Erlbacher on Kurkov's sum). **Read the hit, do not trust the match** -- it cuts both
  ways.

- **Four more withdrawn late on 26 Aug 2026, and the wording that caught them.** The
  entries settle the conjecture without any of the words the detector knew:
  *"Mathar's 4-term recurrence above follows easily from this"* (A105695),
  *"Mathar's recurrence above follows easily from this"* (A010845),
  *"R. J. Mathar's recurrence is correct"* (A126674),
  *"The conjecture is correct"* (A156849). The detector now also matches `is correct`,
  `are correct`, `follows easily`, `follows at once`, `follows immediately`,
  `derives from`, `is a consequence`.
  **Read the hit, do not trust the match.** On A092287 the same phrase *"The conjecture
  is correct"* refers to the square-case factorisation, while paper 17 settles the
  rectangular one, which is a different statement and still open. That paper stands.
  The four vacated slots were refilled by moving the four highest-numbered papers down,
  so the roster stays contiguous; `renumber.json` records the moves.

- **Thirteen papers were withdrawn on 26 Aug 2026 and their slots refilled.** Twelve of
  them (A051292, A098662, A102879, A114121, A025244, A112700, A128743, A136304, A220902,
  A025755, A127275, A081920) rest on conjectures the entry already records as settled.
  The old proof-marker regex looked for "proved/proof/is true/follows from" and missed
  the wording OEIS actually uses most: *"Conjecture confirmed using the differential
  equation…"*, *"Conjecture verified using…"*, *"verified by _Robert Israel_"*, *"can be
  verified by…"*. `recheck.py` and `verify_open.py` now match `confirm*`, `verified`,
  `checked using`, `establish*`, `settled`, `follows from the fact`, `immediate
  consequence`, `can be deduced`, `is a corollary`, and theorem wording.
  The thirteenth, A185020 (paper 191), was a soundness failure, not a novelty failure:
  its g.f. `sqrt((1-4x-sqrt(1-8x-32x^2))/24)/x` is a **nested radical**, and the
  multiquadratic reduction assumes independent radicands. The general algebraic engine
  now proves it properly (paper 391), as it does A166135 (paper 388), the entry that
  cost paper 170.
- **Five more were withdrawn the same day because someone else got there.**
  - 312 (A366932) and 313 (A367015): *"[This is now a theorem — N. J. A. Sloane,
    Dec 31 2025]"*.
  - 7 (A000040): *"[Conjecture is true, follows from Wilson's theorem — Rayhan Ahmed,
    May 21 2026]"*.
  - 4 (A008364): the entry's own comment gives the complete finite verification.
  - 20 (A129365, Conjecture D): resolved in the **OEIS Open** benchmark, machine-checked
    in Lean and scored CORRECT by all three models run against it.
- **Rule that follows: a settlement note is usually not the word "proof".** Search the
  entry for any wording that derives the claim from something already established, and
  read the hit before keeping the result. Numerical wording is the opposite signal and
  settles nothing: *"verified for n = 0..800"*, *"true for 1<=m<=n<=200"*, *"Formula
  verified and used for computations"* are finite checks, and papers 17, 69, 77 and 92
  stand on exactly that distinction.

- **Thirteen papers were withdrawn on 26 Aug 2026 and their slots refilled.** Twelve of
  them (A051292, A098662, A102879, A114121, A025244, A112700, A128743, A136304, A220902,
  A025755, A127275, A081920) rest on conjectures the entry already records as settled.
  The old proof-marker regex looked for "proved/proof/is true/follows from" and missed
  the wording OEIS actually uses most: *"Conjecture confirmed using the differential
  equation…"*, *"Conjecture verified using…"*, *"verified by _Robert Israel_"*, *"can be
  verified by…"*. `recheck.py` and `verify_open.py` now match `confirm*`, `verified`,
  `checked using`, `establish*`, `settled`, `follows from the fact`, `immediate
  consequence`, `can be deduced`, `is a corollary`.
  The thirteenth, A185020 (paper 191), is a soundness failure, not a novelty failure:
  its g.f. `sqrt((1-4x-sqrt(1-8x-32x^2))/24)/x` is a **nested radical**, and the
  multiquadratic reduction assumes independent radicands. This is the same fault that
  cost paper 170 (A166135). The guard now refuses it; the full re-run confirmed no other
  paper is affected.
  **Rule that follows: a settlement note is usually not the word "proof".** Search the
  entry for any wording that derives the recurrence from something already established,
  and read the hit before keeping the result. Numerical wording is the opposite signal
  and does *not* settle anything: *"verified for n = 0..800"*, *"true for 1<=m<=n<=200"*,
  *"Formula verified and used for computations"* are finite checks, and papers 17, 69, 77
  and 92 stand on exactly that distinction.

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
- **Papers 52–305 share one method** (254 entries; 298–305 use the e.g.f. variant).
- **Papers 329, 330 are NOT mechanical, and point at the one seam still worth mining.**
  Both are conjectures asserting that a sequence equals a *convergent infinite series*
  `Sum_k k^n * <hypergeometric in k> * r^k`. The trick: form the e.g.f. of the right-hand
  side and exchange the order of summation. The `k^n` is exactly what an e.g.f. produces,
  so the inner sum collapses to a known generating function evaluated at `e^x * r`, and
  the awkward constants in the conjecture (the `3^(k+1/2)`, the `2^(-3k-1/2)`) turn out to
  be precisely the normalisation that makes it match. Tonelli justifies the swap on the
  disc where the e.g.f. is analytic, and comparing Taylor coefficients settles all `n` at
  once.
  **This also explains the caveats.** A352117's conjecture says `n > 0` because the sum
  omits `k = 0`, which removes a constant `1/sqrt(2)` from the e.g.f., and a constant can
  only disturb the coefficient of `x^0`. The method predicts the exact size of the failure
  at `n = 0`, and it checks out numerically.
  **Look for more of these**: `Conjecture: a(n) = Sum_{k>=0} k^n * ...` on an entry with a
  known e.g.f. It is a small class but each one is a real result, and no sweep finds them
  because the summand is an infinite series rather than an identity between finite objects.
- **Papers 306–313 are the closed-form variant** (8 entries). Same idea in a new place:
  the conjectured `f(n)` is a combination of `n^k r^n`, so its g.f. is `p(theta)` applied
  to `1/(1-r x)`; subtract the entry's posted g.f. and test the difference for being a
  polynomial. **Do not test for the difference being zero** — these claims almost always
  hold only past a small boundary, and requiring `F = A` scores every one of them as a
  mismatch. That mistake cost a full pass before it was spotted. Mathar's conjectured holonomic
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

### 30 Aug 2026: the entry's own NAME was never read

Every engine here has read `%F` lines for its known side, and `%N` never. The name is
the strongest fact an entry has: it is not a formula someone contributed later and might
have guessed, it is the DEFINITION.

- **213 entries** have a name of the form `a(n) = <formula>` and a conjectured recurrence.
  Ten are decided by `hyperterm.py` straight from the name. Six had no paper:
  **A026019, A052183, A052204, A081670, A085781, A157713** — all six re-checked open on
  the live OEIS. The other four were already covered (A034863, A052227, A068551, A191993).
- Widening the pattern from "the name begins with a(n) =" to "the name contains a(n) ="
  gained nothing: the same ten. `name_run2.py`, honest null.
- **141 open entries are named "Expansion of &lt;g.f.&gt;"** and carry a conjectured
  recurrence. That name DEFINES the generating function, and every g.f. engine here was
  built for exactly that input and had never been shown it. `expname_run.py`.
- `nametex.py` / `makename.py` build the papers; the template differs from `hypertex.py`
  only in saying where the known side comes from.

### 30 Aug 2026: four bugs, one of them in a selector again

- **`conjlines.is_recurrence` matched only the word "Conjectur"**, never "Empirical", so
  every Empirical recurrence — most of the corpus — was refused before any engine saw it.
  The xref sweep additionally stripped the marker before calling it and reported **0**
  candidates where there are **376**.
- That is the **fourth** time a selector has silently reported the wrong pool
  (`equate_cands` 1214 vs 50, `emp_cands` 1 vs 1457, now 0 vs 376). **A count has no error
  bar.** `smoke.py` now holds a positive and a negative control for every selector; run it
  after touching one. It found two more the same hour: `timeoutrun.call` and
  `hyperterm.is_zero_sum` both return tuples, and a non-empty tuple is truthy, so
  `if is_zero_sum(...)` accepts everything. Both shipped callers index `[0]` correctly, so
  **no paper is affected** — the misuse was in the new sweep only.
- `extr_run.py` had **no settlement filter at all** and reported A114121 as new when the
  entry says "Conjecture verified ... - Robert Israel, Jul 27 2020". Filter added.
- Comparing a new conjecture against a shipped paper by extracting the PDF's text is
  **not reliable**: `^` comes back as `(cid:2)`, so three duplicates looked new. The sound
  test is whether the A-number appears in `rank-map.json` at all.

### 30 Aug 2026: three veins measured and closed

- **Line wrapping is not a problem.** `coverage.py` reported 86,673 lines continuing an
  unclosed previous line; that test counted a trailing comma as a continuation and was my
  own false alarm. Of **39,487** conjectural lines only **109** cannot stand alone, nearly
  all prose lists ("1) ... 2) ..."). The handful that are truncated recurrences
  (A025183, A036766, A089941, A107026, A108449) are truncated **in the live OEIS too** —
  nothing is recoverable. `trunc.py`.
- **Nonlinear (Cassini-type) identities: under 10 entries**, and the visible ones are
  already answered inside their own entries. A decision procedure exists — a degree-d
  polynomial in the shifts of an order-r P-recursive sequence lies in a module of
  dimension C(r+d,d) closed under shift, so an annihilator follows by linear algebra — but
  there is nothing to point it at. `polyid.py`.
- **Coefficient-extraction fact lines: zero new results.** 19 `a(n) = [x^n] f g^n` lines
  sit on entries whose recurrence is conjectured, and `diagonal.py` settles 18 of them —
  but 16 were already covered, one (A114121) is settled on the entry, and one (A190736)
  is the same conjecture as paper 246. `extr_run.py`. The routing gap was real; the yield
  was not.
- **Multi-formula lines gain nothing at scale.** `fsplit.py` correctly recovers A000027's
  closed form from the middle of "G.f.: x/(1-x)^2. E.g.f.: x*exp(x). a(n)=n.", but over
  every entry with a conjectural recurrence the split produced **0** new parseable known
  sides. Keep the tool — it is what makes the xref control pass — but do not claim it.
- **xref (a fact line naming other entries): 376 candidates, 1 result.** 115 of the first
  120 die because the referenced entry has no closed form of its own. A052183, and it was
  found independently by the name sweep. The addressable remainder is 51 entries where a
  reference is reachable only through a stated recurrence, which would need D-finite
  closure (sum of D-finite is D-finite; annihilator by linear algebra over Q(n)). Not
  built.
- **Hypergeometric closed forms: 59 fact lines, 15 parse, 10 with a rational shift
  quotient.** `hypconv.py` turns pFq into the sum it stands for so `zeilb.py` can take it.
  The rest carry KummerU, additive corrections, or half-integer parameters whose gamma
  ratios sympy will not cancel. Not yet swept.


### 30 Aug 2026 (later): "Expansion of ..." names, and a wrong threshold in 21 papers

- **`expname_run.py`: 141 open entries named "Expansion of &lt;g.f.&gt;", 61 proved.**
  The name DEFINES the generating function, and every g.f. engine here was built for that
  input and had never been shown it. Of the 61, 49 duplicate an existing paper, 1 is a
  second conjecture on an entry that already has one (A306948), and 11 are entries with no
  paper at all: **A053532, A071264, A098557, A105695, A117186, A135052, A162475, A162482,
  A174783, A239425, A247170** — all twelve re-checked open on the live OEIS.
- Roster is now **526**. Engines recorded per paper by the field actually used
  (quadratic / algfield / logexp), not by the sweep that found them.

**The EGF threshold was wrong in every logexp paper.** `logexp.residual_egf` re-indexes
forward — the transfer lemma sets `n = m + r` and `B` tracks `b(m)` — so a residual of
degree `d` gives the recurrence for **n > d + r**, not `n > d`. The corollary in
`makelogexppapers.py` said `n > d`, and 21 shipped papers stated a range wider than their
own algebra establishes. It surfaced because A098557 passed the sweep and then failed the
rebuild's integer check at n = 2, with a reported degree of 0.

- **Nothing shipped was false.** All 21 were re-checked at every index in the gap
  `(d, d+r]` against the published terms: the recurrence holds at all of them. The claim
  was true but under-justified.
- Fixed in the corollary, the theorem statement and `makeslots.integer_check`, and all 21
  rebuilt. Paper 69 (A162972) now reads `n > 7` where it read `n > 0`.
- The lesson is the ordinary case does not transfer: for an o.g.f. `[x^n]B` IS the
  recurrence's left side at `n`, so `n > d` is right there. Any future residual criterion
  must have its index convention checked against a case where the recurrence genuinely
  fails at a small index.

**Two infrastructure facts worth keeping.**

- **Background jobs do not advance between turns.** A sweep started with `nohup &` had 4
  minutes of CPU across an hour of wall clock, because the container is suspended while
  the session is idle. Long sweeps must run in the FOREGROUND in bounded slices:
  `runpool.py` keeps four children alive with a real per-item timeout, a wall-clock
  budget, and progress saved after every item so the sweep is resumable. The expansion
  sweep went from ~20 entries an hour to 91 in a single 520-second slice.
- **`rank.py` was reading `papers/`**, which after the first ranking holds the RANK
  numbering, so it would have copied whatever paper happened to sit at that rank. It now
  reads `papers-old-numbering/`, the `was`-keyed master. `makeslots.py` writes there too.


### 30 Aug 2026 (evening): the honest ceiling, and a full settlement audit

**The ceiling, measured.** With `conjlines` fixed the corpus holds **11,897 open
conjectural recurrences**. Of those:

| count | what the entry offers |
|---|---|
| 10,418 | **nothing stated as fact at all** |
| 587 | only prose |
| 521 | a generating function a parser accepts |
| 304 | a mathematical line **no parser here reads** |
| 37 | a closed form a parser accepts |
| 30 | a sum a parser accepts |

88% have no known side. That is the ceiling on everything built here, not a gap in the
engines. By NAME, **10,408 of the 11,894 are "Number of ..."** — a combinatorial
definition. The 304 unparsed mathematical lines are the one remaining actionable pocket.

**`known_run.py`: 230 entries with a usable known side and no paper, 14 proved, 9 open.**
Shipped: A010845, A066534, A129149, A158826, A187252, A212938, A220250, A258547.
A213801 was refused by its own rebuild (a period-4 term in the closed form the independent
check cannot decide) and is NOT shipped. Roster **534**.

- The four closed-form ones are **elementary**: `10^n - 2*18^n + 27^n`,
  `4^n - 2^(n-2)*(n+1)*(1-(-1)^n)`, `16*2^n - 4*n - 12`. Genuinely open Barker empiricals,
  but the mathematics is a Binet formula. Same for **A126501** (paper on Barker's closed
  form): the entry already states both the g.f. and the recurrence, so the conjecture is
  the Binet formula for a recurrence it gives you. Disclose this.
- The sweep went 8 → 10 → 14 as I fixed my own bugs in it: `parse_conj` rejects the
  `a(n) = <combination>` spelling (41 lost), `coeffs_of` stripped "Conjecture" but not
  "Empirical" (32 lost), and the integer check started at `order` rather than at the
  criterion's own threshold, rejecting three true results whose only failures sit below it.

**Full settlement audit of the roster — all 534 stand.** The local filter reads `%F` only,
but an entry can record a settlement in a `%C` comment or a `%H` link: five of fourteen
fresh results were settled that way (two by **Tong Niu**, arXiv 2605.08444 and 2605.12839).
So every distinct A-number in the roster was re-fetched live and scanned across formula,
comment, link, reference and example. 26 carried settlement wording; each was read.

- **All 26 are about a different statement**, a finite numeric check, or another
  conjecture on the same entry. Specifically: A107587 is "true for n = 0..800, checked by
  Eremin" — finite, not a proof. A162548 and A185089 say "Formula verified and used for
  computations" — numeric use, not a proof. A156894's THIRD conjecture is settled (Bala,
  Maple `sumrecursion`, which is Zeilberger's algorithm and therefore a proof) but my two
  papers there cover the first and second. A268554, A245088, A200753, A188464, A002538,
  A066052, A126501, A129365 all cite proofs of other statements on the same entry.
- Settled and NOT counted, found by this audit: **A002627, A045406** (Tong Niu),
  **A106272, A126674, A135339** (proved on the entry).
- **Add comments and links to the local settlement filter.** Reading `%F` alone is not
  enough, and the live re-check is what has been catching it.


### 30 Aug 2026 (night): are there conjectures outside the OEIS? Yes. Are they reachable? Almost none.

The OEIS is not the only database. Surveyed and measured:

**The Sequence Machine** (sequencedb.net; bulk data github.com/jonmaiga/sequence-machine-data,
4.8 GB, 1,099,250 files, cloned and scanned). 1,332,481 machine-generated sequences and
**1,974,684 conjectured formulas** for OEIS entries, produced by executing generated stack
machines and keeping whatever matches the published terms. Conjectural by construction --
the README says so. Roughly **930,000** are unproven, not already in the OEIS, and match
200+ terms. This is a real and enormous conjecture database. It yielded **nothing**, and
the reason is structural rather than a limit of the engines:

- **65% name another A-number** -- the cross-entry vein already measured here as 89%
  refusal, for the same reason: the referenced entry has no closed form of its own.
- **Rational generating functions: 5,160 distinct** (`smextract.py`). 4,287 sit on entries
  that already state a g.f.; 502 on entries stating a linear recurrence, where the g.f. is
  immediate; 357 have nothing usable; **14 genuine targets** (`sm_run.py`), of which the
  one that "proved" -- A140787, `ogf(1/(1-x-6x^2+4x^3+8x^4))` -- turned out to be the
  entry's own NAME, "Expansion of 1/((1+x)(2x+1)(-1+2x)^2)", multiplied out. **Net zero.**
- **Recurrences: 2,140 distinct** (`smrec.py`), down from ~11,500 program strings once
  reduced to coefficient vectors -- the machine emits many algebraically identical variants
  of one conjecture. 1,519 entries already give the g.f., 51 already state a recurrence,
  417 have nothing usable, **8 targets and all trivial** (`a(n)=a(n-1)`, `a(n)=a(n-2)`).
  **Net zero.**

The structure of the failure is worth keeping: a term-matching miner rediscovers the g.f.
of a sequence that HAS one, and for a sequence without one it emits something unprovable
for exactly the reason its OEIS conjecture was unprovable. **A machine miner cannot
manufacture a known side.**

**A repeat of a bug fixed hours earlier.** The first Sequence Machine filter tested %F
lines for a stated g.f. and did not test the NAME -- the very source exploited to get 18
results the same day. That is what let A140787 through.

Others, assessed and out of scope for this toolkit:

- **Ramanujan Machine** (ramanujanmachine.com) -- conjectured polynomial continued
  fractions for pi, e, zeta(3). Genuinely open and explicitly asking for proofs. The
  convergents satisfy a three-term recurrence with polynomial coefficients, which IS this
  machinery, but the conjecture is a LIMIT, and there is no asymptotics engine here. Its
  "prove our conjectures" page is a stale forum, newest entries ~3 years old.
- **LODA** (loda-lang.org) -- the same kind of mined-program database as the Sequence
  Machine; expect the same structural conclusion.
- **FindStat** -- combinatorial statistics and conjectured bijections. Different domain,
  and the site returned 503.
- **Erdos Problems**, **Formal Conjectures** (DeepMind, Lean + mathlib), **Open Problem
  Garden** -- curated famous open problems. Far outside a P-recursive symbolic toolkit.
- **R. J. Mathar's arXiv output** -- Dirichlet series and prime-zeta tables, not lists of
  conjectured recurrences. His recurrence conjectures live in the OEIS itself.

**Conclusion: for this toolkit the OEIS is the source, and its measured ceiling stands** --
11,897 open conjectural recurrences, 10,418 of them with nothing stated as fact.


### 30 Aug 2026 (late): openness is now decided FIRST, and three papers withdrawn

**Three papers shipped today rested on conjectures their own entries already settle.**
The settlement filter matched "follows from" as adjacent words, and all three entries say
"follows **easily** from":

- **A010845** -- "The e.g.f. y = exp(x)/(1-3x) satisfies (1-3x)y' = (4-3x)y. Mathar's
  recurrence above follows easily from this."
- **A066534** -- Peter Bala, Sep 23 2013: "Mathar's conjectural third-order recurrence
  above is an easy consequence of Jovovic's first-order recurrence a(n)=n*(a(n-1)+2^(n-1))."
- **A105695** -- "Mathar's 4-term recurrence above follows easily from this."

All three withdrawn and recorded in `settled-manual.json`, together with **A105750**
(Bala: "Mathar's third-order recurrence above follows easily from this"), which the new
filter caught before a paper was built. Roster **534 -> 531**, then **532** with A176126.

**Openness is now a front-end filter, not a post-hoc check** (`openness.py`,
`open_index.json`, built by `openindex.py`). Proving first and checking after spends the
expensive half of the work on conjectures that were already answered -- 5 of 14 in one
sweep -- and is what let those three ship. The index says **11,842 of 12,167 conjectural
recurrences are still open, 325 flagged for reading.** Every sweep filters through it
first.

Two things the filter had to learn:

- **Read every tag, not %F.** A002627 and A045406 carry Tong Niu's arXiv proofs as `%H`
  links; A126674 says "R. J. Mathar's recurrence is correct" in a `%C` comment.
- **"follows from" needs a gap for an adverb**, plus "is an easy consequence of", "can be
  derived/shown", "no longer a conjecture", "was settled". And `FINITE` must override:
  A107587's "true for n = 0..800, checked by Eremin" is not a proof and the entry stays
  open.

A flag is a **reason to read, not a verdict** -- 26 of 26 flagged papers in the roster
audit turned out to be about a different statement on the same entry.

**`statedrec_run.py`: a recurrence stated as FACT is the strongest known side there is.**
If the entry asserts L(a)=0 and conjectures C(a)=0, divide C = QL + R in the Ore algebra;
C being a left multiple of L is sufficient but NOT necessary, since the stated L need not
be minimal, so `oremod.vanishes` decides the residual properly. Only **15 entries** in the
corpus state one recurrence and conjecture another (the first regex missed lines beginning
"a(n) = ...", which is most of them -- its character class omitted the letter a). 9 proved,
7 already covered, 2 new, and one of those two (A105750) turned out settled.

**A176126 is the one new result**, and it is a clean one. The entry states
`a(n) = 3*a(n-4) - 3*a(n-8) + a(n-12)`, giving denominator `(1-x^4)^3`; the numerator
carries a factor `(1+x)^3` that cancels, leaving `(x-1)^3*(x^2+1)^3` -- which is exactly
the conjectured order-9 recurrence's denominator. Verified through the generating function
independently of the Ore argument.


### 30 Aug 2026 (night, later): 69 results from a mistyped prefix

**`fzparse.py` / `fz_run.py`: 70 entries, 70 proved, 69 with no paper. Roster 532 -> 601.**

Seventy entries with an open conjectured recurrence state their generating function as

    G.f f: f(z)=(1-sqrt(1-4*z*(a(0)-z*a(0)^2+z*a(1)+(k+l)*z^2/(1-z)+k*z^2/(1-z)^2)))/(2*z) (k=0, l=1)

and **every parser here refused all seventy**, for three reasons at once: the prefix is
usually mistyped "G.f f:" with no full stop, the variable is z rather than x, and the
expression carries free parameters k, l plus a(0) and a(1) -- whose values sit in the
parenthetical at the end of the line and in the entry's own DATA.

That is an explicit QUADRATIC generating function, one square root over Q(x), which is the
field the residual-polynomial criterion was built for first. Once read, all seventy fall
immediately. All 69 without a paper were re-checked live before a single paper was built
(`fz_check.py`, 0 flagged).

**Be honest about what this is:** one family, one shared argument, entries A176605-A177203,
mostly Roger Bagula's. They are 69 distinct conjectures on 69 distinct entries and count as
such, and no paper mentions the others -- but the mathematics is one idea applied 69 times.

**How it was found:** by looking at the 95 "PLAIN" lines among the 304 that carry
mathematics no parser reads -- the residue after everything explicable was explained. 94 of
those 95 were "not written as a(n) = ...", and 66 of them were this one template.

### 30 Aug 2026: parity-split known sides -- correct, and null

`cfparse.parse(..., rounding=True)` now admits floor and ceiling, which `REFUSE` had been
blocking before the KNOWN check ever ran, so lifting the function guard alone changed
nothing. 116 entries state their fact side as two branches a(2n) = ..., a(2n+1) = ..., or
with arguments that round; `parity.halves` resolves the rounding exactly at n = 2m and
n = 2m+1 and hyperterm decides each branch. **16 proved, every one already covered by an
existing paper. Zero new.** The parser extension is right and worth keeping; the yield is
not there.

### 30 Aug 2026: the roster audit finishes clean

The three papers flagged by the widened wording that had not yet been read -- A006231,
A080253, A208355 -- are false positives from "can be obtained" and "can be derived" in
ordinary prose. Their papers prove Mathar recurrences and a mod-k periodicity. **All papers
stand.** False positives cost reading; false negatives cost credibility, so the wide net
stays.


### 31 Aug 2026: WHO poses these conjectures, and why that limits everything

A fair question was put: can the results be credited as solving a conjecture *a person*
posed and tried, rather than bulk machine output? The census settles it.

Of **42,205** conjecture statements in the corpus, by poser:

| count | poser | kind |
|---|---|---|
| 26,538 | (anonymous / inside a block) | mixed |
| 9,144 | Colin Barker | machine-fitted "Empirical:" g.f.s and recurrences, in bulk |
| 1,586 | R. J. Mathar | machine-found recurrences, in bulk |
| 870 | Simon Plouffe | bulk |
| 636 | Chai Wah Wu | considered |
| 309 | Vaclav Kotesovec | considered |
| 208 | Peter Bala | considered |
| 151 | Robert Israel | considered |
| 124 | N. J. A. Sloane | considered |
| 72 | Zhi-Wei Sun | considered, sometimes with a prize |

**502 of the roster's papers prove R. J. Mathar's conjectures.** That is not a choice --
it is the structure of the problem, and the reason is worth stating plainly:

- **2,004 conjectures come from considered human posers.** By shape: 578 linear
  recurrences, 440 positivity/inequality, 349 prose, 210 asymptotic, 142 generating
  function, 122 congruence, 106 closed form, 35 primality. Most of that is out of reach by
  kind, not by effort -- there is no engine here for positivity, primality or asymptotics.
- Of the **750 open entries with no paper carrying a human-posed FORMULA conjecture**,
  `universal.py` found **724 have no readable known side at all.** Zero proved.
- **Mathar's are provable because of WHERE he posts them.** He runs his recurrence search
  on entries that already carry a generating function, so the known side is there by
  construction. A human noticing a pattern posts it wherever the pattern is -- usually on
  an entry that states nothing.

That is the honest ceiling on "credit for a human conjecture", and it is not a parser gap.

### 31 Aug 2026: universal.py -- every route, every open conjecture

Rather than hunting shapes one at a time, `universal.py` offers every fact line on every
open entry to every reader in the project: stated recurrence (Ore division), generating
function, algebraic relation, coefficient extraction, closed form, parity split, sum,
cross-entry reference. Of 11,354 open entries with no paper, a cheap pre-filter leaves 428
that could possibly have a readable side; the rest state nothing.

**9 proved, all open, none previously in the roster:** A034267, A159769, A166761, A172025,
A213801, A248434, A294159, A348410, A392976. Roster **601 -> 610**.

New machinery this needed:

- **`universal._implicit`** reads "G.f. A(x) satisfies P(x,A) = 0" and returns the MINIMAL
  POLYNOMIAL rather than a solved branch -- more robust, and what `algfield.Field` wants.
  Solving a cubic for radicals defeats the series check used to pick a branch. 12 entries
  in the corpus give their g.f. this way; 3 fell.
- **`makeslots` now accepts `minpoly`**, so a degree-5 algebraic g.f. with no radical form
  (A392976) is provable at all.
- **`xreftex.py`**: a closed form the entry gives only as "a(n) = 2*A378933(n)" needs the
  referenced entry's own formula substituted, and the paper must say so rather than
  presenting a formula the entry does not carry.
- `gfclean` now colonises "G.f. <expr>" and "G.f. (for offset 1): <expr>" (7 entries);
  `cfparse` strips a trailing semicolon (A034267 was blocked by one character);
  `makeparity` and `makehyper` use `coeffs_of` instead of `parse_conj`.

**Where a comment can go:** every OEIS entry has Comments and Formula fields, so a proof
can always be recorded on the entry itself. arXiv is not required -- entries carry inline
proofs (A002538, A126674) and entry-hosted PDFs (A087726 at /A087726/a087726_4.pdf).


### 31 Aug 2026: the periodicity-mod-k conjectures are NOT the periodicity theorem

Eighty open entries were found conjecturing something about a(n) mod k being eventually
periodic, forty-two of them Peter Bala's -- apparently a large, human-posed pool for the
theorem already used in papers 32-51. It is not. Two separate readings were wrong, and both
are worth keeping.

- **16 of the 80 are compound.** A377109-A377119 read "every prime divides a(n) for
  infinitely many n, and ... the difference sequence of K(p) is eventually periodic". The
  periodicity half follows from a finite-state argument, but only if 0 occurs in the cycle,
  and THAT is the first half -- which is a genuine and hard claim about prime divisors of a
  linear recurrence, not a corollary of anything here. Matching "eventually periodic" inside
  a compound statement found the wrong clause.
- **The 33 pure ones claim more than periodicity.** Bala writes "eventually periodic with
  the period **dividing phi(k)**", and elsewhere "purely periodic with period p - 1". The
  finite-state argument gives a period bounded by k^r and says nothing about phi(k). The
  sharp form is a number-theoretic statement of Fermat-Euler type, out of reach here.
- **Their e.g.f.s are not of the required form either.** The theorem needs
  A(x) = G(e^x - 1) with G an INTEGER power series. A000436 has cos(x)/cos(3*x), A012780
  arcsin(tan(x)), A122399 Sum_{n>=0} (exp(n*x) - 1)^n. A005046's exp(cosh(x) - 1) does
  become a function of u = e^x - 1, namely exp(u^2/(2(1+u))), but its coefficients are not
  integers, so the truncation-mod-k step fails.

`cfperiod.py` was built and is correct -- for a sequence with an integer constant-coefficient
recurrence and leading coefficient 1, the state vector mod k evolves by a companion matrix
over a finite ring, so the orbit is eventually periodic with pre-period and period at most
k^r, and purely periodic when the trailing coefficient is invertible mod k. Ten entries have
such a recurrence stated as fact. **All ten are the compound prime-divisor conjecture, so
none is settled.** The engine is kept for when a plain periodicity conjecture turns up.

**Bala's conjectures are hard because he is a careful mathematician posing sharp
statements.** That is the same lesson as the poser census: the conjectures that would carry
the most credit are the ones least likely to fall to this machinery.

**12 entries in the universal sweep exceed 8 minutes each** and are still undecided --
large algebraic fields where the residual computation is the bottleneck. Listed in
`uni_todo2.json`. They need a faster field implementation, not a new idea.


### 31 Aug 2026: the full accounting, and four nulls in a row

**The corpus, by shape.** 42,697 conjecture statements across 30,793 entries; 38,913 still
open.

| shape | total | still open | worked? |
|---|---|---|---|
| recurrence | 14,707 | 14,287 | yes, systematically |
| prose / other | 7,501 | 6,586 | out of reach by kind |
| inequality / positivity | 6,750 | 5,440 | no engine |
| generating function | 6,669 | 6,420 | tried as targets -- see below |
| closed form a(n)= | 4,011 | 3,691 | partly |
| congruence / divisibility | 1,742 | 1,439 | partly |
| primality | 695 | 529 | no engine |
| asymptotic / limit | 419 | 365 | no engine |
| triangle T(n,k) | 106 | 96 | no |
| sum / product identity | 97 | 60 | partly |

**The residue is now 255 entries** (from 304), after the parsers added today. What is left:
88 name another entry, 64 an unread Sum_, 36 asymptotics, 21 binomial/factorial, 10 g.f.
The wall everywhere else is unchanged: **10,404 entries have only a prose NAME** and 520
have fact lines that are pure prose.

**Four veins measured and closed:**

- **Conjectured generating functions AS TARGETS.** 6,581 entries have one and no paper, but
  6,292 state nothing as fact. Of the 52 that do, **43 turn out to say "holds at least up to
  n = 1000 but is not known to hold in general"** -- correctly refused, since that is not a
  fact. **0 proved.** (`gftarget.py`. The logic is sound and kept: if L is a fact that
  determines the sequence, and the conjectured g.f.'s coefficients satisfy L and match the
  initial terms, the g.f. is proved.)
- **Inhomogeneous recurrences as the known side.** `inhom.py` reads
  "a(n) = n*(a(n-1) - 1) + 2" and homogenises by applying (N-1)^(m+1). **Exactly 1 entry**
  in the whole open pool, and its line carries a prose caveat. Dead.
- **a(n) = g(n) + c(n)*Sum_k F(n,k).** `sumform.py` reads the 22 residue lines where the sum
  is not the whole right-hand side, and `sumform_run.py` moves the telescoped operator from
  S to a by S = (a-g)/c. 9 candidates, **0 proved** -- 4 timed out, and the rest failed at
  the telescoper, the boundary correction, or the division. The construction is right; the
  pool is too small and too awkward.
- **Combinatorial-counting families.** 7,813 open conjectures sit on entries named "Number
  of n X k arrays", "Number of strings over Z_m", "Number of walks/tilings/permutations
  avoiding ...". These ARE transfer-matrix provable in principle, and that is the largest
  untouched pool in the corpus -- but the automation barrier is building the transfer matrix
  from a prose definition, which is not reliable at scale. The one fully mechanical
  subfamily, strings over Z_m with trace and subtrace conditions (state = running sum and
  running subtrace), has **only 10 members.**

**The honest shape of what remains:** the reliable source all along has been parser gaps,
not new mathematics, and the parsers now read everything in the corpus that is written as
mathematics. What is left is written as prose.


### 31 Aug 2026: conjectured CLOSED FORMS as targets, and a second settlement-wording gap

**`cftarget.py`: prove a conjectured closed form from a recurrence or g.f. stated as fact.**
The mirror of every other sweep: if L is a fact that determines the sequence and the
conjectured closed form c(n) satisfies L and matches the initial terms, then c(n) = a(n).
2,207 entries carry such a conjecture and have no paper -- **2,146 state nothing as fact**,
leaving 8. Adding a g.f. route (read the recurrence off the stated generating function with
`holo.annihilator`, converting the exponential case by multiplying through by (n+r)! and
re-indexing to backward form) took it from 1 hit to 4.

**Two of the four were already settled, and the filter missed both.**

- **A208658** -- "The above conjectures are true." (Stefano Spezia, Nov 19 2023)
- **A235089** -- "In particular, Barker's conjectures are true (see Fried link)."
  (Sela Fried, May 08 2026)

`SETTLED` matched "is true" but not "**are** true". Widened to
`(is|are|was|were)\s+(true|correct|proved|proven|verified|established|known)`, and the
whole roster re-audited: **A166761 -- a paper built earlier the same day -- also falls.**
Andrew Howroyd, Dec 12 2024: "The above empirical formulas are correct." The line used as
the known side, `a(n) = 2*A378933(n)`, sits in the SAME comment block as that settlement.
Withdrawn.

Roster **610 -> 611**: minus A166761, plus A208545 and A227161.

**This is the second settlement-wording gap in two days** (the first was "follows *easily*
from"). Both were single words. The lesson is not to widen once more and stop, but that a
settlement can be phrased any way a person likes -- so the wide net stays, false positives
are read rather than trusted, and every candidate is checked against the live entry before a
paper is built.

**A process failure worth recording:** `python rank.py | head -2 && rm -rf papers && mv ...`
continued past a crash, because `head` exits 0 even when the command feeding it dies. That
replaced papers/ with a partial ranking. Any chain that destroys a directory must test the
result explicitly, not rely on the exit status of a pipeline.

**Two more veins closed:** inheriting a known side across a stated identity between entries
(27,136 such lines corpus-wide, but only 4 sit on an open entry with no paper, and 1 could
inherit) and, from the previous pass, conjectured g.f.s as targets.


### 31 Aug 2026: the b-files were never opened, and the first real disproof from them

**Every check in this project ran against the DATA field -- about forty terms.** The OEIS
also publishes b-files with hundreds or thousands, and the local clone carries 242,201 of
them. They were never opened. (They are Git LFS pointers, since the clone skipped LFS, but
the pointer names the true size, which is enough to order a fetch queue; `bfile.py` fetches
and caches from oeis.org.)

`bsweep.py` tests every open conjectured recurrence against its full b-file. 10,632 entries
are queued, largest b-file first.

**Two false alarms before the first true result, both mine:**

- The first slice reported **362 disproofs out of 2,233** -- a 16% rate, which is not
  credible. Every one was false: the conjectures say "for n > 5", "for n > 13", and the
  test started at n = order. A conjecture is not disproved at an index it never claimed.
- With that fixed, **11 remained, all failing at n = 2..9**. Also false. Mathar's
  polynomial-coefficient recurrences are asserted for LARGE n -- the residual criterion
  says the same, "for all n > deg B" -- so a failure at a small index is the boundary, not
  a counterexample. The test now requires the LAST failure to lie in the upper half of the
  tested range.
- After both fixes: **1 disproof in 2,395 checked**, which is a believable rate.

**A076217 is disproved, and properly.** Colin Barker's "a(n) = -a(n-1)+a(n-2)+a(n-3) for
n>5" fails at n = 3^k, 3^k+1, 3^k+2 for every k >= 2 -- infinitely many indices. The entry
already remarks that it "seems to fail at n = powers of 3", so the counterexamples are
known; **a paper exhibiting one would have been padding.** What is new is the proof that it
fails always, and it is elementary:

- `a(n) = 1` exactly when `n = 3^k - 2`, by induction straight from the entry's defining
  recursion `a(n) = a(n-1) + n*sign(n - a(n-1))`.
- From `a(p-2) = 1` with `p = 3^k` the next values are forced:
  `a(p+1+2i) = 2p+1+i` and `a(p+2+2i) = p-1-i` for `0 <= i <= p-2`. Taking `i = p-2` lands
  on `3p-2 = 3^(k+1)-2` with value 1, which closes the induction.
- Then `-a(p-1)+a(p-2)+a(p-3) = -p+1+(p-1) = 0` while `a(p) = p`; similarly the recurrence
  returns 1 and -1 at `p+1` and `p+2` against `2p+1` and `p-1`.

Verified to n = 60000 against the definition, the DATA field and the 10000-term b-file, all
in exact integer arithmetic. Roster **611 -> 612**; the disproof ranks 55th.

**The lesson for the disproof engine:** a disproof needs a failure the conjecture actually
claims, at an index it actually reaches. Two guards enforce that now, and both were learned
the hard way in a single sitting.


### 31 Aug 2026: I got this IP blocked by the OEIS. Recording it so it is not repeated.

To speed the b-file sweep I wrote a fetcher with four workers and pointed it at oeis.org.
It issued roughly **8,800 requests in about seven minutes**, and the service blocked the
address, returning this in place of every b-file:

> Your IP address has been temporarily blocked due to excessive usage. If you need to crawl
> the OEIS regularly, please consider using the Git repository at
> https://github.com/oeis/oeisdata.

That is a fair complaint and the fault was mine. Two things made it worse than it needed to
be: the blocked response was **cached as though it were data** (8,672 files), because the
"is this a page rather than a b-file" test looked for `<html>` and the block message is
plain text; and the same weak test had already cached 8,802 redirect stubs earlier, because
`curl` was called without `-L` and large b-files are served by a redirect to S3.

Fixed:

- `curl -sSL`, so redirects are followed.
- `_looks_like_bfile` accepts only a file whose first character is `#`, `-` or a digit.
  Anything else is deleted, never cached.
- **`bfile.fetch` is now sequential and rate-limited to one request every 1.2 seconds**, and
  the parallel fetcher is deleted. The remaining 8,672 b-files will take about three hours
  of slices, spread over as many sessions as it takes.

**The route the OEIS recommends is not open here.** The b-files in the local clone are Git
LFS pointers; `git lfs pull` fails because the git proxy will not serve LFS objects for a
repository outside this session's authorized set, and `add_repo` refuses `oeis/oeisdata`
because the session already holds repositories from a different owner. So oeis.org is the
only route, which makes the rate limit the whole of the answer.

**The general rule: a scraper that is fast enough to be noticed is too fast.** Any bulk
fetch from a public service gets one request at a time and a deliberate pause, and its
"did I get real data" test is written to accept only what real data looks like, never to
guess at what an error looks like.


### 31 Aug 2026: conjectured closed forms and g.f.s were never tested for being WRONG

Every disproof check here looked at conjectured RECURRENCES. A conjectured closed form or
generating function was only ever an input to be proved from, never something to refute --
and the DATA field alone refutes one, no downloads needed. `datacheck.py` sweeps the **7,557
open entries** carrying such a conjecture.

**The first run reported 103 disproofs. All 103 were false, and so were the next 96.** Five
separate faults, each found by reading the candidates rather than trusting the count:

1. **Qualifiers.** "a(n) = 2^(n+1) - 1 for n>2 **and odd**", "a(n) = -1 for n = 31 and all
   n >= 33". A conjecture that restricts WHICH n it speaks about must not be tested at the
   indices it excludes. `QUALIFIED` now refuses odd/even/except/prime/if-n/when-n and the
   rest.
2. **Index conventions.** A generating function is often written so that $[x^k]$ is
   $a(k+1)$ -- A071283's is $a(k-4)$. Every g.f. in the sweep looked false until the check
   searched shifts, and the shift search must run over the WHOLE claimed range, not a
   six-term window, and reach at least +-8.
3. **The shift search started at the first term** rather than at the index the claim starts
   from, so a formula asserted "for n >= 10" was judged on terms 0..5.
4. **Truncated lines.** A071283/5/7 and A283644 store a generating function cut off inside
   its numerator. Half a polynomial is not a counterexample.
5. **Floor written as `[...]`**, which the parser reads as something else (A051756).

After all five: **8 candidates, of which 1 is a real disproof.**

**A141135 is disproved.** Colin Barker's generating function
`x(5+4x+4x^2-x^3-x^5+x^8-x^9)/((1-x)^2(1+x+x^2))` reproduces a(1..23) and then gives
91, 102, 113 where the entry publishes 90, 101, 112 -- failing at n = 24, 27, 30, a step of
three, the period of the factor `1+x+x^2`. His companion recurrence
`a(n) = a(n-1)+a(n-3)-a(n-4) for n>10` fails at n = 24 and 25. The two are the same
assertion, since that denominator is the recurrence's characteristic polynomial. Roster
**612 -> 613**.

The paper argues explicitly why this refutes the conjecture and not the data: the terms are
minima over finite sets of pentagon configurations, computed and published, while the g.f.
has 15 free coefficients and 23 terms to fit -- breaking at the 24th is what fitting does.

**Not counted, and why:**

- **A283644** -- Barker's g.f. AND his recurrence both fail from the very first terms. That
  is an entry inconsistency (the data was very likely corrected after he posted in 2017),
  not a mathematical result. Worth sending to OEIS as a correction; not a paper.
- **A286772** -- the block holds "a(n) = 1 for n>2" and "a(n) = 2^(n+1) - 2 for n>2", which
  contradict each other and are plainly Barker's usual odd/even pair with the qualifier lost
  in transcription. Not a disproof.
- **A297741, A071283/5/7, A051756** -- all index conventions or truncation, per the list
  above.



## 3b. SESSION OF 31 AUG 2026 — what was withdrawn, what was added, what is dead

**Four disproofs withdrawn (A098660, A103769, A119967, A129366).** Each refuted a
conjectured recurrence that fails at *every* index. That is the signature of a
transcription defect, not a false conjecture: Mathar's recurrences are fitted to the data,
so one that never holds was never what he computed. Fitting the true recurrence of the
same order and degree from the published terms makes it explicit — the difference is only
dropped integer factors (A098660 loses 4, 8, 32; A103769 loses a 4 on the leading term;
A119967 loses 4, 2, 4, 3). **Rule: a data-fitted conjecture that fails at every index is a
typo. A real disproof fails at a few indices after holding at many.**

**Twenty papers withdrawn as duplicates.** Papers were built for Bala's φ(k) periodicity
conjecture on twenty entries that already had papers 31–50 for the same conjecture. The
openness check confirmed the OEIS entries were unsettled but never asked whether the
roster already held a paper. **Rule: before building anything, test the A-number against
`rank-map.json`.** Entry openness and roster novelty are two different questions and both
have to be asked.

**Four papers added**, all on entries that had no paper at all:
- A079144, A158690 — Bala's φ(k) periodicity, same theorem as papers 31–50; these two
  entries were simply missed by the earlier sweep.
- A079144, A158690 — Bala's *second*, distinct conjecture on each entry: the Gauss
  congruences `a_i(n p^r) = a_i(n p^(r-1)) mod p^r` for **every shift** `a_i(n)=a(n+i)`.
  New theorem, same setup: the operator `D = (1+t) d/dt` maps `Z[[t]]` to itself, so every
  shift stays in the `G(e^x-1)` family; then `a_i(n) = sum_m d_m m^n mod p^r` and the
  elementary `x^(p^r) = x^(p^(r-1)) mod p^r` finishes it. Verified on 932 instances each.

**Nulls measured this session, do not redo:**
- *Residual-not-polynomial as a disproof route.* Fourteen entries ever flagged. Nine had
  papers, four were the typo class above, and the remaining five (A026270, A026377,
  A026672, A202020, A279013) are non-results: three are index-convention mismatches that
  hold once the convention matching the data is used, two quote conjectures with visible
  typos in the entry (`a(n-4)` twice; `2*n7`). **Route exhausted.**
- *The two large data sweeps.* `datacheck_results.json` (7,557 entries) and
  `bsweep_results.json` (3,376) contain exactly 9 DISPROVED verdicts between them. Two are
  genuine and already papered (A141135, A076217). The other seven are transcription
  defects: A071281/83/85/87 carry a spurious outer `x^3` in the g.f. numerator while their
  recurrences hold on all data; A283644's entire Barker block is a copy-paste of
  A283586's; A286772 lost the words "even" and "odd" from two parity formulas; A297741's
  closed form is off by one in the index. **Both sweeps are finished and yielded 2.**
- *The trigonometric φ(k) family.* A000436, A000464, A000182, A002439, A208679, A208681,
  A012780 tested exactly to 110 terms, k ≤ 60. Only A000364 fails (k = 27 and 54), which
  is already paper 28. No new disproof. Note A000464 claims *purely* periodic and does not
  fail — so the pure/eventual distinction is not automatically an error.
- *Gauss congruences beyond those two.* 158 entries mention them; 56 state one as a
  conjecture; of those, exactly one open entry has an integral `G`, and it is A158690.

**Where the φ(k) theorem stops.** It needs `G` integral. A179929 (`G` has denominators
3^j) and A370092 (denominators 2^j) are outside it, and A370092 is the proof that the
hypothesis is necessary: its conjecture genuinely fails at k = 2, which is exactly why
Bala wrote "Let k > 2" there and nowhere else. Bell numbers are the same story — `c_j =
1/j!`, and their period mod p is (p^p-1)/(p-1), which does not divide φ(p). For those two
entries the argument gives the conjecture only for k coprime to 3 resp. 2; that is not a
settled conjecture and is not counted.


**Three m-section identities settled (A084703, A155543, A111403).** The family
`a(n) = A######(m*n+k)` with `m >= 2` has 7 instances, 6 open. Three are decidable from
what the two entries already state as fact:
- A084703 = A089928(4n-2). Both entries post closed forms. The quadrisection turns
  `(1±sqrt2)^(4n)` into `(17±12sqrt2)^n` and the parity term is constantly -1. **Note:
  A089928's posted g.f. `1/((1+2x)(1-2x-x^2))` is wrong** — the denominator expands to
  `1-5x^2-2x^3`, whose reciprocal begins 1,0,5 while the entry begins 1,2,4; the factor
  should be `(1+x^2)`. The paper does not use that line and says so.
- A155543 = A090129(2n+2). A090129 is the order of 3 mod 2^n; the paper proves
  `ord = 2^(n-2)` for n >= 3 from scratch by 2-adic valuation rather than citing the
  entry's reference, so it stands alone.
- A111403 = A002716(2n) - 1. A002716's factual recurrence splits by parity; one induction
  gives `b(2n+1) = 2^(2^(n+1))+1` (the Fermat numbers) and `b(2n) = 2^(2^(n+1))-2^(2^n)+1`.

The remaining three of the seven are not reachable: A060011 (schizophrenic-number digits),
A352813 (a partition-optimisation quantity), A220547 (its own recurrence is only
empirical, so there is no factual known side).

**`xref` is finished, not "not yet swept" as this ledger used to say.** It was run; it
settled exactly one entry, A052183, which is already in the roster.


**A new engine: reduce a defining functional equation mod k (A393856-A393859).**
Paul D. Hanna defines many entries by a functional equation for the g.f. and then
conjectures a congruence on the terms. Those are fully decidable, and the method is
general:
1. Show the functional equation determines the coefficients one at a time (the coefficient
   of `a(N)` in the expansion is 1), so there is exactly one integer solution.
2. Reduction mod k is a ring homomorphism, so `a(n) mod k` obeys the same recursion over
   `Z/kZ`, which likewise has a unique solution.
3. Exhibit a RATIONAL series over `Z/kZ` satisfying the reduced equation. Uniqueness then
   forces the reduction to equal it, and reading off its coefficients is the conjecture.
Step 3 is an identity between rational functions -- finite, exact, no truncation.

For `A(x - x*A(m x)/m) = x` with the conjecture `a(n) = 1 (mod m+1)`: modulo `m+1` we have
`m = -1`, so `B = x - sum a(n) m^(n-1) x^(n+1)` collapses to `x/(1+x)`, and `x/(1-x)`
composed with `x/(1+x)` is `x` on the nose. Four entries (m = 4,5,6,7); the argument works
for every `m >= 2`. A195195 is the `m = 2` member but carries no congruence conjecture, so
it is not claimed.

**Where to take this engine next.** Hanna has many more functional-equation entries with
congruence conjectures, several with the same shape:
`A396102` (A(A(A(x))) = (1+x)A(A(x)), mod 3), `A396797`/`A396807`
(A(x) = x + A^p(x)*A^(p+1)(x), mod 2p), `A396793`/`A396794`/`A396795`,
`A396843`/`A396844`/`A396846`, `A397241`/`A397242`/`A397245`, `A381361`-`A381365`.
Untried; the same three steps apply whenever the equation is triangular in the
coefficients.

**Two families measured and dead.**
- *Second Lagrange form* `a(n) = [x^n] phi(x)^(n+1)/(n+1)`: 17 entries have that shape and
  essentially none carries a conjecture. Widening to all 351 entries defined by
  `a(n) = [x^n] ...` gives 49 with any conjecture and **zero** with a conjectured
  recurrence. What they do carry is supercongruences mod `p^(2r)` or `p^(3r)` and Kotesovec
  asymptotics -- both out of reach. The plain Gauss congruences for that family are already
  known and said so on the entries (see A333564). **Do not rebuild `diagonal.py` for this.**
- *`a(n) = r (mod m)` with a C-finite recurrence*: 844 entries mention a conjecture and a
  numeric modulus, 90 have no paper and a parseable claim, and **none** of the 90 has a
  factual constant-coefficient recurrence. They are partition, theta-function and
  number-theoretic sequences; the congruences are Ramanujan-style. The finite-state
  decision procedure has nothing to chew on here.

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
  - **Closed forms: attacked, and the class is far thinner than its headline number.**
    Of the ~1,100 lines matching `Conjecture: a(n) = ...`, only **34** are an elementary
    formula in `n` on an entry that also posts a `G.f.` The rest are sums, references to
    other A-numbers, integrals, `floor`/`mod`, or congruences dressed as formulas. Of
    those 34, **8** close. Papers 306–313.
  - **Conjectured generating functions: 121 entries, and only 3** also post an
    independent recurrence to check them against. Effectively a dead class for a
    mechanical method — there is nothing to prove the g.f. *from*.

  **A NEW ENGINE REOPENED PART OF THIS — see `logexp.py`.** The claim below that
  transcendental generating functions are unreachable was WRONG, and wrong for two
  reasons worth remembering.

  1. **`exp` and `log` generate a differential module, not just a field.** Monomials
     `log(u)^a * exp(g)^k` span a finitely generated `Q(x)`-module closed under `d/dx`:
     the exponential part never mixes monomials, and the log part only ever moves
     *downwards*, so every computation terminates. The residual test transfers verbatim —
     `B` is a polynomial iff every coefficient outside the constant monomial vanishes.
     This is the same idea as `quadfield`/`multiquad` with different atoms, and it is the
     right way to think about the whole family: **pick atoms closed under `D`, then test.**
     Coefficients may themselves carry a `sqrt` and it stays sound, because the final
     polynomiality test is strict — it can lose a proof, never invent one.
  2. **A parser bug had been hiding the class the whole time.** The implicit-multiplication
     rule "an `x` or `t` followed by a letter" was shredding every function name
     containing one: `exp` -> `ex*p`. So *no `exp` anywhere in OEIS had ever parsed*, in
     any class. Function names are now masked before that rule runs. **When a whole class
     looks empty, suspect the parser before concluding the mathematics is out of reach.**

  Result: papers 320–328, nine recurrences with transcendental e.g.f.s. Running the same
  engine over the 859 o.g.f. entries found nothing further — those are algebraic.

  **THE MECHANICAL SEAMS ARE EXHAUSTED. Read this before spending a session re-mining.**
  Every route below was taken to the end against the full local clone:
  - recurrence + posted `G.f.` — 525 candidates, mined
  - recurrence + `E.g.f.` only — 65 candidates, 8 close; the rest are transcendental
    (`exp`, `log`, `cosh`) and no algebraic method reaches them
  - recurrence + g.f. stated in the NAME (`Expansion of ...`) — 73 found, +6
  - recurrence + an explicit `a(n)=` formula to derive the g.f. from — 175 entries,
    **0 usable**: none of those formulas is an elementary combination of `n^k r^n`
  - recurrence with no formula at all — 323 entries, out of reach
  - gcd-sum conjectures — **5 exist in the whole database**, 3 proved (29–31), 1 already
    settled by Radcliffe, 1 (A373561) is a quadruple sum needing a counting argument
  - `phi(k)` periodicity — **39 exist**, all examined
  - closed forms — 34 usable, 8 close
  What remains of the 15,585 is inequalities (~2,800), "for all n" claims (~1,500),
  limits and asymptotics (~400), sum identities (~270), congruences, primality,
  permutation and finiteness statements. **None of these yields to exact algebra over
  Q(x); they need actual mathematical ideas, one at a time.** The next real gain would
  come from a different engine — creative telescoping for the sum identities, or a
  holonomic ODE solver for the transcendental generating functions — not from more
  sweeping.
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

### 26 Aug 2026: the ceiling above was wrong, and six things moved it

The "~330 papers" ceiling assumed the attackable set was the 555 entries posting a `G.f.`
line and that the field had to be a sum of independent square roots. Both were parser and
engine limits, not facts about OEIS.

1. **`algfield.py` — any algebraic generating function, not just square roots.**
   Work in `K = Q(x)[y]/(P(x,y))` for the minimal polynomial `P`. Differentiating
   `P(x,α)=0` gives `α' = −P_x/P_y`, the quotient taken inside `K` (`P_y` is invertible
   because `P` is squarefree; use the extended Euclidean algorithm in `Q(x)[y]`). `θ` then
   stays exact and the residual test is unchanged. `sympy.minimal_polynomial(expr, y,
   domain=QQ.frac_field(x))` builds `P` straight from the posted expression. **This reaches
   nested radicals** — the exact class that silently mis-reduced under `multiquad` and cost
   papers 170 and 191.
2. **The label is not always `Conjecture:`.** 149 entries write
   `Conjecture D-finite with recurrence …`. Strip the preamble.
3. **The right-hand side is not always `0`.** Several hundred are written
   `a(n) = <recurrence>`, sometimes chained `a(n) = <recurrence> = <closed form>` —
   which asserts BOTH halves. Prove both or drop it (`eqform_extract.py`).
4. **The generating function is not always on a `G.f.` line.** 70 entries whose NAME is
   `Expansion of <expr>` carry a recurrence conjecture and no `G.f.` line; there the
   expression is the *definition*, the strongest possible ground. 36 of 73 close
   (`nogf_scan.py`). A further 15 entries state it mid-sentence — *"Expansion of
   (1+x*C^3)*C^4, where C = …"*, *"Theorem: G.f. = …"* — see `midline_scan.py`.
5. **A whole class is not recurrences at all.** `a(n) = c1*A111111(n+k1) +
   c2*A222222(n+k2) + <polynomial in n>` is one identity between generating functions
   when every entry involved posts one (`cross.py`). Test for a POLYNOMIAL difference,
   not zero.
6. **Series reversions are algebraic.** `f(R) = x` defines `R`; eliminate it from
   `y − E(x,R)` and `f(R) − x` by a resultant and hand the factor with the right
   expansion to `algfield` (`reversion.py`).

7. **The generating function is sometimes only in the entry's NAME as a relation.**
   `a(n) = A000522(n) + 1` fixes it completely (a constant `c` contributes `c*e^x` to an
   exponential generating function). Only two such entries exist and one was already
   confirmed, so this is a one-paper vein -- but the same reading applies wherever a name
   states a plain arithmetic relation (`namerel.py`).

8. **A conjecture can factor through a recurrence the entry already states.** Fifty
   entries carry a conjectured recurrence beside one contributed as plain fact
   ("Recurrence: ..."). Read both as operators in the Ore algebra `Q(n)[N]`, `N f(n) =
   f(n+1)`, where moving `N` past a coefficient shifts it. If the conjectured operator
   `C` factors as `C = Q P` over the stated one, then `C(a) = Q(P(a)) = Q(0) = 0` and the
   conjecture follows -- **with no generating function anywhere in the argument**
   (`ore.py`). Right division is ordinary polynomial division with the twisted product,
   so a zero remainder is exact. Nineteen papers.
   Three things to get right: expand `Q P` back and cancel it against `C` rather than
   trusting the division; verify the *stated* recurrence on the published terms, since
   the whole argument leans on it; and compute the integer poles of `Q`'s coefficients,
   refusing any case where one lands inside the claimed range. Refuse `deg Q = 0` too --
   there the two recurrences are the same one rescaled and there is nothing to prove.
9. **A formula relating the entry to others supplies a generating function.**
   `a(n) = A002003(n) + n` fixes it once the other entry posts one (`relgf.py`); a
   polynomial term `p(n)` contributes `p(theta)[1/(1-x)]`, or `p(theta)[e^x]` in the
   exponential case. Three papers, from 34 candidates.

**Final coverage of the recurrence class:** 1,025 entries carry a `Conjecture ... = 0`
recurrence. 345 are unreachable by any of this: 232 have a purely combinatorial name and
no formula anywhere on the entry, and 113 name a table diagonal or column of another
entry, which gives no usable generating function. That is the real floor, not a parser
limit.

Three parser faults were costing results across every class: a trailing `(End)` or
`[From …]` marker made a g.f. line unparseable; a zero coefficient polynomial has degree
`−∞`, which crashed `apply_poly_theta`; and `to_quad`/`to_multi` substituted on
`sqrt(D)` **syntactically** while `D` had been normalised with `cancel`, so a radicand
written in factored form — `sqrt((x^2-3x+1)(x^2+x+1))` — produced a "decomposition"
whose `v` still held a square root. That last one could only ever lose results, never
invent them (`is_polynomial` ends with `out.is_polynomial(x)`), but it was silently
losing them for the whole run. **Both engines now match on the radicand and refuse
outright if any radical survives.**

**Re-running the whole sweep under fixed code is worth it on its own.** It re-derives
every earlier result independently and flags any that no longer reproduce — that is how
A185020 was caught, and how the `to_quad` bug surfaced (the algebraic engine and the
quadratic one disagreed on A166287; a direct series computation showed the algebraic one
was right).

### Two classes that are dead, and why

- **`wz.py` — Gosper certificates for hypergeometric sums. 284 attempts, 0 proofs.**
  For `a(n) = Sum_k F(n,k)`, form `T(k) = Σ_i p_i(n) F(n−i,k)` and run Gosper directly
  rather than searching with Zeilberger; verify the certificate instead of trusting it.
  **The trap:** the range usually depends on `n` (`Sum_{k=0..n}`), so the operator applied
  to `a(n)` mixes ranges and is not `Σ_k T(k)` unless `F(m,k)` vanishes outside it. With
  `binomial(n,k)` it does; with `binomial(2k+1,k+1)` it does not, and there `T ≡ 0` while
  nothing is proved (A054109 produced exactly that false positive here). Check the
  boundary before the certificate. 214 of the 284 were not single hypergeometric terms
  and 39 more failed the boundary — the class is genuinely dead by this route.
- **The formalisation benchmarks are not a source of targets.** Checked the whole roster
  against **OEIS Open** (492 conjectures, 444 sequences, `epoch-research/LeanOpenProblems`)
  and DeepMind's **formal-conjectures** (299 sequences). Only six papers touch either
  list, all among the original 28, and only A129365 Conjecture D is actually resolved
  (paper 20, withdrawn). Of the 492, **160 were resolved and 332 were not** — but the 332
  are Sun-type existence and number-theory statements (*"every integer n>8 can be written
  as x+y+z with …"*), with nine recurrence-shaped and none of those P-recursive. Nothing
  there for these engines.

- **Differential equations for the g.f. are a dead end, because they are the settlement.**
  Eleven entries pair a recurrence conjecture with a non-conjectural ODE. Nine already say
  the conjecture follows from it, and the last two say so in wording the detector had to
  be widened to catch. Zero results.

### The one genuinely hard target attacked, and why it did not fall

**A193437.** `a(n)` counts permutations of `n` elements whose cycle lengths are all
`== 1 (mod 3)`; e.g.f. `exp(Sum_{k>=0} x^(3k+1)/(3k+1))`, and the entry gives a
non-conjectural recurrence `a(n) = a(n-1) + (n-1)(n-2)(n-3)a(n-3)`. Two conjectures, open
since 2011: `7^floor(n/7) | a(n)`, and more generally `p^floor(n/p) | a(n)` for every
prime `p == 1 (mod 3)`. This is not an oversight by the contributor — it is a real
divisibility problem.

What was established here, for whoever picks it up:

- **It holds to n = 399 for p = 7, 13, 19, 31, 37**, computed from the entry's own
  recurrence (which was checked against the published terms first).
- **The bound is tight.** `v_p(a(n))` equals `floor(n/p)` exactly at many indices -- 149
  of the first 300 for `p = 13`. So no crude estimate can work; a proof has to be exact.
- **Naive induction on the recurrence is not enough.** When `p | n`, both terms on the
  right have valuation exactly `floor(n/p) - 1` and must cancel to gain the last power,
  so the induction needs an auxiliary congruence, not just the bound.
- **`a(n)/p^floor(n/p)` mod p has no visible periodicity** in `n` at period `p`, `3p` or
  `p^2`, so that auxiliary invariant is not going to be a simple periodic one.
- **The structural fact worth starting from.** Since `p == 1 (mod 3)`, the allowed cycle
  lengths divisible by `p` are exactly `p` times the allowed lengths, so the exponent
  series splits as `G(x) = A(x) + G(x^p)/p` with `A` p-integral. That is an Artin-Hasse
  shaped decomposition, and `v_p(a(n)) = v_p(n!) + v_p([x^n]exp G)` is where the two
  contributions have to be balanced against each other.

Not proved. Recorded rather than counted.


### 30 Aug 2026: entries that post no generating function at all

`diagonal.py`. A family of entries defines the sequence only by an instruction,
`a(n) = [x^n] f(x) g(x)^n`, with no g.f. anywhere on the page. Every engine here skipped
them for want of something to test. They are diagonals, and the generating function is
algebraic and computable: reading the extraction as a contour integral and summing the
geometric series leaves one pole inside the circle, the Lagrange branch `x = t g(x)`,
whence `A(t) = f(x(t))/(1 - t g'(x(t)))`. Eliminating `x` by a resultant gives the
minimal polynomial, which `algfield.py` then takes.

Two bugs in it are worth remembering because both were silent.

- Solving the resultant for a closed-form root works only up to degree four. Above that
  `sp.solve` returns nothing and the entry was dropped with no error. Fixed by
  identifying the branch through *which irreducible factor the series satisfies*, which
  needs no root at all.
- Composing a power series into a rational function by substitution and `expand` does not
  terminate on anything but polynomials. It surfaced as "no branch reproduces the terms",
  which reads like a mathematical verdict and was a timeout. Rewritten on truncated
  coefficient lists; the yield went from 9 to 18.

And one in the *checker*, which is the more instructive: the independent second series
computation read `[x^i]` off a rational function with `.coeff(x, i)`, which returns the
numerator's coefficient and keeps the denominator. It rejected six of seven papers as
"the two series computations disagree". On A156894 it returned `1/(x-1)^4` where the
answer is 19. **The engine was right and the check was wrong** — the same shape of error
as the A156894 yardstick below, twice on one entry.


### 30 Aug 2026: a census first, then three engines aimed at what it found

Rather than guess where the remaining work was, every entry carrying an open conjectured
recurrence was classified by what it gives you to work with. **654 remain** after removing
the ones already held. The piles:

| count | what the entry offers |
|---|---|
| 290 | a g.f. is posted, and the engines failed on it |
| 268 | nothing any engine could read |
| 44 | a sum with binomials or factorials |
| 28 | another recurrence posted |
| 19 | a sum without binomials |
| 5 | an e.g.f. |

Then the 290 were diagnosed one by one for *why* they failed, which is the step that
turned the census into work:

| count | cause |
|---|---|
| 109 | the g.f. line does not parse |
| 77 | no g.f. line after all |
| 26 | transcendental or an infinite sum |
| 24 | should have worked -- all 24 turned out to be already settled |
| 20 | parses but does not match the published terms |
| 10 | a continued fraction |
| 13 | the residual test crashed |

**Most of what looked like hard mathematics was notation.** Of the g.f. lines that would
not parse, the commonest defeat was an old-style attribution with no underscores
(`- Maksym Voznyy (voznyy(AT)mail.ru), Aug 11 2009`), an editorial note
(`- amended by _Georg Fischer_`), or a second English sentence. The same held for the
summation formulas: three quarters of the telescoping failures were the parser refusing an
index called `i`, a range written `k>=0`, or a trailing `for n>0, with a(0)=1`.

Both parsers were rewritten to **offer candidate readings and keep whichever reproduces
the entry's own terms**, rather than to cut in the right place by regex. A bad cut is then
rejected by the data instead of trusted, so a permissive parser adds candidates without
adding risk.

`parse_conj` was also reading only some of the labels OEIS uses. It missed
`Conjectured to be D-finite with recurrence`, `Conjectural D-finite`, `Conjecture : ` with
a space, and one entry with a stray letter typed into the label. That had been silently
skipping conjectures in **every** sweep since the beginning. A conjecture that restates the
offset (`Conjecture: (with offset 0 instead of 1) ...`) is now refused outright rather than
parsed against the wrong indexing.

### The alignment trap, and a near miss

`A005560` posts `a(n) = C(n+3, ceiling(n/2))*C(n+2, floor(n/2)) - ...` and has offset 2.
The formula's value at `n` is the entry's `a(n+2)`. Testing it as written rejects a
perfectly good formula; **using it as written would prove something about a different
sequence**. The closed-form engines now search for the alignment and fix it from the data,
and the paper says which shift was used.

The first version of the parity engine reported the conjecture false on both halves. It was
not; the formula was simply unaligned. Same shape as the A156894 lesson below: check the
yardstick before believing the verdict.

### One refutation that was not one

`A000907`: the posted closed form is exact and matches the DATA, and Mathar's conjectured
recurrence fails on the entry's own terms at `n = 2`. It holds for the sequence shifted by
one. That is an off-by-one in how the conjecture is indexed, not a disproof, and claiming a
disproof from it would be wrong-headed. Recorded, not counted.

### Competition is closing these targets, by name

`Tong Niu` has eight papers on the OEIS from 2026, seven of them titled *"A short proof of
Mathar's YYYY recurrence conjecture for ..."*, naming the entry in the title. Five results
in the 30 Aug batch died on them (A001711, A002627, A032123, A045406, plus A214615 and
A176677 caught earlier). This is the same target list, being worked at the same time. The
practical consequence is that **the settlement scan has to be re-run against a fresh clone
before any delivery**, not once at the start.

### 31 Aug 2026: four conjectures are false, and here is what holds instead

The residual criterion is an **equivalence**, and it had been used in one direction only.
Writing `B(x) = Sum_i x^i (p_i(theta+i)A)(x)`, its coefficient of `x^n` IS the quantity
`Sum_i p_i(n)a(n-i)` that the conjecture claims vanishes. So `B` a polynomial of degree
`d` means the recurrence holds for `n > d` -- and `B` not a polynomial means the
conjecture fails for **infinitely many** `n`. A negative from the residual test is a
disproof, not a failure to find a proof.

Fifteen entries had a residual decided non-polynomial across the old runs. Reading them:

- **Three were indexing slips** (A026377, A026672, A080244): shifting the coefficient
  argument and the term indices together by the same amount makes the recurrence hold, so
  the conjecture is right and its stated indexing is off. Not disproofs, not counted.
- **Three had no g.f. reproducing every published term**, so nothing follows.
- **Four are genuinely false** -- A098660, A119967, A129366, A103769 -- surviving every
  shift between -5 and +5 in both arguments, with non-polynomiality decided exactly in the
  algebraic function field where the g.f. lives.

Each became a paper that does more than refute. The generating function is algebraic, so
differentiating its defining equation inside `Q(x)[y]/(P)` keeps `A, A', A''...` in a
finite-dimensional space over `Q(x)`; a linear dependence among them is an ODE, and
reading off the coefficient of each power of `x` turns the ODE into a recurrence
(`algode.py`). That recurrence is then **proved** by the same criterion that refuted the
conjectured one, so the paper carries a correction rather than only a negative.

A098660 is the clearest. Mathar's order-3 recurrence gives 28 rather than 0 at `n = 3`,
and the relation that does hold is

    (n^3-n)a(n) - (16n^3-48n^2+56n-24)a(n-2) + (64n^3-384n^2+704n-384)a(n-4) = 0,

which couples only indices of the same parity. The g.f. involves `sqrt(1-8x^2)`, so the
even and odd parts decouple and no three-term span across parities can work.

**Why this sat unnoticed for months.** The pipeline logged "residual not polynomial" as a
failure and moved on. It was never a failure. The lesson is narrower than "check your
assumptions": when a test is an *iff*, both answers are results, and a codebase that
records one of them as an error will hide every one of them.

**How each disproof is guarded**, because a wrong disproof costs far more than a missed
proof: the g.f. must reproduce *every* published term, not a sample; the failure must
survive every joint re-indexing; non-polynomiality is an exact decision in the field, not
a `simplify` that returned False; and A098660's counterexample was recomputed from the
entry's *other* posted formula, `a(n) = C(n,floor(n/2))*2^floor(n/2)`, with no generating
function involved at all.

### The ledger nearly destroyed itself, and how

`rebuild_table.py` found the end of the RESULTS HELD table with
`max(i for i, l in enumerate(lines) if re.match(r"^\| \d+ \| ", l))` -- the LAST line
anywhere in the file shaped like a table row. That was fine until the 30 Aug census
tables were added, whose rows have exactly that shape. The next rebuild replaced
everything between the roster table and the census with the new rows and deleted four
hundred lines of notes in one run.

It was caught only because the section headings disappeared from a `grep`. The fix is to
stop at the first line that is not a row, and the wider lesson is that a script which
rewrites the ledger is as dangerous as one that writes a paper: **the ledger is the state
that survives, so anything editing it needs the same care as anything claiming a result.**
Recovered from git; nothing was lost permanently.

### 31 Aug 2026, later: two soundness bugs in the field detectors

Both found by auditing what was already shipped, not by a failure.

**`to_quad` claimed membership in `Q(x)` for things that are not rational.** When an
expression contained no SQUARE root it returned `(expr, 0, 1)` -- "A is rational, with no
radical part" -- after checking only that no stray symbols were present. A fourth root, a
cube root, an exp or a log all reached that branch. The arithmetic that follows survives
it, because `theta(u) = x u'` holds for any differentiable `u`, so a proof obtained that
way can still be correct; what is wrong is the paper, which then asserts *"Since A lies in
a quadratic extension of Q(x)"* about a function that does not. `to_multi` had the same
hole. Both now require `is_rational_function(x)`.

**The detectors could not see half-integer powers other than +-1/2.** `D^(3/2)` is a
rational function times `sqrt(D)` and lies in exactly the same field, but matching only
`+-1/2` made

    z*(1+2z^2-z^3)/((1-3z+z^2)*(1+z+z^2))^(3/2)

look radical-free -- straight into the bug above. Rewriting the expression does not work:
sympy folds `b^(-2) * b^(-1/2)` back to `b^(-5/2)` immediately. The fix belongs where the
detector already substitutes a symbol for the root, so `D^(p/2)` becomes
`D^((p-1)/2) * s`.

**What the audit found.** Of 385 papers claiming a quadratic or multiquadratic field, 21
were flagged, then 18 after excluding the hand-written ones. The half-integer fix cleared
seven of those outright -- they were quadratic all along. Of the remainder, two were audit
artefacts (a timeout, and an entry whose g.f. is given implicitly), and **eight were real**:
A025754, A025756, A025757, A025758, A097180, A097188, A097189, A097192, whose generating
functions involve third, fourth, fifth and ninth roots. All eight are true theorems -- the
residual is a polynomial in the correct field too -- so all eight were rebuilt with the
algebraic-field template stating the actual minimal polynomial, and `algfield`'s degree
bound was raised from 6 to 10 to reach the ninth roots. Nothing was withdrawn.

**The audit itself had to be redone once.** Its first pass took the first g.f. line that
parsed, which is not always the one the paper used, and reported 21 mismatches on that
basis. Asking the right question -- *is there ANY posted g.f. that both matches the terms
and lies in the claimed field?* -- is what cut it to the real eight.

### The caret in every quoted conjecture

`tex_escape` mapped `^` to `\^{}`, the circumflex ACCENT. It renders as a caret on the
page, so nothing looked wrong, but in the PDF's text layer it is a control character:
copying a quoted recurrence out of any paper gave `16*n2-64*n` where `16*n^2-64*n` was
meant. Now `\textasciicircum{}`, which extracts correctly. Papers built before this keep
the defect until they are next rebuilt; it is cosmetic on the page and only bites a reader
who copies.

### 31 Aug 2026: a census of what the encyclopedia actually contains

Everything here had attacked one shape of conjecture. Classifying every line beginning
"Conjecture" across all 398,648 entries says how narrow that was:

| lines | open | shape |
|---|---|---|
| 8,316 | 7,959 | prose, or several statements in one comment |
| 1,418 | 1,331 | about primes |
| **1,070** | **1,055** | **linear recurrence, `... = 0` — the only shape worked so far** |
| 830 | 761 | congruence |
| 687 | 660 | an identity with another sequence |
| 622 | 593 | existence or finiteness |
| 597 | 586 | asymptotics or a limit |
| 594 | 575 | a closed form for a(n) |
| 579 | 555 | monotonicity or sign |
| 412 | 353 | a generating function |
| 262 | 247 | divisibility |
| 190 | 183 | linear recurrence, `a(n) = ...` |

**15,845 conjecture lines in total, and the work so far has been inside 7% of them.**

Three consequences, in order of how cheap they were.

**183 conjectures were the shape already handled, written the other way round.** Every
sweep selected lines by `"a(n-" in line and "=0" in line`, so `Conjecture: a(n) = <earlier
terms>` was never offered to any engine. 216 entries carry one in that spelling only.
`conjlines.py` reads both.

**`equate.py`, for conjectured closed forms and conjectured generating functions.** Both
reduce to one question: take what the entry states as FACT -- a posted generating function,
a posted closed form, or a stated recurrence -- derive a linear recurrence from it, check
the conjectured description satisfies the same recurrence, and match initial values. A
recurrence of order r with non-vanishing leading coefficient plus r consecutive values
determines a sequence, so agreement everywhere follows. Deriving the operator from a closed
form needed a construction that is easy to get wrong: the product of the first-order
operators `(N - rho_j)` does NOT annihilate a sum of terms, because applying the first
factor leaves the second term multiplied by `rho_2 - rho_1`, whose shift ratio is no longer
`rho_2`. The correct route is linear algebra over `Q(n)`, and the test that caught the
wrong version was checking the operator against the term's own values.

**Cross-entry identities are not the vein they looked like.** 660 open, and the engine
refuses 89% of them -- but this time reading the refusals showed they are refused
correctly: prose about primes, triangle references, sums over another sequence. Unlike the
summation formulas and the g.f. lines, the bottleneck here is not notation. Recorded as a
dead end rather than built out.

### Counting a pool you cannot touch is worse than not counting

The first candidate filter for `equate` reported **1214 entries**. The engine could use
almost none of them: `a(n) =` is a prefix of `a(n) ==`, so every congruence `a(n) == 2 (mod
n^3)` was counted as a closed form; floor formulas were counted; cross-entry identities
needing a second entry were counted. And `cfparse` accepted `denominator((n-2)^3/n^2)`
because sympify turns an unknown name into an undefined function whose only free symbol is
`n`, which passed the symbol check.

The engine then reported "the conjectured description does not satisfy the recurrence" for
28 conjectures it had never been able to read -- a status that reads like a mathematical
verdict and was not one. With the filter checking parseability and the presence of a usable
known side, the honest pool is **50 entries**, of which two became papers.

The lesson is not "tighten the regex". It is that **a failure status has to distinguish
"I decided against this" from "I could not read this"**, because the first is a result and
the second is a gap, and reporting the second in the language of the first hides the gap.

### 31 Aug 2026: 6,537 conjectures that no engine had ever seen

Sub-classifying the largest census bucket -- the 7,959 lines the first pass could only
call "other" -- found that **3,421 of them are headings**, not statements:

    Conjectures from _Someone_, date: (Start)
    a(n) = a(n-1) + a(n-6) - a(n-7) for n > 14.
    G.f.: (...)/(...).
    (End)

Every sweep in this project reads one line at a time and selects lines beginning with
"Conjecture". The lines inside such a block do not begin with that word. **6,537
conjectured statements sat inside 3,160 blocks, invisible to every engine since the
beginning** -- 2,451 recurrences, 2,396 generating functions, 1,392 closed forms.

That is a formatting blind spot, not a mathematical one, and it is the largest single
oversight found so far. `blocks.py` reads them.

### The circularity that cost 21 false proofs

A statement inside a conjecture block is a CONJECTURE, but it does not say so. Any code
deciding "does the entry state this as fact?" by looking for the word would take one as
established -- and an engine that derives a recurrence from one conjecture to prove
another has proved nothing.

That guard was written first, and it still failed. The last line of a block ends with
"(End)", which the reader strips when storing the statement; the exclusion test compared
the stripped text against the original lines, so it missed on exactly that line. The
engine then took a conjectured generating function as its own justification and reported
it proved. **21 results came out that way before the check caught it**, on a run whose
hit rate -- 21 of 24 -- was itself the thing that looked wrong.

All 21 discarded. The reader now carries the original line beside the cleaned statement,
and every known-side detector in the project (`equate_run`, `cong_run`, `ore_prove`)
subtracts the conjectured set.

**The honest pool after the fix is 27 entries, not 674.** Two became papers. That is the
second headline number this week to collapse on inspection, and the pattern is the same
both times: a filter that admits too much produces a large pool and a high hit rate, and
both are symptoms rather than results.

### What the blocks actually contain, and why most are out of reach

Reading them explains the low yield. Most are Colin Barker or Chai Wah Wu proposing a
linear recurrence fitted to the published data, on sequences with no known structure at
all -- A004484 is Sprague-Grundy values for Wyt Queens, A010910 is a Pisot sequence
defined by `a(n) = floor(a(n-1)^2/a(n-2) + 1/2)`. Whether Pisot sequences satisfy linear
recurrences is a hard open problem in its own right. There is nothing for an engine to
work from, and that is a fact about the conjectures rather than a gap in the tooling.

The tractable ones are those where the entry states something else as fact. A192382 posts
`a(n) = 4^n*(1 - (-1/2)^n)/3` and conjectures a generating function; A294139 posts
`a(n) = n*(4 - 21n + 12n^2 - 5n*(-1)^n)/16` and does the same. Both fall to the equate
engine.

### 1 Sep 2026: the word "Conjecture" was never the right search

A coverage audit -- what unproved statements exist that the word would never find --
changes the size of the problem:

| lines | marker |
|---|---|
| **23,322** | **"Empirical..."** |
| 15,435 | "Conjecture..." |
| 1,822 | "(It) appears that" |
| 851 | "Apparently" |
| 666 | "It seems" |

**"Empirical" is more common than "Conjecture", and this project had never read one.**
It is the OEIS's usual label for a formula found by fitting: 23,081 of the 23,322 sit in
%F. By shape: 10,935 linear recurrences, 3,929 generating functions, 1,569 closed forms --
all shapes the engines settle. 18,142 entries carry at least one.

So the true universe of unproved statements is around 42,000, and the recurrence subset
worked until now is 1,070 of them. **Two and a half percent.**

### Why that vein is nonetheless nearly dead

An empirical formula is a conjecture and cannot justify itself, so an entry is only
tractable if something else on it is stated as fact. Of the 1,457 entries that looked
tractable, 1,417 had no usable known side, and a sample of 900 shows **809 have no other
formula line at all** -- Colin Barker's entries typically post an empirical recurrence and
an empirical generating function together and nothing else. Of the remainder the known
side is usually a floor formula, a reference to another sequence, or a sum the parser
refuses.

That is a fact about the entries rather than a gap in the tooling, and it is the reason
this enormous vein yields four papers. Recorded as worked out.

### A finite verification is not a fact

A229504 posts `a(n) = 3/2*(n-1)*4^(n-1) for n = 1..210`. The engine took it as the known
side and proved a conjectured generating function from it. That is worthless: the formula
is asserted for 210 values and says nothing about the 211th, so anything derived from it
is a statement about a finite check. Withdrawn before it was built, and the known-side
detectors now refuse any formula qualified by `for n = a..b`, `checked`, `verified for` or
`up to n`.

The same discipline that catches "is this line a conjecture?" has to catch "is this line
a conjecture about finitely many terms?", and the second is easier to miss because it
looks like an ordinary formula with a range attached.

### Still unexploited

~~`a(n) = A######(m*n+k)` for `m ≥ 2`~~ — DONE 31 Aug 2026. Seven instances exist, not 14;
six open; three settled (A084703, A155543, A111403) and the other three are out of reach
for the reasons given in the m-section note above section 4. Roots of unity were never needed — both sides' posted
closed forms decided each one.

~~`xref.py`~~ — SWEPT. It settled exactly one entry, A052183, already in the roster. The
triangle references `A######(n,k)` -- another 21 -- still need the triangle's own formula
first, and remain untried.

Word-counting entries ("binary strings of length n with equally many 001 and 010") are a
recognisable family among the 268 unreadable ones, and they are not out of reach: a
transfer matrix in two variables gives a rational `R(x,u)`, the sequence is
`[x^n][u^0]R`, and a diagonal of a bivariate rational function is algebraic. Not attempted.

~~The second Lagrange form~~ — DEAD, measured 31 Aug 2026. The shape exists but carries no
conjectured recurrences anywhere; see the note above section 4.


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
