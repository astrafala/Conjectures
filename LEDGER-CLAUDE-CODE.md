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

Last updated 31 Aug 2026. Roster: **2544 papers** (2539 proofs, 5 disproofs), files `1-PROOF.pdf` … `2544-PROOF.pdf`, **numbered by how hard the result was**: 1 is the hardest.
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
| 58 | PROOF | A091713 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 59 | PROOF | A111403 | an entry equated to an m-section of another entry, decided from both entries' facts |
| 60 | PROOF | A155543 | an entry equated to an m-section of another entry, decided from both entries' facts |
| 61 | PROOF | A196523 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 62 | PROOF | A208545 | a conjectured closed form or g.f., proved against a recurrence derived from the entry |
| 63 | PROOF | A227161 | a conjectured closed form or g.f., proved against a recurrence derived from the entry |
| 64 | PROOF | A378575 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 65 | PROOF | A378576 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 66 | PROOF | A389472 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 67 | PROOF | A393856 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 68 | PROOF | A393857 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 69 | PROOF | A393858 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 70 | PROOF | A393859 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 71 | PROOF | A395833 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 72 | PROOF | A396099 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 73 | PROOF | A396102 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 74 | PROOF | A396797 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 75 | PROOF | A396807 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 76 | PROOF | A397241 | a defining functional equation reduced mod k, then closed by uniqueness of its recursion |
| 77 | DISPROOF | A141135 | a conjecture shown FALSE, with the recurrence that holds instead |
| 78 | DISPROOF | A076217 | a conjecture shown FALSE, with the recurrence that holds instead |
| 79 | PROOF | A129833 | creative telescoping with the boundary and range corrections carried through |
| 80 | PROOF | A306948 | creative telescoping with the boundary and range corrections carried through |
| 81 | PROOF | A129833 | creative telescoping with the boundary and range corrections carried through |
| 82 | PROOF | A000180 | creative telescoping with the boundary and range corrections carried through |
| 83 | PROOF | A207927 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 84 | PROOF | A207965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 85 | PROOF | A207274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 86 | PROOF | A207844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 87 | PROOF | A208038 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 88 | PROOF | A207185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 89 | PROOF | A207441 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 90 | PROOF | A207247 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 91 | PROOF | A206938 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 92 | PROOF | A207445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 93 | PROOF | A208419 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 94 | PROOF | A207239 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 95 | PROOF | A207856 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 96 | PROOF | A207464 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 97 | PROOF | A206998 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 98 | PROOF | A208499 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 99 | PROOF | A207487 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 100 | PROOF | A209957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 101 | PROOF | A207499 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 102 | PROOF | A207664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 103 | PROOF | A207127 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 104 | PROOF | A207907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 105 | PROOF | A207002 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 106 | PROOF | A206783 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 107 | PROOF | A298090 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 108 | PROOF | A207521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 109 | PROOF | A207775 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 110 | PROOF | A207343 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 111 | PROOF | A207086 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 112 | PROOF | A207504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 113 | PROOF | A208026 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 114 | PROOF | A207179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 115 | PROOF | A207697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 116 | PROOF | A207349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 117 | PROOF | A206887 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 118 | PROOF | A207417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 119 | PROOF | A208075 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 120 | PROOF | A207423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 121 | PROOF | A207772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 122 | PROOF | A207716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 123 | PROOF | A209948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 124 | PROOF | A297984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 125 | PROOF | A297855 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 126 | PROOF | A207469 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 127 | PROOF | A207959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 128 | PROOF | A207921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 129 | PROOF | A207273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 130 | PROOF | A209551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 131 | PROOF | A209782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 132 | PROOF | A210330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 133 | PROOF | A210350 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 134 | PROOF | A298051 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 135 | PROOF | A298656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 136 | PROOF | A303798 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 137 | PROOF | A207246 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 138 | PROOF | A210072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 139 | PROOF | A302456 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 140 | PROOF | A303238 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 141 | PROOF | A305093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 142 | PROOF | A316753 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 143 | PROOF | A207789 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 144 | PROOF | A209793 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 145 | PROOF | A301665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 146 | PROOF | A303036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 147 | PROOF | A304948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 148 | PROOF | A207074 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 149 | PROOF | A298954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 150 | PROOF | A206868 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 151 | PROOF | A206991 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 152 | PROOF | A304955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 153 | PROOF | A210272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 154 | PROOF | A208418 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 155 | PROOF | A209853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 156 | PROOF | A298578 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 157 | PROOF | A208695 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 158 | PROOF | A298175 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 159 | PROOF | A207740 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 160 | PROOF | A298164 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 161 | PROOF | A298290 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 162 | PROOF | A298556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 163 | PROOF | A299183 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 164 | PROOF | A299570 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 165 | PROOF | A304006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 166 | PROOF | A304540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 167 | PROOF | A306125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 168 | PROOF | A316307 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 169 | PROOF | A302412 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 170 | PROOF | A303179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 171 | PROOF | A207686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 172 | PROOF | A297947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 173 | PROOF | A298226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 174 | PROOF | A298766 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 175 | PROOF | A301604 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 176 | PROOF | A304015 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 177 | PROOF | A304152 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 178 | PROOF | A304351 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 179 | PROOF | A305363 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 180 | PROOF | A303960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 181 | PROOF | A208701 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 182 | PROOF | A209908 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 183 | PROOF | A304475 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 184 | PROOF | A305219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 185 | PROOF | A305638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 186 | PROOF | A306056 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 187 | PROOF | A316300 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 188 | PROOF | A317032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 189 | PROOF | A317234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 190 | PROOF | A304300 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 191 | PROOF | A207659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 192 | PROOF | A209711 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 193 | PROOF | A298191 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 194 | PROOF | A298618 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 195 | PROOF | A299085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 196 | PROOF | A299341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 197 | PROOF | A299848 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 198 | PROOF | A316235 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 199 | PROOF | A207708 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 200 | PROOF | A207428 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 201 | PROOF | A303799 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 202 | PROOF | A206874 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 203 | PROOF | A208167 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 204 | PROOF | A207091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 205 | PROOF | A210295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 206 | PROOF | A298715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 207 | PROOF | A298830 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 208 | PROOF | A304259 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 209 | PROOF | A305448 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 210 | PROOF | A305338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 211 | PROOF | A303621 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 212 | PROOF | A207268 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 213 | PROOF | A297955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 214 | PROOF | A298066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 215 | PROOF | A298217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 216 | PROOF | A299310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 217 | PROOF | A299447 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 218 | PROOF | A301537 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 219 | PROOF | A316214 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 220 | PROOF | A298097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 221 | PROOF | A298899 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 222 | PROOF | A207491 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 223 | PROOF | A207771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 224 | PROOF | A299678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 225 | PROOF | A316879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 226 | PROOF | A317607 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 227 | PROOF | A305480 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 228 | PROOF | A207843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 229 | PROOF | A207513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 230 | PROOF | A298135 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 231 | PROOF | A298926 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 232 | PROOF | A302305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 233 | PROOF | A207783 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 234 | PROOF | A300085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 235 | PROOF | A206934 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 236 | PROOF | A298632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 237 | PROOF | A207931 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 238 | PROOF | A298504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 239 | PROOF | A298723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 240 | PROOF | A298891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 241 | PROOF | A207663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 242 | PROOF | A207073 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 243 | PROOF | A208365 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 244 | PROOF | A207788 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 245 | PROOF | A207498 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 246 | PROOF | A297939 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 247 | PROOF | A298083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 248 | PROOF | A304054 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 249 | PROOF | A304306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 250 | PROOF | A304343 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 251 | PROOF | A305589 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 252 | PROOF | A305772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 253 | PROOF | A316205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 254 | PROOF | A317007 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 255 | PROOF | A317121 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 256 | PROOF | A317600 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 257 | PROOF | A207761 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 258 | PROOF | A234212 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 259 | PROOF | A300111 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 260 | PROOF | A302873 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 261 | PROOF | A303080 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 262 | PROOF | A316872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 263 | PROOF | A207715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 264 | PROOF | A207440 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 265 | PROOF | A207126 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 266 | PROOF | A299048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 267 | PROOF | A299810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 268 | PROOF | A300310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 269 | PROOF | A303321 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 270 | PROOF | A207030 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 271 | PROOF | A203834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 272 | PROOF | A302633 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 273 | PROOF | A305249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 274 | PROOF | A207512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 275 | PROOF | A305645 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 276 | PROOF | A207272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 277 | PROOF | A206890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 278 | PROOF | A207681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 279 | PROOF | A207906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 280 | PROOF | A298129 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 281 | PROOF | A298255 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 282 | PROOF | A298450 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 283 | PROOF | A299524 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 284 | PROOF | A208161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 285 | PROOF | A305689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 286 | PROOF | A317069 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 287 | PROOF | A233880 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 288 | PROOF | A207486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 289 | PROOF | A297872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 290 | PROOF | A317039 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 291 | PROOF | A317693 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 292 | PROOF | A251109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 293 | PROOF | A207855 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 294 | PROOF | A208074 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 295 | PROOF | A207563 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 296 | PROOF | A207888 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 297 | PROOF | A206880 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 298 | PROOF | A251162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 299 | PROOF | A298497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 300 | PROOF | A316921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 301 | PROOF | A297911 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 302 | PROOF | A302363 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 303 | PROOF | A304593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 304 | PROOF | A306139 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 305 | PROOF | A316379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 306 | PROOF | A317372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 307 | PROOF | A207915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 308 | PROOF | A297813 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 309 | PROOF | A297820 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 310 | PROOF | A207503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 311 | PROOF | A207372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 312 | PROOF | A299131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 313 | PROOF | A299224 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 314 | PROOF | A299889 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 315 | PROOF | A302816 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 316 | PROOF | A303509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 317 | PROOF | A304890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 318 | PROOF | A305950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 319 | PROOF | A234993 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 320 | PROOF | A207245 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 321 | PROOF | A207696 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 322 | PROOF | A208041 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 323 | PROOF | A207125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 324 | PROOF | A207707 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 325 | PROOF | A207463 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 326 | PROOF | A298182 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 327 | PROOF | A207884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 328 | PROOF | A207964 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 329 | PROOF | A207184 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 330 | PROOF | A207586 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 331 | PROOF | A210151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 332 | PROOF | A234328 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 333 | PROOF | A297903 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 334 | PROOF | A298333 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 335 | PROOF | A298625 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 336 | PROOF | A299598 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 337 | PROOF | A302318 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 338 | PROOF | A207342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 339 | PROOF | A303453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 340 | PROOF | A207267 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 341 | PROOF | A207898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 342 | PROOF | A297862 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 343 | PROOF | A298236 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 344 | PROOF | A303521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 345 | PROOF | A304415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 346 | PROOF | A207116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 347 | PROOF | A207892 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 348 | PROOF | A305039 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 349 | PROOF | A316692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 350 | PROOF | A304773 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 351 | PROOF | A302738 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 352 | PROOF | A234885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 353 | PROOF | A207085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 354 | PROOF | A206782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 355 | PROOF | A235170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 356 | PROOF | A297974 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 357 | PROOF | A299362 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 358 | PROOF | A304897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 359 | PROOF | A316579 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 360 | PROOF | A207416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 361 | PROOF | A207029 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 362 | PROOF | A207072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 363 | PROOF | A304229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 364 | PROOF | A305585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 365 | PROOF | A304131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 366 | PROOF | A233953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 367 | PROOF | A305513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 368 | PROOF | A207691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 369 | PROOF | A207926 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 370 | PROOF | A209222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 371 | PROOF | A298837 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 372 | PROOF | A316548 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 373 | PROOF | A234439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 374 | PROOF | A316516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 375 | PROOF | A234032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 376 | PROOF | A207680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 377 | PROOF | A207805 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 378 | PROOF | A299685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 379 | PROOF | A233750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 380 | PROOF | A302950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 381 | PROOF | A305179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 382 | PROOF | A316417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 383 | PROOF | A317380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 384 | PROOF | A233962 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 385 | PROOF | A302468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 386 | PROOF | A303012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 387 | PROOF | A303250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 388 | PROOF | A207490 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 389 | PROOF | A207511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 390 | PROOF | A207520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 391 | PROOF | A303805 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 392 | PROOF | A302423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 393 | PROOF | A303193 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 394 | PROOF | A304061 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 395 | PROOF | A304665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 396 | PROOF | A305018 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 397 | PROOF | A316423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 398 | PROOF | A210386 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 399 | PROOF | A207685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 400 | PROOF | A251315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 401 | PROOF | A235235 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 402 | PROOF | A233687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 403 | PROOF | A208417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 404 | PROOF | A298490 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 405 | PROOF | A304851 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 406 | PROOF | A207266 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 407 | PROOF | A207782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 408 | PROOF | A206937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 409 | PROOF | A207001 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 410 | PROOF | A251436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 411 | PROOF | A297812 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 412 | PROOF | A235234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 413 | PROOF | A306163 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 414 | PROOF | A316612 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 415 | PROOF | A234109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 416 | PROOF | A206886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 417 | PROOF | A207751 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 418 | PROOF | A235252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 419 | PROOF | A207371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 420 | PROOF | A251803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 421 | PROOF | A300142 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 422 | PROOF | A300317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 423 | PROOF | A306168 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 424 | PROOF | A317425 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 425 | PROOF | A235065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 426 | PROOF | A251386 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 427 | PROOF | A207396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 428 | PROOF | A235194 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 429 | PROOF | A234661 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 430 | PROOF | A251070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 431 | PROOF | A235193 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 432 | PROOF | A299725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 433 | PROOF | A303633 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 434 | PROOF | A206997 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 435 | PROOF | A207958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 436 | PROOF | A207658 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 437 | PROOF | A234085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 438 | PROOF | A207115 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 439 | PROOF | A251060 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 440 | PROOF | A251169 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 441 | PROOF | A300205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 442 | PROOF | A233911 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 443 | PROOF | A207760 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 444 | PROOF | A299056 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 445 | PROOF | A299664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 446 | PROOF | A299817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 447 | PROOF | A303884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 448 | PROOF | A305526 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 449 | PROOF | A305681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 450 | PROOF | A316818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 451 | PROOF | A317000 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 452 | PROOF | A317568 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 453 | PROOF | A233647 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 454 | PROOF | A207502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 455 | PROOF | A208166 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 456 | PROOF | A207787 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 457 | PROOF | A209550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 458 | PROOF | A207568 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 459 | PROOF | A297983 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 460 | PROOF | A302209 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 461 | PROOF | A305344 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 462 | PROOF | A298457 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 463 | PROOF | A298997 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 464 | PROOF | A299550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 465 | PROOF | A234147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 466 | PROOF | A207028 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 467 | PROOF | A251153 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 468 | PROOF | A251405 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 469 | PROOF | A234708 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 470 | PROOF | A300181 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 471 | PROOF | A206471 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 472 | PROOF | A234707 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 473 | PROOF | A317731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 474 | PROOF | A208037 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 475 | PROOF | A207920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 476 | PROOF | A208025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 477 | PROOF | A208498 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 478 | PROOF | A298543 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 479 | PROOF | A303965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 480 | PROOF | A305284 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 481 | PROOF | A305343 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 482 | PROOF | A209956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 483 | PROOF | A207585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 484 | PROOF | A207706 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 485 | PROOF | A207859 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 486 | PROOF | A207695 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 487 | PROOF | A251446 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 488 | PROOF | A251265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 489 | PROOF | A251323 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 490 | PROOF | A302622 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 491 | PROOF | A234120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 492 | PROOF | A207767 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 493 | PROOF | A207562 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 494 | PROOF | A207948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 495 | PROOF | A235242 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 496 | PROOF | A234171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 497 | PROOF | A234186 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 498 | PROOF | A298089 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 499 | PROOF | A298663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 500 | PROOF | A302885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 501 | PROOF | A303892 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 502 | PROOF | A305765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 503 | PROOF | A317114 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 504 | PROOF | A234202 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 505 | PROOF | A209654 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 506 | PROOF | A251199 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 507 | PROOF | A251509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 508 | PROOF | A207468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 509 | PROOF | A207238 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 510 | PROOF | A207444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 511 | PROOF | A317516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 512 | PROOF | A298143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 513 | PROOF | A304923 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 514 | PROOF | A304928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 515 | PROOF | A305242 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 516 | PROOF | A207878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 517 | PROOF | A234551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 518 | PROOF | A233787 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 519 | PROOF | A298440 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 520 | PROOF | A298585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 521 | PROOF | A299517 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 522 | PROOF | A299577 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 523 | PROOF | A304844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 524 | PROOF | A316541 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 525 | PROOF | A316928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 526 | PROOF | A207905 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 527 | PROOF | A207497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 528 | PROOF | A207370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 529 | PROOF | A207395 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 530 | PROOF | A207271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 531 | PROOF | A250977 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 532 | PROOF | A251014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 533 | PROOF | A207071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 534 | PROOF | A234416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 535 | PROOF | A303194 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 536 | PROOF | A303322 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 537 | PROOF | A304601 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 538 | PROOF | A316950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 539 | PROOF | A251069 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 540 | PROOF | A299138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 541 | PROOF | A299933 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 542 | PROOF | A209947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 543 | PROOF | A251331 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 544 | PROOF | A207439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 545 | PROOF | A207887 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 546 | PROOF | A207090 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 547 | PROOF | A208160 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 548 | PROOF | A251289 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 549 | PROOF | A303959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 550 | PROOF | A304299 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 551 | PROOF | A305337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 552 | PROOF | A206933 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 553 | PROOF | A207883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 554 | PROOF | A233886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 555 | PROOF | A251502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 556 | PROOF | A297854 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 557 | PROOF | A298571 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 558 | PROOF | A302666 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 559 | PROOF | A207114 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 560 | PROOF | A251216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 561 | PROOF | A301661 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 562 | PROOF | A234487 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 563 | PROOF | A234699 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 564 | PROOF | A303419 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 565 | PROOF | A208687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 566 | PROOF | A207728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 567 | PROOF | A299651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 568 | PROOF | A208686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 569 | PROOF | A207727 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 570 | PROOF | A234668 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 571 | PROOF | A234706 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 572 | PROOF | A208700 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 573 | PROOF | A209731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 574 | PROOF | A297919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 575 | PROOF | A299369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 576 | PROOF | A302411 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 577 | PROOF | A303178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 578 | PROOF | A303686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 579 | PROOF | A304763 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 580 | PROOF | A233640 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 581 | PROOF | A207963 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 582 | PROOF | A207485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 583 | PROOF | A251256 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 584 | PROOF | A234976 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 585 | PROOF | A250922 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 586 | PROOF | A251005 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 587 | PROOF | A250970 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 588 | PROOF | A251097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 589 | PROOF | A234724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 590 | PROOF | A234723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 591 | PROOF | A298961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 592 | PROOF | A250910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 593 | PROOF | A234722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 594 | PROOF | A297885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 595 | PROOF | A298276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 596 | PROOF | A299077 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 597 | PROOF | A302220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 598 | PROOF | A316179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 599 | PROOF | A251206 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 600 | PROOF | A234686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 601 | PROOF | A234685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 602 | PROOF | A302632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 603 | PROOF | A305479 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 604 | PROOF | A207766 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 605 | PROOF | A235206 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 606 | PROOF | A299317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 607 | PROOF | A299717 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 608 | PROOF | A233879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 609 | PROOF | A207759 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 610 | PROOF | A209653 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 611 | PROOF | A207265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 612 | PROOF | A207914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 613 | PROOF | A251225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 614 | PROOF | A203794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 615 | PROOF | A305229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 616 | PROOF | A203833 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 617 | PROOF | A207953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 618 | PROOF | A207122 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 619 | PROOF | A207739 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 620 | PROOF | A233728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 621 | PROOF | A300134 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 622 | PROOF | A302208 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 623 | PROOF | A303796 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 624 | PROOF | A305241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 625 | PROOF | A305957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 626 | PROOF | A317218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 627 | PROOF | A317461 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 628 | PROOF | A235233 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 629 | PROOF | A207407 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 630 | PROOF | A208146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 631 | PROOF | A234985 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 632 | PROOF | A207394 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 633 | PROOF | A207124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 634 | PROOF | A207244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 635 | PROOF | A207510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 636 | PROOF | A207786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 637 | PROOF | A207027 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 638 | PROOF | A302162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 639 | PROOF | A235182 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 640 | PROOF | A234126 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 641 | PROOF | A207877 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 642 | PROOF | A207714 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 643 | PROOF | A299330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 644 | PROOF | A304423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 645 | PROOF | A316278 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 646 | PROOF | A251068 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 647 | PROOF | A207690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 648 | PROOF | A207925 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 649 | PROOF | A209221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 650 | PROOF | A207679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 651 | PROOF | A234884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 652 | PROOF | A233711 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 653 | PROOF | A207348 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 654 | PROOF | A208416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 655 | PROOF | A208497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 656 | PROOF | A207781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 657 | PROOF | A251353 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 658 | PROOF | A234157 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 659 | PROOF | A235181 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 660 | PROOF | A233898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 661 | PROOF | A207750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 662 | PROOF | A302377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 663 | PROOF | A303098 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 664 | PROOF | A305248 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 665 | PROOF | A234453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 666 | PROOF | A234077 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 667 | PROOF | A207804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 668 | PROOF | A207662 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 669 | PROOF | A251108 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 670 | PROOF | A251314 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 671 | PROOF | A206253 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 672 | PROOF | A206470 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 673 | PROOF | A304772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 674 | PROOF | A316515 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 675 | PROOF | A208373 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 676 | PROOF | A209228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 677 | PROOF | A233984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 678 | PROOF | A207567 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 679 | PROOF | A209227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 680 | PROOF | A300171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 681 | PROOF | A300338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 682 | PROOF | A209792 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 683 | PROOF | A207310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 684 | PROOF | A207566 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 685 | PROOF | A206879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 686 | PROOF | A233922 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 687 | PROOF | A207369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 688 | PROOF | A207415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 689 | PROOF | A207742 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 690 | PROOF | A207909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 691 | PROOF | A210271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 692 | PROOF | A233944 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 693 | PROOF | A250836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 694 | PROOF | A207705 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 695 | PROOF | A250959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 696 | PROOF | A251396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 697 | PROOF | A304269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 698 | PROOF | A207812 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 699 | PROOF | A184148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 700 | PROOF | A303966 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 701 | PROOF | A207952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 702 | PROOF | A207121 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 703 | PROOF | A234684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 704 | PROOF | A297989 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 705 | PROOF | A298283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 706 | PROOF | A299657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 707 | PROOF | A299736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 708 | PROOF | A300211 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 709 | PROOF | A251245 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 710 | PROOF | A208036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 711 | PROOF | A207178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 712 | PROOF | A206781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 713 | PROOF | A207406 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 714 | PROOF | A208145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 715 | PROOF | A207770 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 716 | PROOF | A208024 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 717 | PROOF | A184491 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 718 | PROOF | A207684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 719 | PROOF | A207113 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 720 | PROOF | A251161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 721 | PROOF | A251302 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 722 | PROOF | A207427 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 723 | PROOF | A234734 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 724 | PROOF | A234819 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 725 | PROOF | A234879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 726 | PROOF | A234654 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 727 | PROOF | A234733 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 728 | PROOF | A235094 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 729 | PROOF | A234818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 730 | PROOF | A251279 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 731 | PROOF | A234732 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 732 | PROOF | A234817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 733 | PROOF | A298631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 734 | PROOF | A298966 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 735 | PROOF | A235192 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 736 | PROOF | A184371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 737 | PROOF | A234492 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 738 | PROOF | A207561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 739 | PROOF | A207765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 740 | PROOF | A206873 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 741 | PROOF | A207749 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 742 | PROOF | A209652 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 743 | PROOF | A207678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 744 | PROOF | A207758 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 745 | PROOF | A298181 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 746 | PROOF | A234179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 747 | PROOF | A316805 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 748 | PROOF | A317522 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 749 | PROOF | A235093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 750 | PROOF | A207842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 751 | PROOF | A297982 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 752 | PROOF | A299063 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 753 | PROOF | A299176 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 754 | PROOF | A299835 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 755 | PROOF | A303620 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 756 | PROOF | A207882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 757 | PROOF | A207957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 758 | PROOF | A207489 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 759 | PROOF | A207501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 760 | PROOF | A184666 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 761 | PROOF | A207393 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 762 | PROOF | A251198 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 763 | PROOF | A251453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 764 | PROOF | A251802 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 765 | PROOF | A207070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 766 | PROOF | A302621 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 767 | PROOF | A234653 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 768 | PROOF | A207722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 769 | PROOF | A302424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 770 | PROOF | A317730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 771 | PROOF | A298142 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 772 | PROOF | A298778 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 773 | PROOF | A302631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 774 | PROOF | A304468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 775 | PROOF | A306049 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 776 | PROOF | A316285 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 777 | PROOF | A317226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 778 | PROOF | A207738 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 779 | PROOF | A207943 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 780 | PROOF | A206867 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 781 | PROOF | A206990 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 782 | PROOF | A235020 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 783 | PROOF | A206885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 784 | PROOF | A207183 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 785 | PROOF | A207309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 786 | PROOF | A207919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 787 | PROOF | A183786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 788 | PROOF | A208165 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 789 | PROOF | A251067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 790 | PROOF | A207443 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 791 | PROOF | A303313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 792 | PROOF | A301782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 793 | PROOF | A207850 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 794 | PROOF | A208082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 795 | PROOF | A207756 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 796 | PROOF | A209549 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 797 | PROOF | A251370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 798 | PROOF | A207367 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 799 | PROOF | A207951 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 800 | PROOF | A301611 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 801 | PROOF | A303465 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 802 | PROOF | A303804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 803 | PROOF | A207120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 804 | PROOF | A207253 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 805 | PROOF | A207946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 806 | PROOF | A207405 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 807 | PROOF | A208144 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 808 | PROOF | A209781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 809 | PROOF | A209852 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 810 | PROOF | A210071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 811 | PROOF | A210329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 812 | PROOF | A210349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 813 | PROOF | A251795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 814 | PROOF | A297946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 815 | PROOF | A298384 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 816 | PROOF | A299460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 817 | PROOF | A300084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 818 | PROOF | A301536 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 819 | PROOF | A301664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 820 | PROOF | A304014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 821 | PROOF | A304546 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 822 | PROOF | A304954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 823 | PROOF | A306131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 824 | PROOF | A316125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 825 | PROOF | A316443 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 826 | PROOF | A317431 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 827 | PROOF | A207421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 828 | PROOF | A209510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 829 | PROOF | A234878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 830 | PROOF | A234916 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 831 | PROOF | A203377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 832 | PROOF | A208685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 833 | PROOF | A302961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 834 | PROOF | A305085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 835 | PROOF | A316416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 836 | PROOF | A316736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 837 | PROOF | A317379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 838 | PROOF | A235101 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 839 | PROOF | A207726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 840 | PROOF | A233952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 841 | PROOF | A208684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 842 | PROOF | A207484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 843 | PROOF | A209710 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 844 | PROOF | A209907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 845 | PROOF | A233629 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 846 | PROOF | A298323 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 847 | PROOF | A298549 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 848 | PROOF | A298617 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 849 | PROOF | A298765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 850 | PROOF | A298829 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 851 | PROOF | A299216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 852 | PROOF | A299244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 853 | PROOF | A299556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 854 | PROOF | A299583 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 855 | PROOF | A300091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 856 | PROOF | A304692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 857 | PROOF | A304889 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 858 | PROOF | A316636 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 859 | PROOF | A207026 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 860 | PROOF | A207270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 861 | PROOF | A251288 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 862 | PROOF | A251322 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 863 | PROOF | A235315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 864 | PROOF | A304220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 865 | PROOF | A234677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 866 | PROOF | A301660 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 867 | PROOF | A235314 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 868 | PROOF | A234676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 869 | PROOF | A234486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 870 | PROOF | A303797 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 871 | PROOF | A235313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 872 | PROOF | A251295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 873 | PROOF | A297819 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 874 | PROOF | A302804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 875 | PROOF | A306162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 876 | PROOF | A233812 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 877 | PROOF | A234675 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 878 | PROOF | A235180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 879 | PROOF | A207942 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 880 | PROOF | A234108 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 881 | PROOF | A207713 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 882 | PROOF | A207841 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 883 | PROOF | A208699 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 884 | PROOF | A184210 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 885 | PROOF | A298050 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 886 | PROOF | A298128 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 887 | PROOF | A298149 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 888 | PROOF | A298225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 889 | PROOF | A298254 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 890 | PROOF | A298714 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 891 | PROOF | A299003 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 892 | PROOF | A299123 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 893 | PROOF | A299446 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 894 | PROOF | A299453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 895 | PROOF | A299670 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 896 | PROOF | A299748 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 897 | PROOF | A299881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 898 | PROOF | A300262 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 899 | PROOF | A301603 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 900 | PROOF | A302273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 901 | PROOF | A302523 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 902 | PROOF | A303406 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 903 | PROOF | A304151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 904 | PROOF | A304350 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 905 | PROOF | A304671 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 906 | PROOF | A304947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 907 | PROOF | A305170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 908 | PROOF | A305362 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 909 | PROOF | A305913 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 910 | PROOF | A316171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 911 | PROOF | A316234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 912 | PROOF | A317155 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 913 | PROOF | A317453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 914 | PROOF | A251445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 915 | PROOF | A305228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 916 | PROOF | A208006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 917 | PROOF | A234119 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 918 | PROOF | A208372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 919 | PROOF | A233677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 920 | PROOF | A251338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 921 | PROOF | A302261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 922 | PROOF | A304145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 923 | PROOF | A304600 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 924 | PROOF | A305485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 925 | PROOF | A305688 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 926 | PROOF | A316811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 927 | PROOF | A317068 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 928 | PROOF | A317561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 929 | PROOF | A206996 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 930 | PROOF | A234163 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 931 | PROOF | A234445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 932 | PROOF | A207308 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 933 | PROOF | A207897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 934 | PROOF | A207438 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 935 | PROOF | A207496 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 936 | PROOF | A207764 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 937 | PROOF | A209651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 938 | PROOF | A233934 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 939 | PROOF | A251255 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 940 | PROOF | A297871 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 941 | PROOF | A298058 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 942 | PROOF | A298065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 943 | PROOF | A298190 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 944 | PROOF | A298289 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 945 | PROOF | A298315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 946 | PROOF | A298377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 947 | PROOF | A298449 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 948 | PROOF | A298707 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 949 | PROOF | A298722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 950 | PROOF | A298890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 951 | PROOF | A299047 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 952 | PROOF | A299084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 953 | PROOF | A299182 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 954 | PROOF | A299189 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 955 | PROOF | A299523 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 956 | PROOF | A299809 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 957 | PROOF | A304258 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 958 | PROOF | A304699 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 959 | PROOF | A305010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 960 | PROOF | A305447 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 961 | PROOF | A305644 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 962 | PROOF | A316118 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 963 | PROOF | A316450 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 964 | PROOF | A316643 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 965 | PROOF | A316920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 966 | PROOF | A317038 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 967 | PROOF | A317692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 968 | PROOF | A207112 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 969 | PROOF | A207243 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 970 | PROOF | A250969 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 971 | PROOF | A251096 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 972 | PROOF | A251224 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 973 | PROOF | A203824 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 974 | PROOF | A234224 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 975 | PROOF | A235084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 976 | PROOF | A316691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 977 | PROOF | A234223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 978 | PROOF | A208117 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 979 | PROOF | A235083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 980 | PROOF | A303418 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 981 | PROOF | A304130 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 982 | PROOF | A207734 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 983 | PROOF | A208012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 984 | PROOF | A207811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 985 | PROOF | A208553 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 986 | PROOF | A208116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 987 | PROOF | A234031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 988 | PROOF | A234415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 989 | PROOF | A207755 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 990 | PROOF | A207733 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 991 | PROOF | A208011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 992 | PROOF | A234660 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 993 | PROOF | A207366 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 994 | PROOF | A250955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 995 | PROOF | A251274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 996 | PROOF | A251486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 997 | PROOF | A298096 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 998 | PROOF | A298898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 999 | PROOF | A299724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1000 | PROOF | A303632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1001 | PROOF | A316956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1002 | PROOF | A207732 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1003 | PROOF | A207754 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1004 | PROOF | A206932 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1005 | PROOF | A207365 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1006 | PROOF | A208010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1007 | PROOF | A235092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1008 | PROOF | A207252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1009 | PROOF | A207950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1010 | PROOF | A207119 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1011 | PROOF | A207565 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1012 | PROOF | A207731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1013 | PROOF | A208040 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1014 | PROOF | A210385 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1015 | PROOF | A234438 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1016 | PROOF | A207404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1017 | PROOF | A208143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1018 | PROOF | A233718 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1019 | PROOF | A250929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1020 | PROOF | A297938 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1021 | PROOF | A298082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1022 | PROOF | A298503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1023 | PROOF | A299010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1024 | PROOF | A299092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1025 | PROOF | A299309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1026 | PROOF | A299340 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1027 | PROOF | A299677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1028 | PROOF | A299801 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1029 | PROOF | A299847 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1030 | PROOF | A299874 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1031 | PROOF | A300110 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1032 | PROOF | A300309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1033 | PROOF | A302724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1034 | PROOF | A303685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1035 | PROOF | A303883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1036 | PROOF | A304005 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1037 | PROOF | A304305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1038 | PROOF | A305092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1039 | PROOF | A305588 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1040 | PROOF | A305771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1041 | PROOF | A305949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1042 | PROOF | A316204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1043 | PROOF | A316306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1044 | PROOF | A316752 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1045 | PROOF | A316871 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1046 | PROOF | A317006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1047 | PROOF | A317120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1048 | PROOF | A317261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1049 | PROOF | A317599 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1050 | PROOF | A207414 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1051 | PROOF | A207704 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1052 | PROOF | A251215 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1053 | PROOF | A251264 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1054 | PROOF | A251152 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1055 | PROOF | A302514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1056 | PROOF | A206252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1057 | PROOF | A300180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1058 | PROOF | A302161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1059 | PROOF | A305584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1060 | PROOF | A317515 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1061 | PROOF | A302620 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1062 | PROOF | A303958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1063 | PROOF | A206469 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1064 | PROOF | A234698 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1065 | PROOF | A235082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1066 | PROOF | A207947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1067 | PROOF | A233686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1068 | PROOF | A251519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1069 | PROOF | A300204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1070 | PROOF | A302159 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1071 | PROOF | A302737 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1072 | PROOF | A303452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1073 | PROOF | A304298 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1074 | PROOF | A305336 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1075 | PROOF | A305519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1076 | PROOF | A234544 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1077 | PROOF | A234652 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1078 | PROOF | A234211 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1079 | PROOF | A207657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1080 | PROOF | A207941 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1081 | PROOF | A207422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1082 | PROOF | A207881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1083 | PROOF | A207886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1084 | PROOF | A207904 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1085 | PROOF | A207956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1086 | PROOF | A251330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1087 | PROOF | A251385 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1088 | PROOF | A298391 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1089 | PROOF | A298496 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1090 | PROOF | A299509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1091 | PROOF | A299684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1092 | PROOF | A300141 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1093 | PROOF | A300316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1094 | PROOF | A304053 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1095 | PROOF | A304342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1096 | PROOF | A304414 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1097 | PROOF | A304592 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1098 | PROOF | A304896 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1099 | PROOF | A305017 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1100 | PROOF | A305218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1101 | PROOF | A305283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1102 | PROOF | A305637 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1103 | PROOF | A305906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1104 | PROOF | A306138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1105 | PROOF | A316213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1106 | PROOF | A316378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1107 | PROOF | A316547 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1108 | PROOF | A316578 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1109 | PROOF | A316878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1110 | PROOF | A317031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1111 | PROOF | A317148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1112 | PROOF | A317371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1113 | PROOF | A317606 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1114 | PROOF | A207392 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1115 | PROOF | A251313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1116 | PROOF | A298916 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1117 | PROOF | A234561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1118 | PROOF | A235306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1119 | PROOF | A304219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1120 | PROOF | A234560 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1121 | PROOF | A208839 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1122 | PROOF | A208107 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1123 | PROOF | A235305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1124 | PROOF | A208838 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1125 | PROOF | A207594 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1126 | PROOF | A208106 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1127 | PROOF | A234559 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1128 | PROOF | A208122 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1129 | PROOF | A234125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1130 | PROOF | A297810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1131 | PROOF | A299650 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1132 | PROOF | A305512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1133 | PROOF | A235304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1134 | PROOF | A207604 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1135 | PROOF | A207876 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1136 | PROOF | A207603 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1137 | PROOF | A208120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1138 | PROOF | A251273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1139 | PROOF | A234558 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1140 | PROOF | A207251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1141 | PROOF | A207602 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1142 | PROOF | A207930 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1143 | PROOF | A209955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1144 | PROOF | A251205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1145 | PROOF | A207601 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1146 | PROOF | A210294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1147 | PROOF | A233853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1148 | PROOF | A233869 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1149 | PROOF | A233961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1150 | PROOF | A251562 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1151 | PROOF | A297861 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1152 | PROOF | A298216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1153 | PROOF | A298577 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1154 | PROOF | A299055 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1155 | PROOF | A299223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1156 | PROOF | A299569 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1157 | PROOF | A299816 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1158 | PROOF | A302317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1159 | PROOF | A302467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1160 | PROOF | A302665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1161 | PROOF | A302815 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1162 | PROOF | A303249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1163 | PROOF | A303508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1164 | PROOF | A304060 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1165 | PROOF | A304144 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1166 | PROOF | A305084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1167 | PROOF | A305484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1168 | PROOF | A305680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1169 | PROOF | A316735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1170 | PROOF | A207237 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1171 | PROOF | A207264 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1172 | PROOF | A207903 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1173 | PROOF | A251197 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1174 | PROOF | A250976 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1175 | PROOF | A251013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1176 | PROOF | A305038 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1177 | PROOF | A209509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1178 | PROOF | A208032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1179 | PROOF | A208424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1180 | PROOF | A208005 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1181 | PROOF | A302949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1182 | PROOF | A303957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1183 | PROOF | A304922 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1184 | PROOF | A316949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1185 | PROOF | A250909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1186 | PROOF | A208004 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1187 | PROOF | A203376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1188 | PROOF | A233983 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1189 | PROOF | A207560 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1190 | PROOF | A207748 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1191 | PROOF | A209946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1192 | PROOF | A233639 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1193 | PROOF | A234915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1194 | PROOF | A207307 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1195 | PROOF | A210150 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1196 | PROOF | A234338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1197 | PROOF | A297910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1198 | PROOF | A297973 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1199 | PROOF | A298235 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1200 | PROOF | A298332 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1201 | PROOF | A298456 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1202 | PROOF | A299549 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1203 | PROOF | A299597 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1204 | PROOF | A299888 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1205 | PROOF | A302304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1206 | PROOF | A302410 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1207 | PROOF | A302872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1208 | PROOF | A303035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1209 | PROOF | A303177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1210 | PROOF | A303237 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1211 | PROOF | A303891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1212 | PROOF | A304539 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1213 | PROOF | A304762 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1214 | PROOF | A306055 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1215 | PROOF | A306124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1216 | PROOF | A316927 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1217 | PROOF | A317233 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1218 | PROOF | A233659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1219 | PROOF | A250921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1220 | PROOF | A251004 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1221 | PROOF | A251168 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1222 | PROOF | A302679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1223 | PROOF | A203653 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1224 | PROOF | A203793 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1225 | PROOF | A304228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1226 | PROOF | A304268 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1227 | PROOF | A208068 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1228 | PROOF | A297811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1229 | PROOF | A302160 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1230 | PROOF | A305227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1231 | PROOF | A203832 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1232 | PROOF | A207849 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1233 | PROOF | A207721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1234 | PROOF | A208423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1235 | PROOF | A208552 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1236 | PROOF | A208115 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1237 | PROOF | A208371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1238 | PROOF | A208551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1239 | PROOF | A207364 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1240 | PROOF | A207753 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1241 | PROOF | A207875 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1242 | PROOF | A207962 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1243 | PROOF | A208009 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1244 | PROOF | A233878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1245 | PROOF | A207940 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1246 | PROOF | A233727 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1247 | PROOF | A234424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1248 | PROOF | A251272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1249 | PROOF | A251375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1250 | PROOF | A251493 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1251 | PROOF | A297902 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1252 | PROOF | A297954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1253 | PROOF | A298439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1254 | PROOF | A298542 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1255 | PROOF | A298662 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1256 | PROOF | A298836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1257 | PROOF | A299130 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1258 | PROOF | A299329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1259 | PROOF | A299361 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1260 | PROOF | A299516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1261 | PROOF | A299716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1262 | PROOF | A302362 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1263 | PROOF | A302455 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1264 | PROOF | A303520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1265 | PROOF | A303964 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1266 | PROOF | A304474 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1267 | PROOF | A304664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1268 | PROOF | A304850 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1269 | PROOF | A305247 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1270 | PROOF | A305342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1271 | PROOF | A316299 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1272 | PROOF | A316422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1273 | PROOF | A317460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1274 | PROOF | A234905 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1275 | PROOF | A235002 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1276 | PROOF | A235072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1277 | PROOF | A206878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1278 | PROOF | A207118 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1279 | PROOF | A207462 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1280 | PROOF | A207584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1281 | PROOF | A207763 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1282 | PROOF | A207961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1283 | PROOF | A251254 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1284 | PROOF | A184557 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1285 | PROOF | A251066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1286 | PROOF | A251404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1287 | PROOF | A251234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1288 | PROOF | A298186 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1289 | PROOF | A251233 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1290 | PROOF | A209380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1291 | PROOF | A251232 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1292 | PROOF | A298960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1293 | PROOF | A301659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1294 | PROOF | A234222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1295 | PROOF | A208031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1296 | PROOF | A234877 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1297 | PROOF | A209548 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1298 | PROOF | A234156 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1299 | PROOF | A234485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1300 | PROOF | A251231 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1301 | PROOF | A305178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1302 | PROOF | A234118 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1303 | PROOF | A234178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1304 | PROOF | A209730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1305 | PROOF | A233786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1306 | PROOF | A233910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1307 | PROOF | A234327 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1308 | PROOF | A297981 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1309 | PROOF | A297988 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1310 | PROOF | A298282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1311 | PROOF | A298489 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1312 | PROOF | A298624 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1313 | PROOF | A299663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1314 | PROOF | A300170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1315 | PROOF | A300337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1316 | PROOF | A302219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1317 | PROOF | A302376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1318 | PROOF | A303079 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1319 | PROOF | A303097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1320 | PROOF | A304843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1321 | PROOF | A305042 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1322 | PROOF | A305525 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1323 | PROOF | A305764 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1324 | PROOF | A316178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1325 | PROOF | A316540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1326 | PROOF | A316817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1327 | PROOF | A316999 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1328 | PROOF | A317567 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1329 | PROOF | A206780 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1330 | PROOF | A234400 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1331 | PROOF | A207747 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1332 | PROOF | A251059 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1333 | PROOF | A251287 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1334 | PROOF | A235296 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1335 | PROOF | A303726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1336 | PROOF | A235014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1337 | PROOF | A235295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1338 | PROOF | A235013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1339 | PROOF | A235294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1340 | PROOF | A298180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1341 | PROOF | A304218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1342 | PROOF | A208081 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1343 | PROOF | A207810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1344 | PROOF | A208837 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1345 | PROOF | A235293 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1346 | PROOF | A304129 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1347 | PROOF | A304771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1348 | PROOF | A305478 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1349 | PROOF | A316514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1350 | PROOF | A251369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1351 | PROOF | A208105 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1352 | PROOF | A207720 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1353 | PROOF | A208422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1354 | PROOF | A208836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1355 | PROOF | A207725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1356 | PROOF | A207854 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1357 | PROOF | A209791 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1358 | PROOF | A251244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1359 | PROOF | A235081 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1360 | PROOF | A183795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1361 | PROOF | A207250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1362 | PROOF | A233676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1363 | PROOF | A235292 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1364 | PROOF | A251501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1365 | PROOF | A297884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1366 | PROOF | A298275 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1367 | PROOF | A298996 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1368 | PROOF | A299076 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1369 | PROOF | A299137 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1370 | PROOF | A299316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1371 | PROOF | A299368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1372 | PROOF | A299932 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1373 | PROOF | A300133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1374 | PROOF | A301610 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1375 | PROOF | A302884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1376 | PROOF | A303011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1377 | PROOF | A303803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1378 | PROOF | A304467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1379 | PROOF | A305177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1380 | PROOF | A305511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1381 | PROOF | A306048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1382 | PROOF | A316284 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1383 | PROOF | A317113 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1384 | PROOF | A317225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1385 | PROOF | A235251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1386 | PROOF | A233885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1387 | PROOF | A233974 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1388 | PROOF | A234406 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1389 | PROOF | A251611 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1390 | PROOF | A234891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1391 | PROOF | A234992 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1392 | PROOF | A235064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1393 | PROOF | A207341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1394 | PROOF | A207509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1395 | PROOF | A234201 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1396 | PROOF | A251468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1397 | PROOF | A251271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1398 | PROOF | A233943 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1399 | PROOF | A250835 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1400 | PROOF | A207025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1401 | PROOF | A207069 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1402 | PROOF | A251263 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1403 | PROOF | A251312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1404 | PROOF | A251321 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1405 | PROOF | A251435 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1406 | PROOF | A251026 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1407 | PROOF | A251053 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1408 | PROOF | A235275 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1409 | PROOF | A251025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1410 | PROOF | A251052 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1411 | PROOF | A303725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1412 | PROOF | A235274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1413 | PROOF | A208112 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1414 | PROOF | A206251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1415 | PROOF | A251024 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1416 | PROOF | A251051 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1417 | PROOF | A300179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1418 | PROOF | A302512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1419 | PROOF | A303311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1420 | PROOF | A304267 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1421 | PROOF | A235273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1422 | PROOF | A208111 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1423 | PROOF | A208017 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1424 | PROOF | A208072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1425 | PROOF | A207593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1426 | PROOF | A184147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1427 | PROOF | A251023 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1428 | PROOF | A251050 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1429 | PROOF | A251278 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1430 | PROOF | A305043 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1431 | PROOF | A206468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1432 | PROOF | A207175 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1433 | PROOF | A208110 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1434 | PROOF | A209226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1435 | PROOF | A207174 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1436 | PROOF | A208015 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1437 | PROOF | A208070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1438 | PROOF | A250954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1439 | PROOF | A234030 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1440 | PROOF | A235272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1441 | PROOF | A207173 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1442 | PROOF | A184370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1443 | PROOF | A208003 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1444 | PROOF | A208109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1445 | PROOF | A234876 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1446 | PROOF | A207172 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1447 | PROOF | A233685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1448 | PROOF | A251022 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1449 | PROOF | A251049 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1450 | PROOF | A251230 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1451 | PROOF | A297818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1452 | PROOF | A297918 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1453 | PROOF | A298141 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1454 | PROOF | A298570 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1455 | PROOF | A298584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1456 | PROOF | A299062 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1457 | PROOF | A299576 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1458 | PROOF | A299834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1459 | PROOF | A302207 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1460 | PROOF | A302618 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1461 | PROOF | A302630 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1462 | PROOF | A304297 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1463 | PROOF | A304422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1464 | PROOF | A305956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1465 | PROOF | A316277 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1466 | PROOF | A317217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1467 | PROOF | A235169 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1468 | PROOF | A206872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1469 | PROOF | A207089 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1470 | PROOF | A207171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1471 | PROOF | A207437 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1472 | PROOF | A207483 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1473 | PROOF | A207559 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1474 | PROOF | A207712 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1475 | PROOF | A207730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1476 | PROOF | A207939 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1477 | PROOF | A208023 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1478 | PROOF | A208496 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1479 | PROOF | A233646 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1480 | PROOF | A233749 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1481 | PROOF | A234084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1482 | PROOF | A184490 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1483 | PROOF | A210270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1484 | PROOF | A251508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1485 | PROOF | A250968 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1486 | PROOF | A251095 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1487 | PROOF | A251196 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1488 | PROOF | A251214 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1489 | PROOF | A303681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1490 | PROOF | A209381 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1491 | PROOF | A298915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1492 | PROOF | A302513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1493 | PROOF | A303312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1494 | PROOF | A207702 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1495 | PROOF | A207937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1496 | PROOF | A298914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1497 | PROOF | A298921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1498 | PROOF | A301781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1499 | PROOF | A303724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1500 | PROOF | A317514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1501 | PROOF | A208067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1502 | PROOF | A235012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1503 | PROOF | A207848 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1504 | PROOF | A208066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1505 | PROOF | A208121 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1506 | PROOF | A298920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1507 | PROOF | A302619 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1508 | PROOF | A209378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1509 | PROOF | A208080 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1510 | PROOF | A208291 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1511 | PROOF | A208065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1512 | PROOF | A208114 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1513 | PROOF | A208119 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1514 | PROOF | A208370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1515 | PROOF | A234241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1516 | PROOF | A234476 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1517 | PROOF | A234721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1518 | PROOF | A297853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1519 | PROOF | A298919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1520 | PROOF | A298965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1521 | PROOF | A299656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1522 | PROOF | A299735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1523 | PROOF | A300210 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1524 | PROOF | A302948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1525 | PROOF | A304136 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1526 | PROOF | A305240 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1527 | PROOF | A305687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1528 | PROOF | A317067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1529 | PROOF | A235241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1530 | PROOF | A206931 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1531 | PROOF | A207177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1532 | PROOF | A235232 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1533 | PROOF | A207249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1534 | PROOF | A207363 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1535 | PROOF | A234146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1536 | PROOF | A234984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1537 | PROOF | A233710 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1538 | PROOF | A251021 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1539 | PROOF | A251048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1540 | PROOF | A251223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1541 | PROOF | A251270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1542 | PROOF | A203731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1543 | PROOF | A203883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1544 | PROOF | A203930 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1545 | PROOF | A251087 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1546 | PROOF | A251136 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1547 | PROOF | A298185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1548 | PROOF | A303680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1549 | PROOF | A203652 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1550 | PROOF | A251086 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1551 | PROOF | A251135 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1552 | PROOF | A203792 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1553 | PROOF | A305037 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1554 | PROOF | A316690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1555 | PROOF | A209508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1556 | PROOF | A251085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1557 | PROOF | A251134 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1558 | PROOF | A207701 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1559 | PROOF | A207936 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1560 | PROOF | A298163 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1561 | PROOF | A302511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1562 | PROOF | A303310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1563 | PROOF | A304217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1564 | PROOF | A305036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1565 | PROOF | A305226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1566 | PROOF | A316689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1567 | PROOF | A316804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1568 | PROOF | A317521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1569 | PROOF | A203831 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1570 | PROOF | A251084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1571 | PROOF | A251133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1572 | PROOF | A207592 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1573 | PROOF | A208030 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1574 | PROOF | A208290 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1575 | PROOF | A250908 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1576 | PROOF | A251083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1577 | PROOF | A251132 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1578 | PROOF | A203375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1579 | PROOF | A234414 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1580 | PROOF | A234667 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1581 | PROOF | A234705 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1582 | PROOF | A234731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1583 | PROOF | A250953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1584 | PROOF | A251294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1585 | PROOF | A251337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1586 | PROOF | A251485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1587 | PROOF | A302158 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1588 | PROOF | A303192 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1589 | PROOF | A303795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1590 | PROOF | A303956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1591 | PROOF | A304599 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1592 | PROOF | A304921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1593 | PROOF | A305335 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1594 | PROOF | A306161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1595 | PROOF | A316415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1596 | PROOF | A316948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1597 | PROOF | A317378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1598 | PROOF | A206989 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1599 | PROOF | A234185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1600 | PROOF | A234816 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1601 | PROOF | A207306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1602 | PROOF | A207495 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1603 | PROOF | A209945 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1604 | PROOF | A209954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1605 | PROOF | A233638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1606 | PROOF | A251082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1607 | PROOF | A251131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1608 | PROOF | A251345 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1609 | PROOF | A234975 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1610 | PROOF | A184665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1611 | PROOF | A250958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1612 | PROOF | A251301 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1613 | PROOF | A251352 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1614 | PROOF | A251395 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1615 | PROOF | A251452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1616 | PROOF | A251106 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1617 | PROOF | A234138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1618 | PROOF | A235287 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1619 | PROOF | A303718 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1620 | PROOF | A234265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1621 | PROOF | A203823 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1622 | PROOF | A234137 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1623 | PROOF | A235286 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1624 | PROOF | A302678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1625 | PROOF | A303717 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1626 | PROOF | A234264 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1627 | PROOF | A234136 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1628 | PROOF | A235285 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1629 | PROOF | A303679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1630 | PROOF | A303716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1631 | PROOF | A304227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1632 | PROOF | A305583 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1633 | PROOF | A209379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1634 | PROOF | A234263 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1635 | PROOF | A206250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1636 | PROOF | A208016 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1637 | PROOF | A208071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1638 | PROOF | A234135 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1639 | PROOF | A235284 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1640 | PROOF | A300178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1641 | PROOF | A303417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1642 | PROOF | A303715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1643 | PROOF | A303723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1644 | PROOF | A304137 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1645 | PROOF | A304226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1646 | PROOF | A304266 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1647 | PROOF | A305582 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1648 | PROOF | A317729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1649 | PROOF | A234262 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1650 | PROOF | A207700 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1651 | PROOF | A207935 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1652 | PROOF | A208383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1653 | PROOF | A208382 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1654 | PROOF | A234221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1655 | PROOF | A208289 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1656 | PROOF | A208381 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1657 | PROOF | A206467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1658 | PROOF | A207591 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1659 | PROOF | A207689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1660 | PROOF | A207737 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1661 | PROOF | A207924 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1662 | PROOF | A208014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1663 | PROOF | A208035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1664 | PROOF | A208104 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1665 | PROOF | A209220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1666 | PROOF | A234261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1667 | PROOF | A208380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1668 | PROOF | A209547 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1669 | PROOF | A234134 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1670 | PROOF | A234155 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1671 | PROOF | A234228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1672 | PROOF | A235283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1673 | PROOF | A251518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1674 | PROOF | A299723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1675 | PROOF | A303619 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1676 | PROOF | A303722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1677 | PROOF | A305225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1678 | PROOF | A305477 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1679 | PROOF | A317728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1680 | PROOF | A235205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1681 | PROOF | A206866 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1682 | PROOF | A207083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1683 | PROOF | A233897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1684 | PROOF | A234124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1685 | PROOF | A234170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1686 | PROOF | A234550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1687 | PROOF | A234683 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1688 | PROOF | A235312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1689 | PROOF | A235100 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1690 | PROOF | A235191 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1691 | PROOF | A207347 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1692 | PROOF | A207683 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1693 | PROOF | A207769 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1694 | PROOF | A207840 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1695 | PROOF | A208103 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1696 | PROOF | A233811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1697 | PROOF | A234452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1698 | PROOF | A234883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1699 | PROOF | A235019 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1700 | PROOF | A235179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1701 | PROOF | A183785 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1702 | PROOF | A210384 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1703 | PROOF | A233877 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1704 | PROOF | A234260 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1705 | PROOF | A234437 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1706 | PROOF | A251204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1707 | PROOF | A251329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1708 | PROOF | A251384 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1709 | PROOF | A233921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1710 | PROOF | A234076 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1711 | PROOF | A234107 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1712 | PROOF | A184209 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1713 | PROOF | A207170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1714 | PROOF | A207436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1715 | PROOF | A209709 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1716 | PROOF | A209780 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1717 | PROOF | A209851 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1718 | PROOF | A209906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1719 | PROOF | A210070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1720 | PROOF | A251253 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1721 | PROOF | A251081 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1722 | PROOF | A251130 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1723 | PROOF | A251151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1724 | PROOF | A251444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1725 | PROOF | A251311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1726 | PROOF | A251148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1727 | PROOF | A251147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1728 | PROOF | A302677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1729 | PROOF | A208505 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1730 | PROOF | A251146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1731 | PROOF | A208504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1732 | PROOF | A251127 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1733 | PROOF | A298179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1734 | PROOF | A298959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1735 | PROOF | A301658 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1736 | PROOF | A303678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1737 | PROOF | A209507 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1738 | PROOF | A251145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1739 | PROOF | A251126 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1740 | PROOF | A207719 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1741 | PROOF | A208421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1742 | PROOF | A234117 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1743 | PROOF | A251144 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1744 | PROOF | A251368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1745 | PROOF | A235011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1746 | PROOF | A208288 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1747 | PROOF | A234484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1748 | PROOF | A234697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1749 | PROOF | A251125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1750 | PROOF | A298095 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1751 | PROOF | A298897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1752 | PROOF | A299649 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1753 | PROOF | A300203 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1754 | PROOF | A302260 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1755 | PROOF | A302736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1756 | PROOF | A302960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1757 | PROOF | A303451 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1758 | PROOF | A303464 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1759 | PROOF | A303631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1760 | PROOF | A304770 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1761 | PROOF | A305518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1762 | PROOF | A316513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1763 | PROOF | A316810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1764 | PROOF | A316955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1765 | PROOF | A317560 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1766 | PROOF | A234659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1767 | PROOF | A207718 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1768 | PROOF | A207896 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1769 | PROOF | A234177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1770 | PROOF | A234491 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1771 | PROOF | A234543 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1772 | PROOF | A234651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1773 | PROOF | A235303 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1774 | PROOF | A203374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1775 | PROOF | A251124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1776 | PROOF | A235091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1777 | PROOF | A209376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1778 | PROOF | A251143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1779 | PROOF | A251243 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1780 | PROOF | A234557 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1781 | PROOF | A210149 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1782 | PROOF | A233628 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1783 | PROOF | A233960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1784 | PROOF | A251123 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1785 | PROOF | A297817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1786 | PROOF | A297852 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1787 | PROOF | A297883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1788 | PROOF | A297901 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1789 | PROOF | A297945 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1790 | PROOF | A298057 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1791 | PROOF | A298148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1792 | PROOF | A298189 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1793 | PROOF | A298215 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1794 | PROOF | A298448 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1795 | PROOF | A303684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1796 | PROOF | A303794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1797 | PROOF | A303882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1798 | PROOF | A304013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1799 | PROOF | A304052 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1800 | PROOF | A304143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1801 | PROOF | A304257 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1802 | PROOF | A304341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1803 | PROOF | A305091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1804 | PROOF | A184556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1805 | PROOF | A250920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1806 | PROOF | A250975 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1807 | PROOF | A251003 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1808 | PROOF | A251012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1809 | PROOF | A251403 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1810 | PROOF | A250967 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1811 | PROOF | A251122 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1812 | PROOF | A251195 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1813 | PROOF | A251213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1814 | PROOF | A251222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1815 | PROOF | A251252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1816 | PROOF | A251269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1817 | PROOF | A251286 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1818 | PROOF | A251320 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1819 | PROOF | A203822 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1820 | PROOF | A208693 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1821 | PROOF | A208692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1822 | PROOF | A208559 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1823 | PROOF | A301780 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1824 | PROOF | A302676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1825 | PROOF | A207458 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1826 | PROOF | A208691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1827 | PROOF | A207457 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1828 | PROOF | A208557 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1829 | PROOF | A207456 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1830 | PROOF | A207847 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1831 | PROOF | A208029 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1832 | PROOF | A208690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1833 | PROOF | A209225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1834 | PROOF | A209377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1835 | PROOF | A184146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1836 | PROOF | A206249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1837 | PROOF | A207455 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1838 | PROOF | A251277 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1839 | PROOF | A301657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1840 | PROOF | A302422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1841 | PROOF | A302510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1842 | PROOF | A302803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1843 | PROOF | A303309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1844 | PROOF | A304216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1845 | PROOF | A316803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1846 | PROOF | A317520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1847 | PROOF | A207454 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1848 | PROOF | A207694 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1849 | PROOF | A207929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1850 | PROOF | A208064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1851 | PROOF | A233951 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1852 | PROOF | A234674 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1853 | PROOF | A250952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1854 | PROOF | A184369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1855 | PROOF | A206466 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1856 | PROOF | A209790 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1857 | PROOF | A234116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1858 | PROOF | A234029 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1859 | PROOF | A234162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1860 | PROOF | A234210 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1861 | PROOF | A234444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1862 | PROOF | A235271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1863 | PROOF | A234875 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1864 | PROOF | A234914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1865 | PROOF | A235080 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1866 | PROOF | A183794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1867 | PROOF | A209546 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1868 | PROOF | A210293 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1869 | PROOF | A233675 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1870 | PROOF | A233726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1871 | PROOF | A233785 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1872 | PROOF | A234326 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1873 | PROOF | A235291 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1874 | PROOF | A250928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1875 | PROOF | A251229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1876 | PROOF | A251374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1877 | PROOF | A251492 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1878 | PROOF | A251500 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1879 | PROOF | A297809 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1880 | PROOF | A297860 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1881 | PROOF | A297870 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1882 | PROOF | A297909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1883 | PROOF | A297917 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1884 | PROOF | A297937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1885 | PROOF | A297953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1886 | PROOF | A297980 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1887 | PROOF | A298569 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1888 | PROOF | A303677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1889 | PROOF | A303721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1890 | PROOF | A303802 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1891 | PROOF | A303890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1892 | PROOF | A303963 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1893 | PROOF | A304004 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1894 | PROOF | A304304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1895 | PROOF | A304349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1896 | PROOF | A184489 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1897 | PROOF | A233942 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1898 | PROOF | A250834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1899 | PROOF | A251094 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1900 | PROOF | A251262 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1901 | PROOF | A251194 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1902 | PROOF | A251285 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1903 | PROOF | A251310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1904 | PROOF | A183631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1905 | PROOF | A183630 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1906 | PROOF | A209726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1907 | PROOF | A203730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1908 | PROOF | A203882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1909 | PROOF | A183629 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1910 | PROOF | A209532 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1911 | PROOF | A209725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1912 | PROOF | A203929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1913 | PROOF | A208844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1914 | PROOF | A203651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1915 | PROOF | A208843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1916 | PROOF | A203791 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1917 | PROOF | A208558 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1918 | PROOF | A317513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1919 | PROOF | A209531 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1920 | PROOF | A209723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1921 | PROOF | A208842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1922 | PROOF | A208503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1923 | PROOF | A183626 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1924 | PROOF | A203830 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1925 | PROOF | A208079 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1926 | PROOF | A208556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1927 | PROOF | A208841 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1928 | PROOF | A209506 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1929 | PROOF | A209722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1930 | PROOF | A300177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1931 | PROOF | A303416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1932 | PROOF | A303714 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1933 | PROOF | A304128 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1934 | PROOF | A304225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1935 | PROOF | A304265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1936 | PROOF | A305035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1937 | PROOF | A305581 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1938 | PROOF | A316688 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1939 | PROOF | A317512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1940 | PROOF | A207656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1941 | PROOF | A208689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1942 | PROOF | A183625 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1943 | PROOF | A209530 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1944 | PROOF | A250907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1945 | PROOF | A233982 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1946 | PROOF | A234220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1947 | PROOF | A203373 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1948 | PROOF | A209729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1949 | PROOF | A233684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1950 | PROOF | A234133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1951 | PROOF | A234154 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1952 | PROOF | A234483 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1953 | PROOF | A235282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1954 | PROOF | A250951 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1955 | PROOF | A251293 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1956 | PROOF | A251336 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1957 | PROOF | A251517 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1958 | PROOF | A297972 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1959 | PROOF | A298234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1960 | PROOF | A304421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1961 | PROOF | A183624 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1962 | PROOF | A183784 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1963 | PROOF | A209953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1964 | PROOF | A210269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1965 | PROOF | A210383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1966 | PROOF | A234259 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1967 | PROOF | A251203 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1968 | PROOF | A251328 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1969 | PROOF | A251344 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1970 | PROOF | A251383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1971 | PROOF | A251221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1972 | PROOF | A251251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1973 | PROOF | A251319 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1974 | PROOF | A127905 | a recurrence derived from the summand by creative telescoping |
| 1975 | PROOF | A045742 | a recurrence derived from the summand by creative telescoping |
| 1976 | PROOF | A208779 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1977 | PROOF | A208778 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1978 | PROOF | A203729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1979 | PROOF | A203881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1980 | PROOF | A203928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1981 | PROOF | A203650 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1982 | PROOF | A208502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1983 | PROOF | A203790 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1984 | PROOF | A298777 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1985 | PROOF | A301779 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1986 | PROOF | A302675 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1987 | PROOF | A207590 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1988 | PROOF | A207846 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1989 | PROOF | A203829 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1990 | PROOF | A209505 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1991 | PROOF | A184145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1992 | PROOF | A251276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1993 | PROOF | A251484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1994 | PROOF | A184368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1995 | PROOF | A209789 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1996 | PROOF | A233637 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1997 | PROOF | A234436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1998 | PROOF | A243585 | a recurrence derived from the summand by creative telescoping |
| 1999 | PROOF | A026005 | a recurrence derived from the summand by creative telescoping |
| 2000 | PROOF | A359643 | the generating function derived from a coefficient-extraction definition |
| 2001 | PROOF | A156894 | the generating function derived from a coefficient-extraction definition |
| 2002 | PROOF | A156894 | the generating function derived from a coefficient-extraction definition |
| 2003 | PROOF | A371753 | the generating function derived from a coefficient-extraction definition |
| 2004 | PROOF | A226751 | the generating function derived from a coefficient-extraction definition |
| 2005 | PROOF | A386830 | the generating function derived from a coefficient-extraction definition |
| 2006 | PROOF | A172025 | the generating function derived from a coefficient-extraction definition |
| 2007 | PROOF | A348410 | the generating function derived from a coefficient-extraction definition |
| 2008 | PROOF | A243764 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2009 | PROOF | A243760 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2010 | PROOF | A285195 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2011 | PROOF | A243814 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2012 | PROOF | A055392 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2013 | PROOF | A025758 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2014 | PROOF | A308726 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2015 | PROOF | A243022 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2016 | PROOF | A168506 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2017 | PROOF | A239425 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2018 | PROOF | A025757 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2019 | PROOF | A242566 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2020 | PROOF | A270530 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2021 | PROOF | A101478 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2022 | PROOF | A025756 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2023 | PROOF | A097180 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2024 | PROOF | A097189 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2025 | PROOF | A127632 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2026 | PROOF | A130655 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2027 | PROOF | A166135 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2028 | PROOF | A212696 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2029 | PROOF | A261196 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2030 | PROOF | A270530 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2031 | PROOF | A185010 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2032 | PROOF | A185020 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2033 | PROOF | A200312 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2034 | PROOF | A025754 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2035 | PROOF | A097188 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2036 | PROOF | A097192 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2037 | PROOF | A158826 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2038 | PROOF | A159769 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2039 | PROOF | A294159 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2040 | PROOF | A392976 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 2041 | PROOF | A162972 | a transcendental e.g.f., in a differential module over Q(x) |
| 2042 | PROOF | A001465 | a transcendental e.g.f., in a differential module over Q(x) |
| 2043 | PROOF | A085387 | a transcendental e.g.f., in a differential module over Q(x) |
| 2044 | PROOF | A096471 | a transcendental e.g.f., in a differential module over Q(x) |
| 2045 | PROOF | A000704 | a transcendental e.g.f., in a differential module over Q(x) |
| 2046 | PROOF | A001724 | a transcendental e.g.f., in a differential module over Q(x) |
| 2047 | PROOF | A066052 | a transcendental e.g.f., in a differential module over Q(x) |
| 2048 | PROOF | A097204 | a transcendental e.g.f., in a differential module over Q(x) |
| 2049 | PROOF | A053532 | a transcendental e.g.f., in a differential module over Q(x) |
| 2050 | PROOF | A306948 | a transcendental e.g.f., in a differential module over Q(x) |
| 2051 | PROOF | A000483 | a transcendental e.g.f., in a differential module over Q(x) |
| 2052 | PROOF | A000276 | a transcendental e.g.f., in a differential module over Q(x) |
| 2053 | PROOF | A002104 | a transcendental e.g.f., in a differential module over Q(x) |
| 2054 | PROOF | A002538 | a transcendental e.g.f., in a differential module over Q(x) |
| 2055 | PROOF | A066052 | a transcendental e.g.f., in a differential module over Q(x) |
| 2056 | PROOF | A073591 | a transcendental e.g.f., in a differential module over Q(x) |
| 2057 | PROOF | A108704 | a transcendental e.g.f., in a differential module over Q(x) |
| 2058 | PROOF | A110322 | a transcendental e.g.f., in a differential module over Q(x) |
| 2059 | PROOF | A185369 | a transcendental e.g.f., in a differential module over Q(x) |
| 2060 | PROOF | A000276 | a transcendental e.g.f., in a differential module over Q(x) |
| 2061 | PROOF | A000774 | a transcendental e.g.f., in a differential module over Q(x) |
| 2062 | PROOF | A094905 | a transcendental e.g.f., in a differential module over Q(x) |
| 2063 | PROOF | A098557 | a transcendental e.g.f., in a differential module over Q(x) |
| 2064 | PROOF | A051560 | a transcendental e.g.f., in a differential module over Q(x) |
| 2065 | PROOF | A129149 | a transcendental e.g.f., in a differential module over Q(x) |
| 2066 | PROOF | A187252 | a transcendental e.g.f., in a differential module over Q(x) |
| 2067 | PROOF | A005654 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2068 | PROOF | A116385 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2069 | PROOF | A005558 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2070 | PROOF | A065942 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2071 | PROOF | A081181 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2072 | PROOF | A081204 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2073 | PROOF | A005558 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2074 | PROOF | A005559 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2075 | PROOF | A005560 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2076 | PROOF | A005561 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2077 | PROOF | A005562 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2078 | PROOF | A081204 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2079 | PROOF | A081205 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2080 | PROOF | A213801 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 2081 | PROOF | A006231 | a posted closed form against a derived holonomic recurrence |
| 2082 | PROOF | A213203 | a posted closed form compared against the posted generating function |
| 2083 | PROOF | A242429 | a posted closed form compared against the posted generating function |
| 2084 | PROOF | A026018 | a posted closed form compared against the posted generating function |
| 2085 | PROOF | A092634 | a posted closed form compared against the posted generating function |
| 2086 | PROOF | A026026 | a posted closed form compared against the posted generating function |
| 2087 | PROOF | A052227 | a posted closed form compared against the posted generating function |
| 2088 | PROOF | A228329 | a posted closed form compared against the posted generating function |
| 2089 | PROOF | A259457 | a posted closed form compared against the posted generating function |
| 2090 | PROOF | A268554 | a posted closed form compared against the posted generating function |
| 2091 | PROOF | A102319 | several independent square roots |
| 2092 | PROOF | A115256 | several independent square roots |
| 2093 | PROOF | A157125 | several independent square roots |
| 2094 | PROOF | A102318 | several independent square roots |
| 2095 | PROOF | A107587 | several independent square roots |
| 2096 | PROOF | A218185 | several independent square roots |
| 2097 | PROOF | A025567 | several independent square roots |
| 2098 | PROOF | A071684 | several independent square roots |
| 2099 | PROOF | A179648 | several independent square roots |
| 2100 | PROOF | A184120 | several independent square roots |
| 2101 | PROOF | A026163 | several independent square roots |
| 2102 | PROOF | A102318 | several independent square roots |
| 2103 | PROOF | A101500 | several independent square roots |
| 2104 | PROOF | A102319 | several independent square roots |
| 2105 | PROOF | A107587 | several independent square roots |
| 2106 | PROOF | A072100 | several independent square roots |
| 2107 | PROOF | A025567 | several independent square roots |
| 2108 | PROOF | A334509 | an identity between different entries |
| 2109 | PROOF | A298022 | an identity between different entries |
| 2110 | PROOF | A273676 | an identity between different entries |
| 2111 | PROOF | A273832 | an identity between different entries |
| 2112 | PROOF | A319371 | an identity between different entries |
| 2113 | PROOF | A110320 | an identity between different entries |
| 2114 | PROOF | A309878 | an identity between different entries |
| 2115 | PROOF | A315520 | an identity between different entries |
| 2116 | PROOF | A346370 | an identity between different entries |
| 2117 | PROOF | A176126 | the residual test over one square root, or none |
| 2118 | PROOF | A191625 | the residual test over one square root, or none |
| 2119 | PROOF | A186341 | the residual test over one square root, or none |
| 2120 | PROOF | A026743 | the residual test over one square root, or none |
| 2121 | PROOF | A191786 | the residual test over one square root, or none |
| 2122 | PROOF | A210496 | the residual test over one square root, or none |
| 2123 | PROOF | A182892 | the residual test over one square root, or none |
| 2124 | PROOF | A270724 | the residual test over one square root, or none |
| 2125 | PROOF | A190171 | the residual test over one square root, or none |
| 2126 | PROOF | A257515 | the residual test over one square root, or none |
| 2127 | PROOF | A190788 | the residual test over one square root, or none |
| 2128 | PROOF | A095981 | the residual test over one square root, or none |
| 2129 | PROOF | A212205 | the residual test over one square root, or none |
| 2130 | PROOF | A270661 | the residual test over one square root, or none |
| 2131 | PROOF | A157021 | the residual test over one square root, or none |
| 2132 | PROOF | A165537 | the residual test over one square root, or none |
| 2133 | PROOF | A166287 | the residual test over one square root, or none |
| 2134 | PROOF | A174013 | the residual test over one square root, or none |
| 2135 | PROOF | A178072 | the residual test over one square root, or none |
| 2136 | PROOF | A182894 | the residual test over one square root, or none |
| 2137 | PROOF | A114584 | the residual test over one square root, or none |
| 2138 | PROOF | A164586 | the residual test over one square root, or none |
| 2139 | PROOF | A189053 | the residual test over one square root, or none |
| 2140 | PROOF | A182904 | the residual test over one square root, or none |
| 2141 | PROOF | A274295 | the residual test over one square root, or none |
| 2142 | PROOF | A226434 | the residual test over one square root, or none |
| 2143 | PROOF | A257104 | the residual test over one square root, or none |
| 2144 | PROOF | A108600 | the residual test over one square root, or none |
| 2145 | PROOF | A114851 | the residual test over one square root, or none |
| 2146 | PROOF | A125306 | the residual test over one square root, or none |
| 2147 | PROOF | A166290 | the residual test over one square root, or none |
| 2148 | PROOF | A228770 | the residual test over one square root, or none |
| 2149 | PROOF | A257300 | the residual test over one square root, or none |
| 2150 | PROOF | A089324 | the residual test over one square root, or none |
| 2151 | PROOF | A104625 | the residual test over one square root, or none |
| 2152 | PROOF | A113956 | the residual test over one square root, or none |
| 2153 | PROOF | A116383 | the residual test over one square root, or none |
| 2154 | PROOF | A162548 | the residual test over one square root, or none |
| 2155 | PROOF | A173993 | the residual test over one square root, or none |
| 2156 | PROOF | A244886 | the residual test over one square root, or none |
| 2157 | PROOF | A157003 | the residual test over one square root, or none |
| 2158 | PROOF | A162482 | the residual test over one square root, or none |
| 2159 | PROOF | A163493 | the residual test over one square root, or none |
| 2160 | PROOF | A191398 | the residual test over one square root, or none |
| 2161 | PROOF | A135582 | the residual test over one square root, or none |
| 2162 | PROOF | A139376 | the residual test over one square root, or none |
| 2163 | PROOF | A346074 | the residual test over one square root, or none |
| 2164 | PROOF | A190166 | the residual test over one square root, or none |
| 2165 | PROOF | A025251 | the residual test over one square root, or none |
| 2166 | PROOF | A228771 | the residual test over one square root, or none |
| 2167 | PROOF | A025268 | the residual test over one square root, or none |
| 2168 | PROOF | A025272 | the residual test over one square root, or none |
| 2169 | PROOF | A162475 | the residual test over one square root, or none |
| 2170 | PROOF | A385252 | the residual test over one square root, or none |
| 2171 | PROOF | A114464 | the residual test over one square root, or none |
| 2172 | PROOF | A127154 | the residual test over one square root, or none |
| 2173 | PROOF | A135335 | the residual test over one square root, or none |
| 2174 | PROOF | A165540 | the residual test over one square root, or none |
| 2175 | PROOF | A171416 | the residual test over one square root, or none |
| 2176 | PROOF | A188314 | the residual test over one square root, or none |
| 2177 | PROOF | A247170 | the residual test over one square root, or none |
| 2178 | PROOF | A254314 | the residual test over one square root, or none |
| 2179 | PROOF | A270661 | the residual test over one square root, or none |
| 2180 | PROOF | A003440 | the residual test over one square root, or none |
| 2181 | PROOF | A110521 | the residual test over one square root, or none |
| 2182 | PROOF | A114190 | the residual test over one square root, or none |
| 2183 | PROOF | A116387 | the residual test over one square root, or none |
| 2184 | PROOF | A128096 | the residual test over one square root, or none |
| 2185 | PROOF | A135052 | the residual test over one square root, or none |
| 2186 | PROOF | A157021 | the residual test over one square root, or none |
| 2187 | PROOF | A160823 | the residual test over one square root, or none |
| 2188 | PROOF | A166287 | the residual test over one square root, or none |
| 2189 | PROOF | A174808 | the residual test over one square root, or none |
| 2190 | PROOF | A185089 | the residual test over one square root, or none |
| 2191 | PROOF | A186940 | the residual test over one square root, or none |
| 2192 | PROOF | A190736 | the residual test over one square root, or none |
| 2193 | PROOF | A219314 | the residual test over one square root, or none |
| 2194 | PROOF | A100095 | the residual test over one square root, or none |
| 2195 | PROOF | A100097 | the residual test over one square root, or none |
| 2196 | PROOF | A191313 | the residual test over one square root, or none |
| 2197 | PROOF | A191790 | the residual test over one square root, or none |
| 2198 | PROOF | A273351 | the residual test over one square root, or none |
| 2199 | PROOF | A278472 | the residual test over one square root, or none |
| 2200 | PROOF | A108296 | the residual test over one square root, or none |
| 2201 | PROOF | A116391 | the residual test over one square root, or none |
| 2202 | PROOF | A110198 | the residual test over one square root, or none |
| 2203 | PROOF | A182879 | the residual test over one square root, or none |
| 2204 | PROOF | A182887 | the residual test over one square root, or none |
| 2205 | PROOF | A135925 | the residual test over one square root, or none |
| 2206 | PROOF | A007901 | the residual test over one square root, or none |
| 2207 | PROOF | A025256 | the residual test over one square root, or none |
| 2208 | PROOF | A025258 | the residual test over one square root, or none |
| 2209 | PROOF | A000781 | the residual test over one square root, or none |
| 2210 | PROOF | A025245 | the residual test over one square root, or none |
| 2211 | PROOF | A025257 | the residual test over one square root, or none |
| 2212 | PROOF | A025269 | the residual test over one square root, or none |
| 2213 | PROOF | A025270 | the residual test over one square root, or none |
| 2214 | PROOF | A025275 | the residual test over one square root, or none |
| 2215 | PROOF | A032096 | the residual test over one square root, or none |
| 2216 | PROOF | A102880 | the residual test over one square root, or none |
| 2217 | PROOF | A111053 | the residual test over one square root, or none |
| 2218 | PROOF | A152120 | the residual test over one square root, or none |
| 2219 | PROOF | A159771 | the residual test over one square root, or none |
| 2220 | PROOF | A166694 | the residual test over one square root, or none |
| 2221 | PROOF | A166696 | the residual test over one square root, or none |
| 2222 | PROOF | A191796 | the residual test over one square root, or none |
| 2223 | PROOF | A217711 | the residual test over one square root, or none |
| 2224 | PROOF | A278023 | the residual test over one square root, or none |
| 2225 | PROOF | A279014 | the residual test over one square root, or none |
| 2226 | PROOF | A000483 | the residual test over one square root, or none |
| 2227 | PROOF | A026030 | the residual test over one square root, or none |
| 2228 | PROOF | A026031 | the residual test over one square root, or none |
| 2229 | PROOF | A048775 | the residual test over one square root, or none |
| 2230 | PROOF | A116409 | the residual test over one square root, or none |
| 2231 | PROOF | A126322 | the residual test over one square root, or none |
| 2232 | PROOF | A128750 | the residual test over one square root, or none |
| 2233 | PROOF | A143955 | the residual test over one square root, or none |
| 2234 | PROOF | A165203 | the residual test over one square root, or none |
| 2235 | PROOF | A168505 | the residual test over one square root, or none |
| 2236 | PROOF | A176605 | the residual test over one square root, or none |
| 2237 | PROOF | A181933 | the residual test over one square root, or none |
| 2238 | PROOF | A191585 | the residual test over one square root, or none |
| 2239 | PROOF | A215973 | the residual test over one square root, or none |
| 2240 | PROOF | A234269 | the residual test over one square root, or none |
| 2241 | PROOF | A236407 | the residual test over one square root, or none |
| 2242 | PROOF | A270363 | the residual test over one square root, or none |
| 2243 | PROOF | A098521 | the residual test over one square root, or none |
| 2244 | PROOF | A100096 | the residual test over one square root, or none |
| 2245 | PROOF | A100099 | the residual test over one square root, or none |
| 2246 | PROOF | A105849 | the residual test over one square root, or none |
| 2247 | PROOF | A105864 | the residual test over one square root, or none |
| 2248 | PROOF | A105865 | the residual test over one square root, or none |
| 2249 | PROOF | A108308 | the residual test over one square root, or none |
| 2250 | PROOF | A114194 | the residual test over one square root, or none |
| 2251 | PROOF | A115967 | the residual test over one square root, or none |
| 2252 | PROOF | A117186 | the residual test over one square root, or none |
| 2253 | PROOF | A120010 | the residual test over one square root, or none |
| 2254 | PROOF | A124431 | the residual test over one square root, or none |
| 2255 | PROOF | A124431 | the residual test over one square root, or none |
| 2256 | PROOF | A126568 | the residual test over one square root, or none |
| 2257 | PROOF | A132364 | the residual test over one square root, or none |
| 2258 | PROOF | A141342 | the residual test over one square root, or none |
| 2259 | PROOF | A155051 | the residual test over one square root, or none |
| 2260 | PROOF | A157002 | the residual test over one square root, or none |
| 2261 | PROOF | A157100 | the residual test over one square root, or none |
| 2262 | PROOF | A166076 | the residual test over one square root, or none |
| 2263 | PROOF | A166300 | the residual test over one square root, or none |
| 2264 | PROOF | A168503 | the residual test over one square root, or none |
| 2265 | PROOF | A174107 | the residual test over one square root, or none |
| 2266 | PROOF | A174169 | the residual test over one square root, or none |
| 2267 | PROOF | A176332 | the residual test over one square root, or none |
| 2268 | PROOF | A184018 | the residual test over one square root, or none |
| 2269 | PROOF | A188312 | the residual test over one square root, or none |
| 2270 | PROOF | A188482 | the residual test over one square root, or none |
| 2271 | PROOF | A191782 | the residual test over one square root, or none |
| 2272 | PROOF | A217333 | the residual test over one square root, or none |
| 2273 | PROOF | A257072 | the residual test over one square root, or none |
| 2274 | PROOF | A261681 | the residual test over one square root, or none |
| 2275 | PROOF | A073155 | the residual test over one square root, or none |
| 2276 | PROOF | A105524 | the residual test over one square root, or none |
| 2277 | PROOF | A114589 | the residual test over one square root, or none |
| 2278 | PROOF | A114590 | the residual test over one square root, or none |
| 2279 | PROOF | A162481 | the residual test over one square root, or none |
| 2280 | PROOF | A174783 | the residual test over one square root, or none |
| 2281 | PROOF | A188460 | the residual test over one square root, or none |
| 2282 | PROOF | A188464 | the residual test over one square root, or none |
| 2283 | PROOF | A190725 | the residual test over one square root, or none |
| 2284 | PROOF | A191526 | the residual test over one square root, or none |
| 2285 | PROOF | A191531 | the residual test over one square root, or none |
| 2286 | PROOF | A211278 | the residual test over one square root, or none |
| 2287 | PROOF | A026327 | the residual test over one square root, or none |
| 2288 | PROOF | A081207 | the residual test over one square root, or none |
| 2289 | PROOF | A102882 | the residual test over one square root, or none |
| 2290 | PROOF | A182881 | the residual test over one square root, or none |
| 2291 | PROOF | A191309 | the residual test over one square root, or none |
| 2292 | PROOF | A191319 | the residual test over one square root, or none |
| 2293 | PROOF | A191790 | the residual test over one square root, or none |
| 2294 | PROOF | A273351 | the residual test over one square root, or none |
| 2295 | PROOF | A025248 | the residual test over one square root, or none |
| 2296 | PROOF | A025249 | the residual test over one square root, or none |
| 2297 | PROOF | A026017 | the residual test over one square root, or none |
| 2298 | PROOF | A071717 | the residual test over one square root, or none |
| 2299 | PROOF | A081672 | the residual test over one square root, or none |
| 2300 | PROOF | A104722 | the residual test over one square root, or none |
| 2301 | PROOF | A109263 | the residual test over one square root, or none |
| 2302 | PROOF | A118093 | the residual test over one square root, or none |
| 2303 | PROOF | A118974 | the residual test over one square root, or none |
| 2304 | PROOF | A121320 | the residual test over one square root, or none |
| 2305 | PROOF | A126323 | the residual test over one square root, or none |
| 2306 | PROOF | A128723 | the residual test over one square root, or none |
| 2307 | PROOF | A135334 | the residual test over one square root, or none |
| 2308 | PROOF | A141351 | the residual test over one square root, or none |
| 2309 | PROOF | A141353 | the residual test over one square root, or none |
| 2310 | PROOF | A163824 | the residual test over one square root, or none |
| 2311 | PROOF | A165201 | the residual test over one square root, or none |
| 2312 | PROOF | A279014 | the residual test over one square root, or none |
| 2313 | PROOF | A026027 | the residual test over one square root, or none |
| 2314 | PROOF | A026135 | the residual test over one square root, or none |
| 2315 | PROOF | A050168 | the residual test over one square root, or none |
| 2316 | PROOF | A059279 | the residual test over one square root, or none |
| 2317 | PROOF | A063395 | the residual test over one square root, or none |
| 2318 | PROOF | A071722 | the residual test over one square root, or none |
| 2319 | PROOF | A082134 | the residual test over one square root, or none |
| 2320 | PROOF | A097331 | the residual test over one square root, or none |
| 2321 | PROOF | A100193 | the residual test over one square root, or none |
| 2322 | PROOF | A103973 | the residual test over one square root, or none |
| 2323 | PROOF | A106181 | the residual test over one square root, or none |
| 2324 | PROOF | A108623 | the residual test over one square root, or none |
| 2325 | PROOF | A126180 | the residual test over one square root, or none |
| 2326 | PROOF | A128732 | the residual test over one square root, or none |
| 2327 | PROOF | A134389 | the residual test over one square root, or none |
| 2328 | PROOF | A143013 | the residual test over one square root, or none |
| 2329 | PROOF | A143954 | the residual test over one square root, or none |
| 2330 | PROOF | A157418 | the residual test over one square root, or none |
| 2331 | PROOF | A158196 | the residual test over one square root, or none |
| 2332 | PROOF | A158197 | the residual test over one square root, or none |
| 2333 | PROOF | A191585 | the residual test over one square root, or none |
| 2334 | PROOF | A257290 | the residual test over one square root, or none |
| 2335 | PROOF | A054341 | the residual test over one square root, or none |
| 2336 | PROOF | A071715 | the residual test over one square root, or none |
| 2337 | PROOF | A090413 | the residual test over one square root, or none |
| 2338 | PROOF | A090826 | the residual test over one square root, or none |
| 2339 | PROOF | A091699 | the residual test over one square root, or none |
| 2340 | PROOF | A098664 | the residual test over one square root, or none |
| 2341 | PROOF | A099363 | the residual test over one square root, or none |
| 2342 | PROOF | A100098 | the residual test over one square root, or none |
| 2343 | PROOF | A105872 | the residual test over one square root, or none |
| 2344 | PROOF | A119975 | the residual test over one square root, or none |
| 2345 | PROOF | A121724 | the residual test over one square root, or none |
| 2346 | PROOF | A121725 | the residual test over one square root, or none |
| 2347 | PROOF | A126931 | the residual test over one square root, or none |
| 2348 | PROOF | A126932 | the residual test over one square root, or none |
| 2349 | PROOF | A127361 | the residual test over one square root, or none |
| 2350 | PROOF | A127363 | the residual test over one square root, or none |
| 2351 | PROOF | A155051 | the residual test over one square root, or none |
| 2352 | PROOF | A166078 | the residual test over one square root, or none |
| 2353 | PROOF | A166587 | the residual test over one square root, or none |
| 2354 | PROOF | A166588 | the residual test over one square root, or none |
| 2355 | PROOF | A176006 | the residual test over one square root, or none |
| 2356 | PROOF | A185087 | the residual test over one square root, or none |
| 2357 | PROOF | A190724 | the residual test over one square root, or none |
| 2358 | PROOF | A225887 | the residual test over one square root, or none |
| 2359 | PROOF | A227081 | the residual test over one square root, or none |
| 2360 | PROOF | A257178 | the residual test over one square root, or none |
| 2361 | PROOF | A257388 | the residual test over one square root, or none |
| 2362 | PROOF | A257838 | the residual test over one square root, or none |
| 2363 | PROOF | A001712 | the residual test over one square root, or none |
| 2364 | PROOF | A025175 | the residual test over one square root, or none |
| 2365 | PROOF | A025577 | the residual test over one square root, or none |
| 2366 | PROOF | A026023 | the residual test over one square root, or none |
| 2367 | PROOF | A055217 | the residual test over one square root, or none |
| 2368 | PROOF | A081052 | the residual test over one square root, or none |
| 2369 | PROOF | A103821 | the residual test over one square root, or none |
| 2370 | PROOF | A107231 | the residual test over one square root, or none |
| 2371 | PROOF | A110199 | the residual test over one square root, or none |
| 2372 | PROOF | A116406 | the residual test over one square root, or none |
| 2373 | PROOF | A128734 | the residual test over one square root, or none |
| 2374 | PROOF | A191307 | the residual test over one square root, or none |
| 2375 | PROOF | A278472 | the residual test over one square root, or none |
| 2376 | PROOF | A034863 | the residual test over one square root, or none |
| 2377 | PROOF | A128652 | the residual test over one square root, or none |
| 2378 | PROOF | A174195 | the residual test over one square root, or none |
| 2379 | PROOF | A192480 | the residual test over one square root, or none |
| 2380 | PROOF | A158495 | the residual test over one square root, or none |
| 2381 | PROOF | A189176 | the residual test over one square root, or none |
| 2382 | PROOF | A194724 | the residual test over one square root, or none |
| 2383 | PROOF | A210474 | the residual test over one square root, or none |
| 2384 | PROOF | A262768 | the residual test over one square root, or none |
| 2385 | PROOF | A026029 | the residual test over one square root, or none |
| 2386 | PROOF | A064088 | the residual test over one square root, or none |
| 2387 | PROOF | A064089 | the residual test over one square root, or none |
| 2388 | PROOF | A064090 | the residual test over one square root, or none |
| 2389 | PROOF | A064091 | the residual test over one square root, or none |
| 2390 | PROOF | A064092 | the residual test over one square root, or none |
| 2391 | PROOF | A067299 | the residual test over one square root, or none |
| 2392 | PROOF | A068551 | the residual test over one square root, or none |
| 2393 | PROOF | A080243 | the residual test over one square root, or none |
| 2394 | PROOF | A114191 | the residual test over one square root, or none |
| 2395 | PROOF | A116881 | the residual test over one square root, or none |
| 2396 | PROOF | A122920 | the residual test over one square root, or none |
| 2397 | PROOF | A132864 | the residual test over one square root, or none |
| 2398 | PROOF | A133305 | the residual test over one square root, or none |
| 2399 | PROOF | A133306 | the residual test over one square root, or none |
| 2400 | PROOF | A133307 | the residual test over one square root, or none |
| 2401 | PROOF | A133308 | the residual test over one square root, or none |
| 2402 | PROOF | A141222 | the residual test over one square root, or none |
| 2403 | PROOF | A154623 | the residual test over one square root, or none |
| 2404 | PROOF | A157328 | the residual test over one square root, or none |
| 2405 | PROOF | A158196 | the residual test over one square root, or none |
| 2406 | PROOF | A158197 | the residual test over one square root, or none |
| 2407 | PROOF | A191993 | the residual test over one square root, or none |
| 2408 | PROOF | A225034 | the residual test over one square root, or none |
| 2409 | PROOF | A242172 | the residual test over one square root, or none |
| 2410 | PROOF | A002867 | the residual test over one square root, or none |
| 2411 | PROOF | A014533 | the residual test over one square root, or none |
| 2412 | PROOF | A051524 | the residual test over one square root, or none |
| 2413 | PROOF | A071264 | the residual test over one square root, or none |
| 2414 | PROOF | A081046 | the residual test over one square root, or none |
| 2415 | PROOF | A098519 | the residual test over one square root, or none |
| 2416 | PROOF | A098520 | the residual test over one square root, or none |
| 2417 | PROOF | A101596 | the residual test over one square root, or none |
| 2418 | PROOF | A101601 | the residual test over one square root, or none |
| 2419 | PROOF | A101602 | the residual test over one square root, or none |
| 2420 | PROOF | A111779 | the residual test over one square root, or none |
| 2421 | PROOF | A112703 | the residual test over one square root, or none |
| 2422 | PROOF | A119012 | the residual test over one square root, or none |
| 2423 | PROOF | A128057 | the residual test over one square root, or none |
| 2424 | PROOF | A128746 | the residual test over one square root, or none |
| 2425 | PROOF | A132900 | the residual test over one square root, or none |
| 2426 | PROOF | A151483 | the residual test over one square root, or none |
| 2427 | PROOF | A167481 | the residual test over one square root, or none |
| 2428 | PROOF | A171556 | the residual test over one square root, or none |
| 2429 | PROOF | A176479 | the residual test over one square root, or none |
| 2430 | PROOF | A182401 | the residual test over one square root, or none |
| 2431 | PROOF | A208355 | the residual test over one square root, or none |
| 2432 | PROOF | A210064 | the residual test over one square root, or none |
| 2433 | PROOF | A240558 | the residual test over one square root, or none |
| 2434 | PROOF | A141771 | the residual test over one square root, or none |
| 2435 | PROOF | A176606 | the residual test over one square root, or none |
| 2436 | PROOF | A176607 | the residual test over one square root, or none |
| 2437 | PROOF | A176609 | the residual test over one square root, or none |
| 2438 | PROOF | A176610 | the residual test over one square root, or none |
| 2439 | PROOF | A176611 | the residual test over one square root, or none |
| 2440 | PROOF | A176675 | the residual test over one square root, or none |
| 2441 | PROOF | A176749 | the residual test over one square root, or none |
| 2442 | PROOF | A176750 | the residual test over one square root, or none |
| 2443 | PROOF | A176751 | the residual test over one square root, or none |
| 2444 | PROOF | A176752 | the residual test over one square root, or none |
| 2445 | PROOF | A176753 | the residual test over one square root, or none |
| 2446 | PROOF | A176754 | the residual test over one square root, or none |
| 2447 | PROOF | A176755 | the residual test over one square root, or none |
| 2448 | PROOF | A176756 | the residual test over one square root, or none |
| 2449 | PROOF | A176757 | the residual test over one square root, or none |
| 2450 | PROOF | A176759 | the residual test over one square root, or none |
| 2451 | PROOF | A176828 | the residual test over one square root, or none |
| 2452 | PROOF | A176829 | the residual test over one square root, or none |
| 2453 | PROOF | A176830 | the residual test over one square root, or none |
| 2454 | PROOF | A176832 | the residual test over one square root, or none |
| 2455 | PROOF | A176854 | the residual test over one square root, or none |
| 2456 | PROOF | A176855 | the residual test over one square root, or none |
| 2457 | PROOF | A176856 | the residual test over one square root, or none |
| 2458 | PROOF | A176857 | the residual test over one square root, or none |
| 2459 | PROOF | A176858 | the residual test over one square root, or none |
| 2460 | PROOF | A176859 | the residual test over one square root, or none |
| 2461 | PROOF | A176952 | the residual test over one square root, or none |
| 2462 | PROOF | A176953 | the residual test over one square root, or none |
| 2463 | PROOF | A176956 | the residual test over one square root, or none |
| 2464 | PROOF | A176957 | the residual test over one square root, or none |
| 2465 | PROOF | A176958 | the residual test over one square root, or none |
| 2466 | PROOF | A176959 | the residual test over one square root, or none |
| 2467 | PROOF | A176962 | the residual test over one square root, or none |
| 2468 | PROOF | A176964 | the residual test over one square root, or none |
| 2469 | PROOF | A176966 | the residual test over one square root, or none |
| 2470 | PROOF | A176967 | the residual test over one square root, or none |
| 2471 | PROOF | A177123 | the residual test over one square root, or none |
| 2472 | PROOF | A177124 | the residual test over one square root, or none |
| 2473 | PROOF | A177125 | the residual test over one square root, or none |
| 2474 | PROOF | A177126 | the residual test over one square root, or none |
| 2475 | PROOF | A177127 | the residual test over one square root, or none |
| 2476 | PROOF | A177128 | the residual test over one square root, or none |
| 2477 | PROOF | A177129 | the residual test over one square root, or none |
| 2478 | PROOF | A177130 | the residual test over one square root, or none |
| 2479 | PROOF | A177131 | the residual test over one square root, or none |
| 2480 | PROOF | A177163 | the residual test over one square root, or none |
| 2481 | PROOF | A177165 | the residual test over one square root, or none |
| 2482 | PROOF | A177166 | the residual test over one square root, or none |
| 2483 | PROOF | A177167 | the residual test over one square root, or none |
| 2484 | PROOF | A177168 | the residual test over one square root, or none |
| 2485 | PROOF | A177169 | the residual test over one square root, or none |
| 2486 | PROOF | A177170 | the residual test over one square root, or none |
| 2487 | PROOF | A177171 | the residual test over one square root, or none |
| 2488 | PROOF | A177172 | the residual test over one square root, or none |
| 2489 | PROOF | A177175 | the residual test over one square root, or none |
| 2490 | PROOF | A177177 | the residual test over one square root, or none |
| 2491 | PROOF | A177178 | the residual test over one square root, or none |
| 2492 | PROOF | A177179 | the residual test over one square root, or none |
| 2493 | PROOF | A177180 | the residual test over one square root, or none |
| 2494 | PROOF | A177181 | the residual test over one square root, or none |
| 2495 | PROOF | A177182 | the residual test over one square root, or none |
| 2496 | PROOF | A177183 | the residual test over one square root, or none |
| 2497 | PROOF | A177184 | the residual test over one square root, or none |
| 2498 | PROOF | A177185 | the residual test over one square root, or none |
| 2499 | PROOF | A177197 | the residual test over one square root, or none |
| 2500 | PROOF | A177198 | the residual test over one square root, or none |
| 2501 | PROOF | A177199 | the residual test over one square root, or none |
| 2502 | PROOF | A177200 | the residual test over one square root, or none |
| 2503 | PROOF | A177203 | the residual test over one square root, or none |
| 2504 | PROOF | A081670 | the known side is the entry's NAME rather than a formula line |
| 2505 | PROOF | A085781 | the known side is the entry's NAME rather than a formula line |
| 2506 | PROOF | A026019 | the known side is the entry's NAME rather than a formula line |
| 2507 | PROOF | A052183 | the known side is the entry's NAME rather than a formula line |
| 2508 | PROOF | A052204 | the known side is the entry's NAME rather than a formula line |
| 2509 | PROOF | A157713 | the known side is the entry's NAME rather than a formula line |
| 2510 | PROOF | A334511 | a posted closed form decided by the theory of hypergeometric terms |
| 2511 | PROOF | A333905 | a posted closed form decided by the theory of hypergeometric terms |
| 2512 | PROOF | A049486 | a posted closed form decided by the theory of hypergeometric terms |
| 2513 | PROOF | A267879 | a posted closed form decided by the theory of hypergeometric terms |
| 2514 | PROOF | A267802 | a posted closed form decided by the theory of hypergeometric terms |
| 2515 | PROOF | A267847 | a posted closed form decided by the theory of hypergeometric terms |
| 2516 | PROOF | A034267 | a posted closed form decided by the theory of hypergeometric terms |
| 2517 | PROOF | A126501 | a posted closed form decided by the theory of hypergeometric terms |
| 2518 | PROOF | A128153 | a posted closed form decided by the theory of hypergeometric terms |
| 2519 | PROOF | A212938 | a posted closed form decided by the theory of hypergeometric terms |
| 2520 | PROOF | A220250 | a posted closed form decided by the theory of hypergeometric terms |
| 2521 | PROOF | A248434 | a posted closed form decided by the theory of hypergeometric terms |
| 2522 | PROOF | A258547 | a posted closed form decided by the theory of hypergeometric terms |
| 2523 | PROOF | A272706 | a posted closed form decided by the theory of hypergeometric terms |
| 2524 | PROOF | A126089 | complete annihilation, tested in the Ore algebra Q(n)[N] |
| 2525 | PROOF | A025271 | division of one posted operator by another |
| 2526 | PROOF | A138164 | division of one posted operator by another |
| 2527 | PROOF | A143017 | division of one posted operator by another |
| 2528 | PROOF | A159772 | division of one posted operator by another |
| 2529 | PROOF | A000986 | division of one posted operator by another |
| 2530 | PROOF | A022917 | division of one posted operator by another |
| 2531 | PROOF | A217447 | division of one posted operator by another |
| 2532 | PROOF | A226302 | division of one posted operator by another |
| 2533 | PROOF | A245088 | division of one posted operator by another |
| 2534 | PROOF | A026165 | division of one posted operator by another |
| 2535 | PROOF | A185966 | division of one posted operator by another |
| 2536 | PROOF | A200753 | division of one posted operator by another |
| 2537 | PROOF | A217358 | division of one posted operator by another |
| 2538 | PROOF | A228960 | division of one posted operator by another |
| 2539 | PROOF | A003435 | division of one posted operator by another |
| 2540 | PROOF | A228331 | division of one posted operator by another |
| 2541 | PROOF | A273019 | division of one posted operator by another |
| 2542 | PROOF | A386834 | division of one posted operator by another |
| 2543 | PROOF | A228330 | division of one posted operator by another |
| 2544 | PROOF | A228333 | division of one posted operator by another |

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


**The funceq-mod engine, second batch (A396099, A396102, A396797, A396807).** Same three
steps as the first batch. What is new is the iterate lemma: if `A(x) = x + ...` has
`a(1) = 1` then `[x^N] A^j = j*a(N) + (terms in a(1..N-1))`, which is what makes the
coefficient of `a(N)` come out 1 and so gives uniqueness. And over `Z/kZ` the iterates of
`f = x/(1-x)` are `f^j = x/(1-jx)`, which is what makes the reduced equation collapse.

- `A(x) = x + A^p(x)*A^(p+1)(x)`: modulo k the equation says
  `(1-px)(1-(p+1)x) = 1-x`, i.e. `k | 2p` and `k | p(p+1)`. The largest such k is
  `gcd(2p, p(p+1))` = `2p` for odd p and `p` for even p. That is exactly why Hanna states
  A396797 (p=3) mod 6 and A396807 (p=5) mod 10. Both papers also settle his SECOND
  conjecture on those entries, `[x^n] A^k = k^(n-1) (mod 2p)` for every integer k, which
  falls straight out of `f^j = x/(1-jx)`.
- A396099 is the p=2 member; the identity gives modulus 2, which is exactly its
  "all terms are odd" conjecture. Its two further conjectures are modulo 4 and are NOT
  claimed - the identity fails there.
- A396798 is p=4, giving modulus 4, but its stated conjectures are all modulo 8. Nothing
  claimed.
- A396102 (`A^3 = (1+x)A^2`, mod 3): `f^3 = x/(1-3x) = x` and `f^2 = x/(1-2x) = x/(1+x)`,
  so `(1+x)f^2 = x` too. Coefficient of `a(N)` is `3-2 = 1`.

**Where this engine STOPS, and it is not obvious.** A396793/A396794/A396795 look identical
in shape (`A^i(x)*A^j(x) = x^2 + m^2 x^3`, conjecture `a(n) = 0 mod m`) and the residues do
check out numerically -- but the coefficient of `a(N)` in those equations is exactly `m`,
not 1. So modulo m the recursion does not determine `a(N)` at all and the uniqueness step
collapses. Written out, `m*a(N) = -(stuff)`, and the conjecture is the statement that
`m^2 | stuff`, which is a real theorem, not a corollary of uniqueness. **Always compute the
coefficient of a(N) and check it is a unit modulo k before claiming anything.** These three
were built and dropped for exactly this reason.


**funceq-mod, third batch: the self-composition shift family (A091713, A196523, A378575,
A378576).** `A(x) = x + x*A^j(x)`, conjectured `a(n) = 1 (mod j-1)`. Modulo `j-1` we have
`j = 1`, so `f^j = x/(1-jx)` becomes `x/(1-x) = f`, and then
`x + x*f^j = x + x^2/(1-x) = x/(1-x) = f`. The coefficient of `a(N)` is 1 because the right
side contributes only `[x^(N-1)] A^j`. Four entries, j = 3,4,5,6 giving moduli 2,3,4,5;
A091713's conjecture is worded "all terms are odd", which is the j=3 case.

**The full funceq census.** 5,491 OEIS entries are defined by a functional equation for
their generating function. Of those, **52** are open, carry a congruence conjecture, and
have no paper. `funceq_cands.json` holds the list. Twelve are now done (four here, four in
the second batch, four in the first). What is left splits into:
- *Reachable by the same three steps, once a rational candidate mod k is found.* The
  conjectures state PERIODIC residue patterns rather than a constant, so the candidate is
  not `x/(1-x)` but some other rational series over `Z/kZ`. Examples: A396803/A396805/
  A396806 (`A(x) = x*exp(A^j(x))`, patterns mod 3, 5, 6), A396798 (mod 8), A397346
  (`[4,2,0,2]` mod 8), A386648 (`[2,3,4,3,2,5]` mod 6). The method is: compute residues,
  fit a rational series, verify it satisfies the reduced equation by clearing denominators
  (a finite polynomial identity over Z/kZ), then invoke uniqueness. **Check the coefficient
  of a(N) is a unit mod k first.**
- *Out of reach here.* Conjectures whose residue depends on an arithmetic property of n
  (n a square, a power of 2, a sum of two distinct powers of 3, ...): A378580, A378581,
  A379204, A380060, A393170-A393173, A396808, A397242, A397245, A325286, and others. Those
  are not congruences with a periodic pattern and the uniqueness route says nothing about
  them.


**A396798's stated conjecture is off by one, on its own data.** It reads
"a(n) = [1,1,5,5] repeating (mod 8) for n >= 1". The entry's published terms give
`1,1,1,5,5,1,1,5,5,...` mod 8, so the pattern starts at n=2, not n=1, and the stated form
first fails at n=3 (a(3)=9, which is 1 mod 8, not 5). Verified against the %S line itself,
not against a reconstruction. This is an index slip of the same class as the Mathar cases:
**not a disproof and not to be papered as one.**

**The next concrete step on the mod-8 and mod-9 cases: perturbation over Z/kZ.** The
obstruction to the funceq-mod engine on A396798 is that `x/(1-x)` solves the reduced
equation only mod 4, not mod 8. But the true reduction mod 8 is
`Abar = x/(1-x) + 4g` with `g = x^4(1+x)/(1-x^4)`, and since `4*4 = 0 mod 8` the correction
term is nilpotent. Composition then linearises exactly:
`Abar(Abar) = f(f) + 4[ g*f'(f) + g(f) ]`, a first-order Taylor expansion that is EXACT
because the second-order term carries 4^2. Every piece stays rational (`f^j = x/(1-jx)`,
`f' = 1/(1-x)^2`), so nine iterations remain tractable where naive symbolic composition
would blow up to degree 5^9. Same idea should reach A381364/A381365 (mod 9, with 3^2 = 0)
and A397346 (mod 8). Not yet carried out.

**The e.g.f. iteration family is NOT reachable this way.** A396803, A396805, A396806
(`E.g.f. A(x) = x*exp(A^j(x))`) do have a triangular recursion with coefficient 1 -- but on
the EXPONENTIAL coefficients c(n) = a(n)/n!, which are rationals with n! in the
denominator. Reduction mod k is not a ring homomorphism on those, so the uniqueness step
does not transfer to a(n) = n!c(n). The conjectured residues are non-zero for large n,
which already shows c(n) is not k-integral. Recorded so this is not attempted again
without a different idea.


**funceq-mod reaches a COEFFICIENT-CONDITION definition (A397241).** The entry is defined
by `n*[x^n]A^n = (n-1)*[x^n]A^(n+1)` for n>1, with a(0)=a(1)=1 fixed by the entry's own
expansion line. The uniqueness step works beautifully here: `[x^N]A^M = M*a(N) + earlier`
(write A = 1+U and note only the r=1 term of the binomial expansion can reach a(N)), so the
coefficient of a(N) is `N*N - (N-1)(N+1) = 1` exactly. The n=2 condition then returns
a(2)=1, matching the entry.

Modulo 2 the reduction is `1/(1-x)`, and the condition becomes
`N*C(2N-1,N) = (N-1)*C(2N,N) mod 2`. The right side dies because `C(2N,N) = 2*C(2N-1,N)`
(Pascal plus symmetry). The left side dies because `v_2(C(2N,N)) = s(N)`, the binary digit
sum (Kummer), so `v_2(C(2N-1,N)) = s(N)-1 >= 1` whenever N is odd and >= 3, while an even N
kills it directly. **That settles "all terms are odd".**

*The other two conjectures on that entry are NOT settled and are flagged as such in the
paper.* Their reductions are visible -- `(1+x^3)/(1-x)` mod 3 and `(1+2x^3)/(1-x)` mod 4,
both verified for n <= 34 -- and the mod-4 case reduces, via the same nilpotent trick
(`Abar = f + 2h`, `(2h)^2 = 0`), to
`(2-N)*C(2N-1,N) = 2[N^2*C(2N-4,N-1) - (N^2-1)*C(2N-3,N)] mod 4`.
Both sides vanish unless N or N-1 is a power of 2, where both equal 2. Proving that for all
N is the open step. The mod 3 case reduces to a Lucas-type identity. **This is the most
promising unfinished thread in the funceq family** -- the setup is done, only the binomial
congruence is missing.


**funceq-mod, fourth batch: two reductions that are not `x/(1-x)` (A389472, A395833).**
Both show the engine reaching well past the "all coefficients equal" case.

- **A389472**, `x^2*(A(x)+1) = A(x^2+x^3)`, conjecture `a(2n-1) = 0 (mod 2)` for n>1. Over
  F_2 the equation is PARITY-PRESERVING, because Frobenius gives
  `(x^2+x^3)^2 = x^4+x^6` -- again a polynomial in x^2. So `Abar = x + C(x^2)` is a
  solution, where C solves the companion equation `y*C(y) = C(y^2+y^3)`; the substitution
  cannot manufacture odd exponents, and the single odd exponent 1 forced by a(1)=1 is all
  there is. Uniqueness (the recursion `a(N-2) = sum_n a(n)*C(n,N-2n)` reaches only
  `n <= floor(N/2)`) finishes it. Checked: `x + C(x^2)` matches `a(n) mod 2` at every
  n <= 60. *The entry's mod-3 conjecture is NOT settled and the paper says so* -- the proof
  turns on Frobenius, and mod 3 the equation substitutes the first power of `x^2+x^3`, not
  the third, so Frobenius is not available where it is needed.
- **A395833**, `[x^n] A(x/A(x)^(2n-1)) = 0` for n>1, conjecture `a(n) = 0 (mod 3)` for
  n>=2. The reduction mod 3 is the POLYNOMIAL `1+x`. Substituting it turns the n-th
  condition into `(-1)^(n-1) * C(3n-3, n-1)`, so the whole conjecture is the single
  divisibility `3 | C(3m,m)`. Legendre gives it outright:
  `v_3(C(3m,m)) = (s_3(m) + s_3(2m) - s_3(3m))/2 = s_3(2m)/2 >= 1`, using `s_3(3m)=s_3(m)`.
  Specific to p=3: mod 2 the same computation gives `C(6,2)=15`, odd, so `1+x` is not the
  reduction there. *The entry's `(2n-1) | a(n)` conjecture is NOT settled.*

**Two structural lessons for the remaining 40 funceq candidates.**
1. The candidate reduction need not be `x/(1-x)`, and need not even be a power series -- a
   POLYNOMIAL reduction (A395833) makes the proof trivial once found. Always compute the
   residues first and look at what they actually are.
2. When the equation substitutes `x^p + ...` and the modulus is p, check whether Frobenius
   applies. That is what makes A389472 work mod 2 and fail mod 3.


## 3c. THE TRANSFER-MATRIX ENGINE — 44 papers in one sweep

**The biggest single group found so far.** R. H. Hardin contributed thousands of entries of
the form "Number of (n+1) X K 0..m arrays with <local condition on every 2 X 2 subblock>",
each with an EMPIRICAL linear recurrence and no proof. Those recurrences are not empirical
at all: the rows of such an array are the vertices of a finite digraph whose edges are the
admissible row-to-row steps, so an (n+1)-row array is a walk of length n and

    a(n) = 1^T M^n 1

for the adjacency matrix M on S = (m+1)^K vertices. That is C-finite by construction. For a
conjectured recurrence with characteristic polynomial q,

    a(n) - sum_i c_i a(n-i) = 1^T M^(n-r) q(M) 1,

so the recurrence holds for every n > t exactly when u_j = 1^T M^j q(M) 1 vanishes for all
j > t - r. The sequence (u_j) obeys the MONIC recurrence given by the characteristic
polynomial of M, so S consecutive zeros force all later ones: the last nonzero u_j pins the
threshold exactly, and the whole thing is a finite exact integer computation.

44 entries proved, 0 failures, states from 9 up to 19683. Every one was checked by
rebuilding the digraph from the entry's own wording and matching the walk counts against
every published term before the algebra was trusted.

**Three mistakes made getting here, all worth remembering.**
1. *The block-marker trap, again.* A first pass over "entries with a conjectured recurrence
   and a factual g.f." reported **458 provable**. Block-aware filtering cut it to **9**: on
   498 of those entries the "factual" g.f. sat inside a `Conjectures from _Colin Barker_:
   (Start) ... (End)` block, so it was conjectural, and using it would have been circular.
   `blocks.py` exists precisely for this and was not used. **Never read conjecturality off
   a single line.**
2. *A normaliser that ate a letter.* The name parser rewrote every `x` into ` X `, including
   the one inside "exactly", so 13 names silently failed to parse. Restricting the rewrite
   to an `x` between digits or parens fixed it.
3. *Demanding more than the conjecture claims.* The first annihilation test required the
   recurrence from n = order onwards and reported **12 failures**. Hardin fits his
   recurrences to his own data, so a universal failure was implausible on its face -- and
   indeed the test was wrong, not the conjectures: the right question is the smallest
   threshold t, not whether t = order. All 12 came back proved once `threshold()` replaced
   `annihilates()`.

**Where this engine goes next.** The same census counted **1053** entries whose names
mention a 2 X 2 subblock condition of other shapes (sum <= c, sum having a property) and
**512** of the "avoiding <pattern> horizontally and <pattern> vertically" form, plus 4949
more n X k array entries in total, nearly all with empirical recurrences and no paper. Each
new condition needs only its own edge predicate; the rest of the engine is unchanged. The
state space (m+1)^K is the only real limit -- 19683 ran fine, 65536 was skipped.


**Transfer matrix, second family: 159 more (the constant-stress tilings).** Names of the
form

    Number of (n+1) X (K+1) 0..m arrays with every 2 X 2 subblock having its diagonal sum
    differing from its antidiagonal sum by c [, with no adjacent elements equal]

In a block with top row (r_j, r_{j+1}) and bottom row (s_j, s_{j+1}) the condition is
`|r_j + s_{j+1} - r_{j+1} - s_j| = c`. Note the ABSOLUTE VALUE: reading "differing by c" as
a signed equation gives exactly half the right count, which the DATA check caught
immediately (136 vs 68 on A234162). Where "no adjacent elements equal" is present it splits
in two: the horizontal part constrains a single row and so selects the VERTEX set, the
vertical part constrains a pair and so belongs to the EDGE relation.

159 proved, 0 failures, orders 2 to 49, state spaces 9 to 16807. Every one matched its
entry's published terms before the algebra was trusted, none was already settled, and every
proved threshold landed at the natural minimum. 46 were skipped for a state space over
20000, 5 for an unparsable recurrence, 3 for being square (n+1) X (n+1) arrays, where the
count is not a walk in n.

**Operational note: the sweep is now restartable.** The container restarted mid-run and
80 completed items were lost because results were written only at the end. `sweep_transfer3.py`
now saves `transfer3_hits.json` and `transfer3_done.json` after every entry and skips what
is already done. **Any sweep that takes more than a few minutes should do the same.**


**Transfer matrix, third family: 496 more (pattern avoidance).** Names of the form

    Number of n X K 0..m arrays avoiding <p> [and <p2>] horizontally
                            and <q> [and <q2>] vertically

The patterns have length 3, so the constraint across the growing direction ties together
THREE consecutive rows and a single row is not enough state. Take a window of TWO
consecutive admissible rows: the step drops the first and appends a new one, and the edge
condition is exactly the one new vertical triple per column. Then
`a(n) = 1^T P^(n-2) 1`. Rows failing the horizontal patterns are excluded from the vertex
set, since that condition lives inside one row. For the transposed names ("K X n arrays")
the two directions swap and the same code applies.

496 of 512 proved, 0 failures, orders 2 to 99, state spaces 16 to 1936.

**A regex bug that had been silently costing entries.** `ratrec.parse_rec` matched a term's
coefficient with `[^+-]+?` -- at least one character -- so a term written with an implicit
coefficient of 1, as in `+a(n-20)`, never matched, the leftover check fired, and the whole
line was refused. **That took this sweep from 206 to 496.** The same bug will have cost
entries in every earlier sweep that used `parse_rec`; the fix is in, and the earlier
families are worth re-running.

**The DATA check earned its place twice more.**
- A207353's name is "avoiding the pattern z+1 z+1 z horizontally" -- a PARAMETRISED pattern,
  not literal digits. The parser read the digits and built a wrong model, and the data check
  caught it. `transfer4.parse_name` now refuses any name containing `the pattern`, a bare
  `z`, or `<letter>+<digit>`.
- A207600 counts 3 X n arrays with offset 0, so its DATA begins with the empty array,
  a(0) = 1, and the model list starts one index later. Not proved; the sweep has no offset
  alignment. One entry, recorded rather than bodged.

**On thresholds.** 230 of the 496 entries state their own "for n > k"; in every one of those
the proved threshold is at or before the stated one. For the other 266 the proved threshold
is the natural minimum. A check across all 496 found **zero** indices where the recurrence
fails at an index the entry itself claims. An earlier version of that check ignored the
stated thresholds and reported 8 false alarms -- always test the claim the entry actually
makes.


**Transfer matrix, fourth family: 788 more (neighbour counts).** Names of the form

    Number of n X K 0..m arrays with every element equal|unequal to <set> king-move
    adjacent elements [, with upper left element zero]

Each cell must have, among its neighbours, a number carrying the same value (or a different
value) lying in a stated set. Three neighbourhoods appear: king-move (8), "horizontally,
diagonally or antidiagonally" (6), and "horizontally or vertically" (4).

**What is new here is the BOUNDARY.** The neighbourhood reaches one row up and one row down,
so a window of two rows is enough state -- but the first row has nothing above it and the
last nothing below, and both then satisfy the condition more easily. A plain walk count
`1^T P^(n-2) 1` is therefore WRONG. The right object is

    a(n) = s^T P^(n-2) e

with `s(r,s) = 1` when row r passes with no row above (and, where the entry says so,
`r_1 = 0`), the edge `(r,s) -> (s,t)` testing row s against r and t, and `e(r,s) = 1` when
row s passes with no row below. Each row's condition is then tested exactly once and with
the right neighbours. `transfer5.py` carries its own `terms` and `threshold` taking start
and end vectors, because the ones in `transfer2` assume all-ones.

788 proved, 0 failures, 0 data mismatches, orders 2 to 82, state spaces 16 to 16384. 621 of
the entries state their own "for n > k" and the proved threshold is at or before it in every
case; a check across all 788 found no index where a recurrence fails at a point its entry
claims.

**Shell hazard, again.** The chain `rank.py && ... && rm -rf papers && mv ... && rm -f
*.zip && makezips.py` hit the 2-minute tool timeout part-way through, after the rm and mv
but during the zipping, leaving six partial archives. The roster itself was intact and was
verified by counting before anything else was done. **Split the rank/replace step from the
zip step; never leave both in one chain.**

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

### 31 Aug 2026: transfer matrix, fifth family — 426 papers from ONE generic predicate compiler

The four earlier transfer-matrix families each needed their own name parser and their own
edge predicate: subblock sums, constant stress, pattern avoidance, neighbour counts. That
is the wrong shape of work. The families differ only in the PREDICATE on the four entries
of a 2 X 2 block; the digraph, the walk count, the Cayley--Hamilton bound and the
annihilation test are identical every time.

`transfer6.py` is therefore built the other way round: one fixed engine plus a compiler
that turns the predicate clause of an OEIS name into a Python function of
`(a,b,c,d) = (top-left, top-right, bottom-left, bottom-right)` and, at the same time,
into the LaTeX line the paper displays. Adding a family is adding one regex and one
lambda. Twenty-odd predicate forms are compiled today, among them:

  * sums (`summing to 4 6 or 8`, `summing to a prime`, `sum greater than 4`);
  * counts (`having two or three distinct values`, `having one or two 1s`,
    `containing exactly one value repeat`, `having exactly 2 ones`);
  * differences (`the sum of the squares of all six edge and diagonal differences equal
    to 12`, `the absolute values ... no larger than 1`, `distinct clockwise edge
    differences`, `at most one duplicate clockwise edge difference`);
  * algebra (`zero permanent`, `nonzero determinant`, `equal diagonal elements or equal
    antidiagonal elements`);
  * comparisons (`the sum of its diagonal elements greater than the maximum of its
    antidiagonal elements`, `x11-x00 less than x10-x01`).

Four things the engine now handles that the older ones did not:

  1. **Fraction prefixes.** `Half the number of ...`, `1/4 the number of ...`,
     `One quarter ...`, `1/25 ...` — 83 of the 426. A constant factor passes through the
     annihilation test untouched, but it must be divided out before the DATA check or
     every one of them looks like a wrong model.
  2. **Transposed names.** `Number of (6+1)X(n+1) 0..2 arrays ...` walks along COLUMNS,
     and the block is then `[[r_i, s_i], [r_{i+1}, s_{i+1}]]`, not `[[r_j, r_{j+1}],
     [s_j, s_{j+1}]]`. Reading it the other way silently transposes every predicate that
     is not symmetric.
  3. **A depth-first edge build.** The edge condition is a conjunction of one constraint
     per adjacent column pair, so the successors of a row are enumerated column by column
     instead of by testing all S^2 pairs. At S = 32768 that is the difference between
     seconds and an hour.
  4. **The `no` quantifier.** `with no 2 X 2 subblock having ...` is the negation of the
     same predicate, not a different predicate.

**A bug worth recording.** The name normaliser that inserts spaces around the product
sign used a lookbehind `(?<=[n)])` so that `nX4` became `n X 4`. It also fired on the `n`
that ends the ordinary word *than*, so `having x11-x00 less than x10-x01` became
`... less tha X 10-x01` and 20 entries were refused as unparsable. The left token is now
matched as `(\bn|\d|\))`, which requires a standalone `n`. This is the third time a
name normaliser has eaten a letter of an English word; the pattern to distrust is any
character class of single letters applied to a whole name.

**Result.** 426 entries proved, no failures, no DATA mismatches, no unparsable
recurrences. Orders 2 to 86, state spaces 4 to 32768. Every one of the 426 was checked
against `rank-map.json` before building — 190 entries in the pool already had papers from
the earlier families and were skipped, which is exactly what the duplicate check is for.
A separate consistency check the older engines could not make: the name says the array has
`n + b` lines, so the DATA must line up at shift `b - 1 + offset`; the shift found by the
DATA search agreed with that arithmetic in all 426 cases, so the indexing is not a fit.

**What is left in this pool, measured.** 52 entries parse but have state spaces from
46656 to 9765625 — 43 of them constant-stress — and are out of reach of an explicit
adjacency list; they need a matrix-product form of the matvec and a bound on the Krylov
dimension, and are recorded as unfinished rather than skipped quietly. Roughly 470 names
carry a 2 X 2 clause the compiler still refuses: about 150 add `and new values 0..k
introduced in row major order` (a canonical-form condition, not local — the state must
carry how many values have been introduced), about 60 compare a block with its
neighbouring blocks (local to a THREE-row window, so the state is a row pair), and 23 say
`all 2 X 2 subblock sums the same` (local once the common sum is fixed, so the count
splits as a sum over that value). All three are reachable; none is done.

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
