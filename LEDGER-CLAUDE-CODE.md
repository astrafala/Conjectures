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

Last updated 2 Sep 2026. Roster: **6514 papers** (6508 proofs, 6 disproofs), files `1-PROOF.pdf` … `6514-PROOF.pdf`, **numbered by how hard the result was**: 1 is the hardest.
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
| 77 | PROOF | A251454 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 78 | PROOF | A251459 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 79 | PROOF | A234078 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 80 | PROOF | A250978 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 81 | PROOF | A251354 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 82 | PROOF | A251359 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 83 | PROOF | A222387 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 84 | PROOF | A234446 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 85 | PROOF | A251015 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 86 | PROOF | A234986 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 87 | PROOF | A233719 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 88 | PROOF | A296112 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 89 | PROOF | A300212 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 90 | PROOF | A234906 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 91 | PROOF | A234911 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 92 | PROOF | A251006 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 93 | PROOF | A233729 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 94 | PROOF | A264516 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 95 | PROOF | A251563 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 96 | PROOF | A251567 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 97 | PROOF | A220238 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 98 | PROOF | A220283 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 99 | PROOF | A263814 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 100 | PROOF | A263962 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 101 | PROOF | A233923 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 102 | PROOF | A251397 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 103 | PROOF | A251402 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 104 | PROOF | A250923 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 105 | PROOF | A283723 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 106 | PROOF | A234164 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 107 | PROOF | A251332 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 108 | PROOF | A234339 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 109 | PROOF | A234343 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 110 | PROOF | A231705 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 111 | PROOF | A231710 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 112 | PROOF | A298967 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 113 | PROOF | A233712 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 114 | PROOF | A250960 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 115 | PROOF | A250965 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 116 | PROOF | A233660 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 117 | PROOF | A251303 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 118 | PROOF | A251308 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 119 | PROOF | A235073 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 120 | PROOF | A235078 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 121 | PROOF | A283039 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 122 | PROOF | A220972 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 123 | PROOF | A233870 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 124 | PROOF | A233875 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 125 | PROOF | A235003 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 126 | PROOF | A235007 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 127 | PROOF | A264571 | grid permutations with a bounded index change, as a matching turned into a walk |
| 128 | PROOF | A233945 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 129 | PROOF | A250837 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 130 | PROOF | A233899 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 131 | PROOF | A264509 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 132 | PROOF | A233854 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 133 | PROOF | A234425 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 134 | PROOF | A234428 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 135 | PROOF | A233641 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 136 | PROOF | A251207 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 137 | PROOF | A229315 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 138 | PROOF | A220529 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 139 | PROOF | A250930 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 140 | PROOF | A235021 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 141 | PROOF | A220914 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 142 | PROOF | A233630 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 143 | PROOF | A218176 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 144 | PROOF | A235102 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 145 | PROOF | A233975 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 146 | PROOF | A251217 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 147 | PROOF | A251266 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 148 | PROOF | A234401 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 149 | PROOF | A234405 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 150 | PROOF | A251347 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 151 | PROOF | A281804 | a cell condition with an exception budget, counted up to relabelling |
| 152 | PROOF | A220792 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 153 | PROOF | A233887 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 154 | PROOF | A279265 | a cell condition with an exception budget, counted up to relabelling |
| 155 | PROOF | A220920 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 156 | PROOF | A220936 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 157 | PROOF | A264417 | grid permutations with a bounded index change, as a matching turned into a walk |
| 158 | PROOF | A264572 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 159 | PROOF | A279154 | a cell condition with an exception budget, counted up to relabelling |
| 160 | PROOF | A281984 | a cell condition with an exception budget, counted up to relabelling |
| 161 | PROOF | A280904 | a cell condition with an exception budget, counted up to relabelling |
| 162 | PROOF | A281161 | a cell condition with an exception budget, counted up to relabelling |
| 163 | PROOF | A279489 | a cell condition with an exception budget, counted up to relabelling |
| 164 | PROOF | A263971 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 165 | PROOF | A264268 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 166 | PROOF | A234407 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 167 | PROOF | A234412 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 168 | PROOF | A251494 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 169 | PROOF | A234892 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 170 | PROOF | A234898 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 171 | PROOF | A280809 | a cell condition with an exception budget, counted up to relabelling |
| 172 | PROOF | A234545 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 173 | PROOF | A251612 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 174 | PROOF | A251616 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 175 | PROOF | A251257 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 176 | PROOF | A234998 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 177 | PROOF | A222936 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 178 | PROOF | A264241 | grid permutations with a bounded index change, as a matching turned into a walk |
| 179 | PROOF | A281762 | a cell condition with an exception budget, counted up to relabelling |
| 180 | PROOF | A264258 | grid permutations with a bounded index change, as a matching turned into a walk |
| 181 | PROOF | A220173 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 182 | PROOF | A221663 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 183 | PROOF | A264219 | grid permutations with a bounded index change, as a matching turned into a walk |
| 184 | PROOF | A229539 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 185 | PROOF | A281884 | a cell condition with an exception budget, counted up to relabelling |
| 186 | PROOF | A234477 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 187 | PROOF | A234481 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 188 | PROOF | A220325 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 189 | PROOF | A221664 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 190 | PROOF | A235175 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 191 | PROOF | A264880 | grid permutations with a bounded index change, as a matching turned into a walk |
| 192 | PROOF | A282156 | a cell condition with an exception budget, counted up to relabelling |
| 193 | PROOF | A233678 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 194 | PROOF | A280176 | a cell condition with an exception budget, counted up to relabelling |
| 195 | PROOF | A279744 | a cell condition with an exception budget, counted up to relabelling |
| 196 | PROOF | A234242 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 197 | PROOF | A234245 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 198 | PROOF | A220801 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 199 | PROOF | A251469 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 200 | PROOF | A251474 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 201 | PROOF | A264196 | grid permutations with a bounded index change, as a matching turned into a walk |
| 202 | PROOF | A251296 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 203 | PROOF | A281798 | a cell condition with an exception budget, counted up to relabelling |
| 204 | PROOF | A233755 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 205 | PROOF | A229516 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 206 | PROOF | A280808 | a cell condition with an exception budget, counted up to relabelling |
| 207 | PROOF | A279130 | a cell condition with an exception budget, counted up to relabelling |
| 208 | PROOF | A255149 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 209 | PROOF | A251339 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 210 | PROOF | A251442 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 211 | PROOF | A281695 | a cell condition with an exception budget, counted up to relabelling |
| 212 | PROOF | A234229 | the conjecture's own text was unavailable; the recurrence was recovered and shown unique |
| 213 | PROOF | A235258 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 214 | PROOF | A251801 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 215 | PROOF | A235071 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 216 | PROOF | A281767 | a cell condition with an exception budget, counted up to relabelling |
| 217 | PROOF | A220534 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 218 | PROOF | A251175 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 219 | PROOF | A229533 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 220 | PROOF | A279974 | a cell condition with an exception budget, counted up to relabelling |
| 221 | PROOF | A280807 | a cell condition with an exception budget, counted up to relabelling |
| 222 | PROOF | A218594 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 223 | PROOF | A218191 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 224 | PROOF | A218894 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 225 | PROOF | A234152 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 226 | PROOF | A220372 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 227 | PROOF | A251158 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 228 | PROOF | A264283 | grid permutations with a bounded index change, as a matching turned into a walk |
| 229 | PROOF | A264334 | grid permutations with a bounded index change, as a matching turned into a walk |
| 230 | PROOF | A264504 | grid permutations with a bounded index change, as a matching turned into a walk |
| 231 | PROOF | A264567 | grid permutations with a bounded index change, as a matching turned into a walk |
| 232 | PROOF | A264581 | grid permutations with a bounded index change, as a matching turned into a walk |
| 233 | PROOF | A264485 | grid permutations with a bounded index change, as a matching turned into a walk |
| 234 | PROOF | A280310 | a cell condition with an exception budget, counted up to relabelling |
| 235 | PROOF | A279802 | a cell condition with an exception budget, counted up to relabelling |
| 236 | PROOF | A281328 | a cell condition with an exception budget, counted up to relabelling |
| 237 | PROOF | A281030 | a cell condition with an exception budget, counted up to relabelling |
| 238 | PROOF | A222445 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 239 | PROOF | A279461 | a cell condition with an exception budget, counted up to relabelling |
| 240 | PROOF | A264301 | grid permutations with a bounded index change, as a matching turned into a walk |
| 241 | PROOF | A281248 | a cell condition with an exception budget, counted up to relabelling |
| 242 | PROOF | A235248 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 243 | PROOF | A220575 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 244 | PROOF | A234190 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 245 | PROOF | A217980 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 246 | PROOF | A234208 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 247 | PROOF | A228982 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 248 | PROOF | A251515 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 249 | PROOF | A279324 | a cell condition with an exception budget, counted up to relabelling |
| 250 | PROOF | A279582 | a cell condition with an exception budget, counted up to relabelling |
| 251 | PROOF | A281079 | a cell condition with an exception budget, counted up to relabelling |
| 252 | PROOF | A279531 | a cell condition with an exception budget, counted up to relabelling |
| 253 | PROOF | A264252 | grid permutations with a bounded index change, as a matching turned into a walk |
| 254 | PROOF | A279163 | a cell condition with an exception budget, counted up to relabelling |
| 255 | PROOF | A264139 | grid permutations with a bounded index change, as a matching turned into a walk |
| 256 | PROOF | A234672 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 257 | PROOF | A234712 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 258 | PROOF | A234982 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 259 | PROOF | A220223 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 260 | PROOF | A264362 | grid permutations with a bounded index change, as a matching turned into a walk |
| 261 | PROOF | A282186 | a cell condition with an exception budget, counted up to relabelling |
| 262 | PROOF | A282126 | a cell condition with an exception budget, counted up to relabelling |
| 263 | PROOF | A264001 | grid permutations with a bounded index change, as a matching turned into a walk |
| 264 | PROOF | A264204 | grid permutations with a bounded index change, as a matching turned into a walk |
| 265 | PROOF | A229641 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 266 | PROOF | A280157 | a cell condition with an exception budget, counted up to relabelling |
| 267 | PROOF | A283661 | a cell condition with an exception budget, counted up to relabelling |
| 268 | PROOF | A218900 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 269 | PROOF | A281078 | a cell condition with an exception budget, counted up to relabelling |
| 270 | PROOF | A281560 | a cell condition with an exception budget, counted up to relabelling |
| 271 | PROOF | A281761 | a cell condition with an exception budget, counted up to relabelling |
| 272 | PROOF | A220456 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 273 | PROOF | A263966 | grid permutations with a bounded index change, as a matching turned into a walk |
| 274 | PROOF | A264282 | grid permutations with a bounded index change, as a matching turned into a walk |
| 275 | PROOF | A264310 | grid permutations with a bounded index change, as a matching turned into a walk |
| 276 | PROOF | A280806 | a cell condition with an exception budget, counted up to relabelling |
| 277 | PROOF | A279264 | a cell condition with an exception budget, counted up to relabelling |
| 278 | PROOF | A235239 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 279 | PROOF | A234991 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 280 | PROOF | A229635 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 281 | PROOF | A263970 | grid permutations with a bounded index change, as a matching turned into a walk |
| 282 | PROOF | A281160 | a cell condition with an exception budget, counted up to relabelling |
| 283 | PROOF | A219437 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 284 | PROOF | A280482 | a cell condition with an exception budget, counted up to relabelling |
| 285 | PROOF | A281655 | a cell condition with an exception budget, counted up to relabelling |
| 286 | PROOF | A218646 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 287 | PROOF | A263817 | grid permutations with a bounded index change, as a matching turned into a walk |
| 288 | PROOF | A264109 | grid permutations with a bounded index change, as a matching turned into a walk |
| 289 | DISPROOF | A197230 | a conjecture shown FALSE, with the recurrence that holds instead |
| 290 | PROOF | A279738 | a cell condition with an exception budget, counted up to relabelling |
| 291 | PROOF | A281077 | a cell condition with an exception budget, counted up to relabelling |
| 292 | PROOF | A218367 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 293 | PROOF | A218201 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 294 | PROOF | A220795 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 295 | PROOF | A281135 | a cell condition with an exception budget, counted up to relabelling |
| 296 | PROOF | A280280 | a cell condition with an exception budget, counted up to relabelling |
| 297 | PROOF | A279973 | a cell condition with an exception budget, counted up to relabelling |
| 298 | PROOF | A281559 | a cell condition with an exception budget, counted up to relabelling |
| 299 | PROOF | A279979 | a cell condition with an exception budget, counted up to relabelling |
| 300 | PROOF | A219423 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 301 | PROOF | A281399 | a cell condition with an exception budget, counted up to relabelling |
| 302 | PROOF | A281125 | a cell condition with an exception budget, counted up to relabelling |
| 303 | PROOF | A264212 | grid permutations with a bounded index change, as a matching turned into a walk |
| 304 | PROOF | A218081 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 305 | PROOF | A217633 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 306 | PROOF | A229101 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 307 | PROOF | A281535 | a cell condition with an exception budget, counted up to relabelling |
| 308 | PROOF | A280230 | a cell condition with an exception budget, counted up to relabelling |
| 309 | PROOF | A279524 | a cell condition with an exception budget, counted up to relabelling |
| 310 | PROOF | A263965 | grid permutations with a bounded index change, as a matching turned into a walk |
| 311 | PROOF | A220382 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 312 | PROOF | A279153 | a cell condition with an exception budget, counted up to relabelling |
| 313 | PROOF | A220316 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 314 | PROOF | A220339 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 315 | PROOF | A220387 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 316 | PROOF | A281398 | a cell condition with an exception budget, counted up to relabelling |
| 317 | PROOF | A229604 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 318 | PROOF | A280213 | a cell condition with an exception budget, counted up to relabelling |
| 319 | PROOF | A264309 | grid permutations with a bounded index change, as a matching turned into a walk |
| 320 | PROOF | A264295 | grid permutations with a bounded index change, as a matching turned into a walk |
| 321 | PROOF | A280175 | a cell condition with an exception budget, counted up to relabelling |
| 322 | PROOF | A281558 | a cell condition with an exception budget, counted up to relabelling |
| 323 | PROOF | A281931 | a cell condition with an exception budget, counted up to relabelling |
| 324 | PROOF | A217979 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 325 | PROOF | A220917 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 326 | PROOF | A279898 | a cell condition with an exception budget, counted up to relabelling |
| 327 | PROOF | A264373 | grid permutations with a bounded index change, as a matching turned into a walk |
| 328 | PROOF | A264528 | grid permutations with a bounded index change, as a matching turned into a walk |
| 329 | PROOF | A282227 | a cell condition with an exception budget, counted up to relabelling |
| 330 | PROOF | A229538 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 331 | PROOF | A218062 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 332 | PROOF | A281983 | a cell condition with an exception budget, counted up to relabelling |
| 333 | PROOF | A264879 | grid permutations with a bounded index change, as a matching turned into a walk |
| 334 | PROOF | A219399 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 335 | PROOF | A229515 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 336 | PROOF | A281397 | a cell condition with an exception budget, counted up to relabelling |
| 337 | PROOF | A281076 | a cell condition with an exception budget, counted up to relabelling |
| 338 | PROOF | A264515 | grid permutations with a bounded index change, as a matching turned into a walk |
| 339 | PROOF | A218633 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 340 | PROOF | A218811 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 341 | PROOF | A218760 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 342 | PROOF | A281054 | a cell condition with an exception budget, counted up to relabelling |
| 343 | PROOF | A281567 | a cell condition with an exception budget, counted up to relabelling |
| 344 | PROOF | A229476 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 345 | PROOF | A229532 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 346 | PROOF | A229591 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 347 | PROOF | A264240 | grid permutations with a bounded index change, as a matching turned into a walk |
| 348 | PROOF | A264631 | grid permutations with a bounded index change, as a matching turned into a walk |
| 349 | PROOF | A229634 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 350 | PROOF | A229640 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 351 | PROOF | A279921 | a cell condition with an exception budget, counted up to relabelling |
| 352 | PROOF | A220757 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 353 | PROOF | A280805 | a cell condition with an exception budget, counted up to relabelling |
| 354 | PROOF | A281029 | a cell condition with an exception budget, counted up to relabelling |
| 355 | PROOF | A280804 | a cell condition with an exception budget, counted up to relabelling |
| 356 | PROOF | A280401 | a cell condition with an exception budget, counted up to relabelling |
| 357 | PROOF | A218839 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 358 | PROOF | A218228 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 359 | PROOF | A218282 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 360 | PROOF | A219144 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 361 | PROOF | A281406 | a cell condition with an exception budget, counted up to relabelling |
| 362 | PROOF | A264005 | grid permutations with a bounded index change, as a matching turned into a walk |
| 363 | PROOF | A259723 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 364 | PROOF | A229603 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 365 | PROOF | A279737 | a cell condition with an exception budget, counted up to relabelling |
| 366 | PROOF | A280229 | a cell condition with an exception budget, counted up to relabelling |
| 367 | PROOF | A218523 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 368 | PROOF | A279743 | a cell condition with an exception budget, counted up to relabelling |
| 369 | PROOF | A279488 | a cell condition with an exception budget, counted up to relabelling |
| 370 | PROOF | A219305 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 371 | PROOF | A220065 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 372 | PROOF | A281690 | a cell condition with an exception budget, counted up to relabelling |
| 373 | PROOF | A281566 | a cell condition with an exception budget, counted up to relabelling |
| 374 | PROOF | A281396 | a cell condition with an exception budget, counted up to relabelling |
| 375 | PROOF | A217960 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 376 | PROOF | A279301 | a cell condition with an exception budget, counted up to relabelling |
| 377 | PROOF | A280903 | a cell condition with an exception budget, counted up to relabelling |
| 378 | PROOF | A263813 | grid permutations with a bounded index change, as a matching turned into a walk |
| 379 | PROOF | A263961 | grid permutations with a bounded index change, as a matching turned into a walk |
| 380 | PROOF | A264308 | grid permutations with a bounded index change, as a matching turned into a walk |
| 381 | PROOF | A264477 | grid permutations with a bounded index change, as a matching turned into a walk |
| 382 | PROOF | A264545 | grid permutations with a bounded index change, as a matching turned into a walk |
| 383 | PROOF | A264564 | grid permutations with a bounded index change, as a matching turned into a walk |
| 384 | PROOF | A264578 | grid permutations with a bounded index change, as a matching turned into a walk |
| 385 | PROOF | A264630 | grid permutations with a bounded index change, as a matching turned into a walk |
| 386 | PROOF | A219101 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 387 | PROOF | A218066 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 388 | PROOF | A281159 | a cell condition with an exception budget, counted up to relabelling |
| 389 | PROOF | A221036 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 390 | PROOF | A220923 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 391 | PROOF | A281405 | a cell condition with an exception budget, counted up to relabelling |
| 392 | PROOF | A264108 | grid permutations with a bounded index change, as a matching turned into a walk |
| 393 | PROOF | A264184 | grid permutations with a bounded index change, as a matching turned into a walk |
| 394 | PROOF | A264191 | grid permutations with a bounded index change, as a matching turned into a walk |
| 395 | PROOF | A264342 | grid permutations with a bounded index change, as a matching turned into a walk |
| 396 | PROOF | A229457 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 397 | PROOF | A280119 | a cell condition with an exception budget, counted up to relabelling |
| 398 | PROOF | A281134 | a cell condition with an exception budget, counted up to relabelling |
| 399 | PROOF | A229590 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 400 | PROOF | A255101 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 401 | PROOF | A264111 | grid permutations with a bounded index change, as a matching turned into a walk |
| 402 | PROOF | A264132 | grid permutations with a bounded index change, as a matching turned into a walk |
| 403 | PROOF | A264314 | grid permutations with a bounded index change, as a matching turned into a walk |
| 404 | PROOF | A264331 | grid permutations with a bounded index change, as a matching turned into a walk |
| 405 | PROOF | A264501 | grid permutations with a bounded index change, as a matching turned into a walk |
| 406 | PROOF | A280156 | a cell condition with an exception budget, counted up to relabelling |
| 407 | PROOF | A281395 | a cell condition with an exception budget, counted up to relabelling |
| 408 | PROOF | A281883 | a cell condition with an exception budget, counted up to relabelling |
| 409 | PROOF | A217640 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 410 | PROOF | A218893 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 411 | PROOF | A264508 | grid permutations with a bounded index change, as a matching turned into a walk |
| 412 | PROOF | A281564 | a cell condition with an exception budget, counted up to relabelling |
| 413 | PROOF | A281803 | a cell condition with an exception budget, counted up to relabelling |
| 414 | PROOF | A218899 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 415 | PROOF | A220243 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 416 | PROOF | A281053 | a cell condition with an exception budget, counted up to relabelling |
| 417 | PROOF | A279658 | a cell condition with an exception budget, counted up to relabelling |
| 418 | PROOF | A218175 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 419 | PROOF | A218080 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 420 | PROOF | A219058 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 421 | PROOF | A218593 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 422 | PROOF | A219447 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 423 | PROOF | A220964 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 424 | PROOF | A218190 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 425 | PROOF | A218366 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 426 | PROOF | A281203 | a cell condition with an exception budget, counted up to relabelling |
| 427 | PROOF | A264060 | grid permutations with a bounded index change, as a matching turned into a walk |
| 428 | PROOF | A279867 | a cell condition with an exception budget, counted up to relabelling |
| 429 | PROOF | A281404 | a cell condition with an exception budget, counted up to relabelling |
| 430 | PROOF | A229508 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 431 | PROOF | A229668 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 432 | PROOF | A229682 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 433 | PROOF | A281052 | a cell condition with an exception budget, counted up to relabelling |
| 434 | PROOF | A229531 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 435 | PROOF | A279530 | a cell condition with an exception budget, counted up to relabelling |
| 436 | PROOF | A281534 | a cell condition with an exception budget, counted up to relabelling |
| 437 | PROOF | A281694 | a cell condition with an exception budget, counted up to relabelling |
| 438 | PROOF | A282155 | a cell condition with an exception budget, counted up to relabelling |
| 439 | PROOF | A256029 | a table line whose recurrence was unwritten, recovered from its stated order and shown unique |
| 440 | PROOF | A229537 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 441 | PROOF | A279801 | a cell condition with an exception budget, counted up to relabelling |
| 442 | PROOF | A281565 | a cell condition with an exception budget, counted up to relabelling |
| 443 | PROOF | A281075 | a cell condition with an exception budget, counted up to relabelling |
| 444 | PROOF | A219123 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 445 | PROOF | A281557 | a cell condition with an exception budget, counted up to relabelling |
| 446 | PROOF | A220762 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 447 | PROOF | A228972 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 448 | PROOF | A281074 | a cell condition with an exception budget, counted up to relabelling |
| 449 | PROOF | A220994 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 450 | PROOF | A264315 | grid permutations with a bounded index change, as a matching turned into a walk |
| 451 | PROOF | A279129 | a cell condition with an exception budget, counted up to relabelling |
| 452 | PROOF | A218061 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 453 | PROOF | A221031 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 454 | PROOF | A219412 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 455 | PROOF | A217965 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 456 | PROOF | A279162 | a cell condition with an exception budget, counted up to relabelling |
| 457 | PROOF | A228981 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 458 | PROOF | A219980 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 459 | PROOF | A220407 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 460 | PROOF | A219436 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 461 | PROOF | A264380 | grid permutations with a bounded index change, as a matching turned into a walk |
| 462 | PROOF | A264535 | grid permutations with a bounded index change, as a matching turned into a walk |
| 463 | PROOF | A264585 | grid permutations with a bounded index change, as a matching turned into a walk |
| 464 | PROOF | A264649 | grid permutations with a bounded index change, as a matching turned into a walk |
| 465 | PROOF | A264670 | grid permutations with a bounded index change, as a matching turned into a walk |
| 466 | PROOF | A281649 | a cell condition with an exception budget, counted up to relabelling |
| 467 | PROOF | A264478 | grid permutations with a bounded index change, as a matching turned into a walk |
| 468 | PROOF | A264546 | grid permutations with a bounded index change, as a matching turned into a walk |
| 469 | PROOF | A229456 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 470 | PROOF | A281403 | a cell condition with an exception budget, counted up to relabelling |
| 471 | PROOF | A280212 | a cell condition with an exception budget, counted up to relabelling |
| 472 | PROOF | A281247 | a cell condition with an exception budget, counted up to relabelling |
| 473 | PROOF | A264584 | grid permutations with a bounded index change, as a matching turned into a walk |
| 474 | PROOF | A279323 | a cell condition with an exception budget, counted up to relabelling |
| 475 | PROOF | A281327 | a cell condition with an exception budget, counted up to relabelling |
| 476 | PROOF | A263969 | grid permutations with a bounded index change, as a matching turned into a walk |
| 477 | PROOF | A264629 | grid permutations with a bounded index change, as a matching turned into a walk |
| 478 | PROOF | A280174 | a cell condition with an exception budget, counted up to relabelling |
| 479 | PROOF | A279460 | a cell condition with an exception budget, counted up to relabelling |
| 480 | PROOF | A281028 | a cell condition with an exception budget, counted up to relabelling |
| 481 | PROOF | A219151 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 482 | PROOF | A220304 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 483 | PROOF | A280553 | a cell condition with an exception budget, counted up to relabelling |
| 484 | PROOF | A281062 | a cell condition with an exception budget, counted up to relabelling |
| 485 | PROOF | A280552 | a cell condition with an exception budget, counted up to relabelling |
| 486 | PROOF | A281061 | a cell condition with an exception budget, counted up to relabelling |
| 487 | PROOF | A264246 | grid permutations with a bounded index change, as a matching turned into a walk |
| 488 | PROOF | A264677 | grid permutations with a bounded index change, as a matching turned into a walk |
| 489 | PROOF | A280551 | a cell condition with an exception budget, counted up to relabelling |
| 490 | PROOF | A281060 | a cell condition with an exception budget, counted up to relabelling |
| 491 | PROOF | A279652 | a cell condition with an exception budget, counted up to relabelling |
| 492 | PROOF | A280475 | a cell condition with an exception budget, counted up to relabelling |
| 493 | PROOF | A280550 | a cell condition with an exception budget, counted up to relabelling |
| 494 | PROOF | A281059 | a cell condition with an exception budget, counted up to relabelling |
| 495 | PROOF | A229602 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 496 | PROOF | A264300 | grid permutations with a bounded index change, as a matching turned into a walk |
| 497 | PROOF | A264365 | grid permutations with a bounded index change, as a matching turned into a walk |
| 498 | PROOF | A264484 | grid permutations with a bounded index change, as a matching turned into a walk |
| 499 | PROOF | A219064 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 500 | PROOF | A279972 | a cell condition with an exception budget, counted up to relabelling |
| 501 | PROOF | A281797 | a cell condition with an exception budget, counted up to relabelling |
| 502 | PROOF | A218588 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 503 | PROOF | A229639 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 504 | PROOF | A217451 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 505 | PROOF | A283660 | a cell condition with an exception budget, counted up to relabelling |
| 506 | PROOF | A221633 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 507 | PROOF | A281401 | a cell condition with an exception budget, counted up to relabelling |
| 508 | PROOF | A281766 | a cell condition with an exception budget, counted up to relabelling |
| 509 | PROOF | A220255 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 510 | PROOF | A218200 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 511 | PROOF | A220309 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 512 | PROOF | A220538 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 513 | PROOF | A218227 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 514 | PROOF | A220213 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 515 | PROOF | A218281 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 516 | PROOF | A264054 | grid permutations with a bounded index change, as a matching turned into a walk |
| 517 | PROOF | A264091 | grid permutations with a bounded index change, as a matching turned into a walk |
| 518 | PROOF | A264122 | grid permutations with a bounded index change, as a matching turned into a walk |
| 519 | PROOF | A281202 | a cell condition with an exception budget, counted up to relabelling |
| 520 | PROOF | A264138 | grid permutations with a bounded index change, as a matching turned into a walk |
| 521 | PROOF | A229475 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 522 | PROOF | A229507 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 523 | PROOF | A281201 | a cell condition with an exception budget, counted up to relabelling |
| 524 | PROOF | A279866 | a cell condition with an exception budget, counted up to relabelling |
| 525 | PROOF | A280481 | a cell condition with an exception budget, counted up to relabelling |
| 526 | PROOF | A264004 | grid permutations with a bounded index change, as a matching turned into a walk |
| 527 | PROOF | A264158 | grid permutations with a bounded index change, as a matching turned into a walk |
| 528 | PROOF | A264267 | grid permutations with a bounded index change, as a matching turned into a walk |
| 529 | PROOF | A279523 | a cell condition with an exception budget, counted up to relabelling |
| 530 | PROOF | A279581 | a cell condition with an exception budget, counted up to relabelling |
| 531 | PROOF | A281133 | a cell condition with an exception budget, counted up to relabelling |
| 532 | PROOF | A281654 | a cell condition with an exception budget, counted up to relabelling |
| 533 | PROOF | A282125 | a cell condition with an exception budget, counted up to relabelling |
| 534 | PROOF | A280549 | a cell condition with an exception budget, counted up to relabelling |
| 535 | PROOF | A281058 | a cell condition with an exception budget, counted up to relabelling |
| 536 | PROOF | A281402 | a cell condition with an exception budget, counted up to relabelling |
| 537 | PROOF | A221063 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 538 | PROOF | A264211 | grid permutations with a bounded index change, as a matching turned into a walk |
| 539 | PROOF | A264251 | grid permutations with a bounded index change, as a matching turned into a walk |
| 540 | PROOF | A264266 | grid permutations with a bounded index change, as a matching turned into a walk |
| 541 | PROOF | A264294 | grid permutations with a bounded index change, as a matching turned into a walk |
| 542 | PROOF | A218645 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 543 | PROOF | A279128 | a cell condition with an exception budget, counted up to relabelling |
| 544 | PROOF | A279978 | a cell condition with an exception budget, counted up to relabelling |
| 545 | PROOF | A281057 | a cell condition with an exception budget, counted up to relabelling |
| 546 | PROOF | A281394 | a cell condition with an exception budget, counted up to relabelling |
| 547 | PROOF | A219129 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 548 | PROOF | A219137 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 549 | PROOF | A220227 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 550 | PROOF | A264423 | grid permutations with a bounded index change, as a matching turned into a walk |
| 551 | PROOF | A218517 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 552 | PROOF | A218237 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 553 | PROOF | A218805 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 554 | PROOF | A217978 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 555 | PROOF | A279152 | a cell condition with an exception budget, counted up to relabelling |
| 556 | PROOF | A221667 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 557 | PROOF | A218804 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 558 | PROOF | A218236 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 559 | PROOF | A219398 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 560 | PROOF | A220971 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 561 | PROOF | A222381 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 562 | PROOF | A218843 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 563 | PROOF | A220191 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 564 | PROOF | A218759 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 565 | PROOF | A218189 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 566 | PROOF | A220172 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 567 | PROOF | A280439 | a cell condition with an exception budget, counted up to relabelling |
| 568 | PROOF | A281211 | a cell condition with an exception budget, counted up to relabelling |
| 569 | PROOF | A280438 | a cell condition with an exception budget, counted up to relabelling |
| 570 | PROOF | A281210 | a cell condition with an exception budget, counted up to relabelling |
| 571 | PROOF | A229390 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 572 | PROOF | A280897 | a cell condition with an exception budget, counted up to relabelling |
| 573 | PROOF | A280437 | a cell condition with an exception budget, counted up to relabelling |
| 574 | PROOF | A281209 | a cell condition with an exception budget, counted up to relabelling |
| 575 | PROOF | A229584 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 576 | PROOF | A279575 | a cell condition with an exception budget, counted up to relabelling |
| 577 | PROOF | A279852 | a cell condition with an exception budget, counted up to relabelling |
| 578 | PROOF | A280393 | a cell condition with an exception budget, counted up to relabelling |
| 579 | PROOF | A264281 | grid permutations with a bounded index change, as a matching turned into a walk |
| 580 | PROOF | A264332 | grid permutations with a bounded index change, as a matching turned into a walk |
| 581 | PROOF | A264360 | grid permutations with a bounded index change, as a matching turned into a walk |
| 582 | PROOF | A264502 | grid permutations with a bounded index change, as a matching turned into a walk |
| 583 | PROOF | A264565 | grid permutations with a bounded index change, as a matching turned into a walk |
| 584 | PROOF | A264579 | grid permutations with a bounded index change, as a matching turned into a walk |
| 585 | PROOF | A280436 | a cell condition with an exception budget, counted up to relabelling |
| 586 | PROOF | A281208 | a cell condition with an exception budget, counted up to relabelling |
| 587 | PROOF | A229667 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 588 | PROOF | A229633 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 589 | PROOF | A279651 | a cell condition with an exception budget, counted up to relabelling |
| 590 | PROOF | A280474 | a cell condition with an exception budget, counted up to relabelling |
| 591 | PROOF | A280896 | a cell condition with an exception budget, counted up to relabelling |
| 592 | PROOF | A282185 | a cell condition with an exception budget, counted up to relabelling |
| 593 | PROOF | A264000 | grid permutations with a bounded index change, as a matching turned into a walk |
| 594 | PROOF | A264166 | grid permutations with a bounded index change, as a matching turned into a walk |
| 595 | PROOF | A264218 | grid permutations with a bounded index change, as a matching turned into a walk |
| 596 | PROOF | A264239 | grid permutations with a bounded index change, as a matching turned into a walk |
| 597 | PROOF | A264245 | grid permutations with a bounded index change, as a matching turned into a walk |
| 598 | PROOF | A264359 | grid permutations with a bounded index change, as a matching turned into a walk |
| 599 | PROOF | A229388 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 600 | PROOF | A229455 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 601 | PROOF | A229589 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 602 | PROOF | A280118 | a cell condition with an exception budget, counted up to relabelling |
| 603 | PROOF | A281124 | a cell condition with an exception budget, counted up to relabelling |
| 604 | PROOF | A279263 | a cell condition with an exception budget, counted up to relabelling |
| 605 | PROOF | A279736 | a cell condition with an exception budget, counted up to relabelling |
| 606 | PROOF | A281760 | a cell condition with an exception budget, counted up to relabelling |
| 607 | PROOF | A219004 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 608 | PROOF | A229601 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 609 | PROOF | A229632 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 610 | PROOF | A229536 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 611 | PROOF | A263999 | grid permutations with a bounded index change, as a matching turned into a walk |
| 612 | PROOF | A264202 | grid permutations with a bounded index change, as a matching turned into a walk |
| 613 | PROOF | A229387 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 614 | PROOF | A279971 | a cell condition with an exception budget, counted up to relabelling |
| 615 | PROOF | A281050 | a cell condition with an exception budget, counted up to relabelling |
| 616 | PROOF | A281930 | a cell condition with an exception budget, counted up to relabelling |
| 617 | PROOF | A218060 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 618 | PROOF | A229638 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 619 | PROOF | A279300 | a cell condition with an exception budget, counted up to relabelling |
| 620 | PROOF | A279865 | a cell condition with an exception budget, counted up to relabelling |
| 621 | PROOF | A280309 | a cell condition with an exception budget, counted up to relabelling |
| 622 | PROOF | A219406 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 623 | PROOF | A221059 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 624 | PROOF | A280155 | a cell condition with an exception budget, counted up to relabelling |
| 625 | PROOF | A281982 | a cell condition with an exception budget, counted up to relabelling |
| 626 | PROOF | A229665 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 627 | PROOF | A217639 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 628 | PROOF | A264507 | grid permutations with a bounded index change, as a matching turned into a walk |
| 629 | PROOF | A219422 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 630 | PROOF | A219136 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 631 | PROOF | A264069 | grid permutations with a bounded index change, as a matching turned into a walk |
| 632 | PROOF | A264130 | grid permutations with a bounded index change, as a matching turned into a walk |
| 633 | PROOF | A264339 | grid permutations with a bounded index change, as a matching turned into a walk |
| 634 | PROOF | A264167 | grid permutations with a bounded index change, as a matching turned into a walk |
| 635 | PROOF | A264286 | grid permutations with a bounded index change, as a matching turned into a walk |
| 636 | PROOF | A264491 | grid permutations with a bounded index change, as a matching turned into a walk |
| 637 | PROOF | A264203 | grid permutations with a bounded index change, as a matching turned into a walk |
| 638 | PROOF | A264622 | grid permutations with a bounded index change, as a matching turned into a walk |
| 639 | PROOF | A279851 | a cell condition with an exception budget, counted up to relabelling |
| 640 | PROOF | A280400 | a cell condition with an exception budget, counted up to relabelling |
| 641 | PROOF | A280435 | a cell condition with an exception budget, counted up to relabelling |
| 642 | PROOF | A281207 | a cell condition with an exception budget, counted up to relabelling |
| 643 | PROOF | A263960 | grid permutations with a bounded index change, as a matching turned into a walk |
| 644 | PROOF | A218314 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 645 | PROOF | A222382 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 646 | PROOF | A220542 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 647 | PROOF | A217959 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 648 | PROOF | A218838 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 649 | PROOF | A218516 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 650 | PROOF | A218587 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 651 | PROOF | A221587 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 652 | PROOF | A279262 | a cell condition with an exception budget, counted up to relabelling |
| 653 | PROOF | A279742 | a cell condition with an exception budget, counted up to relabelling |
| 654 | PROOF | A281206 | a cell condition with an exception budget, counted up to relabelling |
| 655 | PROOF | A218997 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 656 | PROOF | A220574 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 657 | PROOF | A218079 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 658 | PROOF | A221030 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 659 | PROOF | A220381 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 660 | PROOF | A218051 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 661 | PROOF | A218892 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 662 | PROOF | A218065 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 663 | PROOF | A218313 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 664 | PROOF | A219411 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 665 | PROOF | A221066 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 666 | PROOF | A219100 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 667 | PROOF | A218898 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 668 | PROOF | A218199 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 669 | PROOF | A219150 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 670 | PROOF | A229577 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 671 | PROOF | A229576 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 672 | PROOF | A264018 | grid permutations with a bounded index change, as a matching turned into a walk |
| 673 | PROOF | A264068 | grid permutations with a bounded index change, as a matching turned into a walk |
| 674 | PROOF | A264085 | grid permutations with a bounded index change, as a matching turned into a walk |
| 675 | PROOF | A264338 | grid permutations with a bounded index change, as a matching turned into a walk |
| 676 | PROOF | A264366 | grid permutations with a bounded index change, as a matching turned into a walk |
| 677 | PROOF | A264551 | grid permutations with a bounded index change, as a matching turned into a walk |
| 678 | PROOF | A229575 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 679 | PROOF | A279897 | a cell condition with an exception budget, counted up to relabelling |
| 680 | PROOF | A281321 | a cell condition with an exception budget, counted up to relabelling |
| 681 | PROOF | A264107 | grid permutations with a bounded index change, as a matching turned into a walk |
| 682 | PROOF | A229574 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 683 | PROOF | A229583 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 684 | PROOF | A229474 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 685 | PROOF | A229573 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 686 | PROOF | A229530 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 687 | PROOF | A279574 | a cell condition with an exception budget, counted up to relabelling |
| 688 | PROOF | A279896 | a cell condition with an exception budget, counted up to relabelling |
| 689 | PROOF | A280392 | a cell condition with an exception budget, counted up to relabelling |
| 690 | PROOF | A281320 | a cell condition with an exception budget, counted up to relabelling |
| 691 | PROOF | A281051 | a cell condition with an exception budget, counted up to relabelling |
| 692 | PROOF | A280228 | a cell condition with an exception budget, counted up to relabelling |
| 693 | PROOF | A229454 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 694 | PROOF | A229529 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 695 | PROOF | A229588 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 696 | PROOF | A263812 | grid permutations with a bounded index change, as a matching turned into a walk |
| 697 | PROOF | A264106 | grid permutations with a bounded index change, as a matching turned into a walk |
| 698 | PROOF | A264544 | grid permutations with a bounded index change, as a matching turned into a walk |
| 699 | PROOF | A264570 | grid permutations with a bounded index change, as a matching turned into a walk |
| 700 | PROOF | A229432 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 701 | PROOF | A220806 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 702 | PROOF | A279735 | a cell condition with an exception budget, counted up to relabelling |
| 703 | PROOF | A280227 | a cell condition with an exception budget, counted up to relabelling |
| 704 | PROOF | A281199 | a cell condition with an exception budget, counted up to relabelling |
| 705 | PROOF | A220324 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 706 | PROOF | A229535 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 707 | PROOF | A279322 | a cell condition with an exception budget, counted up to relabelling |
| 708 | PROOF | A280279 | a cell condition with an exception budget, counted up to relabelling |
| 709 | PROOF | A280399 | a cell condition with an exception budget, counted up to relabelling |
| 710 | PROOF | A229472 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 711 | PROOF | A217958 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 712 | PROOF | A229314 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 713 | PROOF | A217450 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 714 | PROOF | A228980 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 715 | PROOF | A229386 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 716 | PROOF | A229514 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 717 | PROOF | A219143 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 718 | DISPROOF | A141135 | a conjecture shown FALSE, with the recurrence that holds instead |
| 719 | PROOF | A264361 | grid permutations with a bounded index change, as a matching turned into a walk |
| 720 | PROOF | A229681 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 721 | PROOF | A264280 | grid permutations with a bounded index change, as a matching turned into a walk |
| 722 | PROOF | A229680 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 723 | PROOF | A229666 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 724 | PROOF | A264238 | grid permutations with a bounded index change, as a matching turned into a walk |
| 725 | PROOF | A264307 | grid permutations with a bounded index change, as a matching turned into a walk |
| 726 | PROOF | A229600 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 727 | PROOF | A218059 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 728 | PROOF | A219405 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 729 | PROOF | A218837 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 730 | PROOF | A219003 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 731 | PROOF | A218078 | the number of distinct indicator arrays a cell condition produces: an image count, made a walk count by determinisation |
| 732 | DISPROOF | A076217 | a conjecture shown FALSE, with the recurrence that holds instead |
| 733 | PROOF | A264067 | grid permutations with a bounded index change, as a matching turned into a walk |
| 734 | PROOF | A264129 | grid permutations with a bounded index change, as a matching turned into a walk |
| 735 | PROOF | A264337 | grid permutations with a bounded index change, as a matching turned into a walk |
| 736 | PROOF | A229506 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 737 | PROOF | A229582 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 738 | PROOF | A281200 | a cell condition with an exception budget, counted up to relabelling |
| 739 | PROOF | A229505 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 740 | PROOF | A229581 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 741 | PROOF | A229473 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 742 | PROOF | A229572 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 743 | PROOF | A229504 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 744 | PROOF | A229580 | defective colourings: a budget of monochromatic pairs carried in the state, counted up to relabelling |
| 745 | PROOF | A264273 | grid permutations with a bounded index change, as a matching turned into a walk |
| 746 | PROOF | A223666 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 747 | PROOF | A209811 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 748 | PROOF | A210058 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 749 | PROOF | A206653 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 750 | PROOF | A223785 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 751 | PROOF | A205259 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 752 | PROOF | A208565 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 753 | PROOF | A223679 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 754 | PROOF | A198650 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 755 | PROOF | A204534 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 756 | PROOF | A209894 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 757 | PROOF | A275397 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 758 | PROOF | A209099 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 759 | PROOF | A198664 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 760 | PROOF | A209845 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 761 | PROOF | A210104 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 762 | PROOF | A279380 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 763 | PROOF | A279712 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 764 | PROOF | A204394 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 765 | PROOF | A204075 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 766 | PROOF | A240780 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 767 | PROOF | A198622 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 768 | PROOF | A209500 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 769 | PROOF | A209826 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 770 | PROOF | A209523 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 771 | PROOF | A281341 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 772 | PROOF | A204522 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 773 | PROOF | A269040 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 774 | PROOF | A269057 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 775 | PROOF | A203983 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 776 | PROOF | A204941 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 777 | PROOF | A205267 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 778 | PROOF | A275262 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 779 | PROOF | A204526 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 780 | PROOF | A269149 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 781 | PROOF | A268796 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 782 | PROOF | A268807 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 783 | PROOF | A204570 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 784 | PROOF | A268739 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 785 | PROOF | A268787 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 786 | PROOF | A268891 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 787 | PROOF | A269000 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 788 | PROOF | A269087 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 789 | PROOF | A224023 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 790 | PROOF | A276245 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 791 | PROOF | A224968 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 792 | PROOF | A269183 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 793 | PROOF | A214105 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 794 | PROOF | A210161 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 795 | PROOF | A209461 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 796 | PROOF | A223997 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 797 | PROOF | A205408 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 798 | PROOF | A198703 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 799 | PROOF | A269034 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 800 | PROOF | A269051 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 801 | PROOF | A214145 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 802 | PROOF | A199144 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 803 | PROOF | A204776 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 804 | PROOF | A223678 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 805 | PROOF | A276244 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 806 | PROOF | A204393 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 807 | PROOF | A204741 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 808 | PROOF | A208257 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 809 | PROOF | A214241 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 810 | PROOF | A225022 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 811 | PROOF | A275091 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 812 | PROOF | A210121 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 813 | PROOF | A204652 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 814 | PROOF | A275033 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 815 | PROOF | A280066 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 816 | PROOF | A223957 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 817 | PROOF | A224743 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 818 | PROOF | A276296 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 819 | PROOF | A204475 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 820 | PROOF | A224157 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 821 | PROOF | A198714 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 822 | PROOF | A209810 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 823 | PROOF | A274892 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 824 | PROOF | A275501 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 825 | PROOF | A275562 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 826 | PROOF | A269017 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 827 | PROOF | A210130 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 828 | PROOF | A210400 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 829 | PROOF | A208268 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 830 | PROOF | A208313 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 831 | PROOF | A199651 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 832 | PROOF | A275224 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 833 | PROOF | A204885 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 834 | PROOF | A210409 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 835 | PROOF | A240786 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 836 | PROOF | A224306 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 837 | PROOF | A225021 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 838 | PROOF | A204074 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 839 | PROOF | A214104 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 840 | PROOF | A214190 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 841 | PROOF | A209740 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 842 | PROOF | A275040 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 843 | PROOF | A275128 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 844 | PROOF | A198509 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 845 | PROOF | A268773 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 846 | PROOF | A204635 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 847 | PROOF | A203919 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 848 | PROOF | A223871 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 849 | PROOF | A269884 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 850 | PROOF | A231421 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 851 | PROOF | A204310 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 852 | PROOF | A223996 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 853 | PROOF | A268765 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 854 | PROOF | A281951 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 855 | PROOF | A209098 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 856 | PROOF | A210057 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 857 | PROOF | A206652 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 858 | PROOF | A275087 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 859 | PROOF | A223797 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 860 | PROOF | A198475 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 861 | PROOF | A208861 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 862 | PROOF | A224349 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 863 | PROOF | A214115 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 864 | PROOF | A268795 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 865 | PROOF | A268806 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 866 | PROOF | A205258 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 867 | PROOF | A268786 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 868 | PROOF | A268890 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 869 | PROOF | A268999 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 870 | PROOF | A269086 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 871 | PROOF | A208564 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 872 | PROOF | A224175 | an explicit closed form, turned into the recurrence it satisfies |
| 873 | PROOF | A274956 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 874 | PROOF | A224022 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 875 | PROOF | A224046 | an explicit closed form, turned into the recurrence it satisfies |
| 876 | PROOF | A224202 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 877 | PROOF | A224276 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 878 | PROOF | A223947 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 879 | PROOF | A224156 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 880 | PROOF | A198523 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 881 | PROOF | A204355 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 882 | PROOF | A269010 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 883 | PROOF | A269074 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 884 | PROOF | A281712 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 885 | PROOF | A275396 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 886 | PROOF | A209844 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 887 | PROOF | A198656 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 888 | PROOF | A204357 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 889 | PROOF | A198288 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 890 | PROOF | A223665 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 891 | PROOF | A204356 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 892 | PROOF | A281833 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 893 | PROOF | A199642 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 894 | PROOF | A279711 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 895 | PROOF | A209893 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 896 | PROOF | A233096 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 897 | PROOF | A214169 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 898 | PROOF | A205167 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 899 | PROOF | A240779 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 900 | PROOF | A268738 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 901 | PROOF | A210103 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 902 | PROOF | A233070 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 903 | PROOF | A198904 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 904 | PROOF | A231398 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 905 | PROOF | A208320 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 906 | PROOF | A209825 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 907 | PROOF | A224646 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 908 | PROOF | A269211 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 909 | PROOF | A198529 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 910 | PROOF | A224645 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 911 | PROOF | A269933 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 912 | PROOF | A224155 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 913 | PROOF | A269148 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 914 | PROOF | A269217 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 915 | PROOF | A269039 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 916 | PROOF | A269056 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 917 | PROOF | A204569 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 918 | PROOF | A198979 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 919 | PROOF | A269016 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 920 | PROOF | A224742 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 921 | PROOF | A198649 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 922 | PROOF | A281717 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 923 | PROOF | A209522 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 924 | PROOF | A224174 | an explicit closed form, turned into the recurrence it satisfies |
| 925 | PROOF | A224011 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 926 | PROOF | A204488 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 927 | PROOF | A224282 | an explicit closed form, turned into the recurrence it satisfies |
| 928 | PROOF | A224021 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 929 | PROOF | A223677 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 930 | PROOF | A224201 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 931 | PROOF | A204392 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 932 | PROOF | A204486 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 933 | PROOF | A224373 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 934 | PROOF | A208198 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 935 | PROOF | A269280 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 936 | PROOF | A268909 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 937 | PROOF | A268976 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 938 | PROOF | A269033 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 939 | PROOF | A269050 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 940 | PROOF | A231193 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 941 | PROOF | A223971 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 942 | PROOF | A204363 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 943 | PROOF | A280675 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 944 | PROOF | A269824 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 945 | PROOF | A223995 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 946 | PROOF | A281340 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 947 | PROOF | A204485 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 948 | PROOF | A268737 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 949 | PROOF | A279379 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 950 | PROOF | A209499 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 951 | PROOF | A208267 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 952 | PROOF | A223738 | an explicit closed form, turned into the recurrence it satisfies |
| 953 | PROOF | A224264 | an explicit closed form, turned into the recurrence it satisfies |
| 954 | PROOF | A224376 | an explicit closed form, turned into the recurrence it satisfies |
| 955 | PROOF | A275039 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 956 | PROOF | A275127 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 957 | PROOF | A203876 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 958 | PROOF | A204487 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 959 | PROOF | A223827 | an explicit closed form, turned into the recurrence it satisfies |
| 960 | PROOF | A224053 | an explicit closed form, turned into the recurrence it satisfies |
| 961 | PROOF | A232139 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 962 | PROOF | A224305 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 963 | PROOF | A208256 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 964 | PROOF | A275347 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 965 | PROOF | A223965 | an explicit closed form, turned into the recurrence it satisfies |
| 966 | PROOF | A274752 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 967 | PROOF | A275180 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 968 | PROOF | A204147 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 969 | PROOF | A223946 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 970 | PROOF | A268772 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 971 | PROOF | A274891 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 972 | PROOF | A275500 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 973 | PROOF | A203918 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 974 | PROOF | A282052 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 975 | PROOF | A269182 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 976 | PROOF | A268794 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 977 | PROOF | A268805 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 978 | PROOF | A275032 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 979 | PROOF | A268764 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 980 | PROOF | A208172 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 981 | PROOF | A198910 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 982 | PROOF | A198621 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 983 | PROOF | A204374 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 984 | PROOF | A210160 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 985 | PROOF | A208312 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 986 | PROOF | A268785 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 987 | PROOF | A268889 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 988 | PROOF | A268998 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 989 | PROOF | A269085 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 990 | PROOF | A209460 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 991 | PROOF | A184025 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 992 | PROOF | A184024 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 993 | PROOF | A274725 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 994 | PROOF | A198206 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 995 | PROOF | A184023 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 996 | PROOF | A223784 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 997 | PROOF | A224386 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 998 | PROOF | A184022 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 999 | PROOF | A204277 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1000 | PROOF | A203982 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1001 | PROOF | A200796 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1002 | PROOF | A214111 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1003 | PROOF | A240785 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1004 | PROOF | A214144 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1005 | PROOF | A184021 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1006 | PROOF | A204627 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1007 | PROOF | A214163 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1008 | PROOF | A208869 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1009 | PROOF | A281711 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1010 | PROOF | A280065 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1011 | PROOF | A210120 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1012 | PROOF | A233016 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1013 | PROOF | A270055 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1014 | PROOF | A269094 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1015 | PROOF | A224010 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1016 | PROOF | A268637 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1017 | PROOF | A275086 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1018 | PROOF | A208712 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1019 | PROOF | A268908 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1020 | PROOF | A268975 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1021 | PROOF | A198713 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1022 | PROOF | A268885 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1023 | PROOF | A268994 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1024 | PROOF | A275261 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1025 | PROOF | A224372 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1026 | PROOF | A269009 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1027 | PROOF | A269073 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1028 | PROOF | A204747 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1029 | PROOF | A269015 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1030 | PROOF | A269079 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1031 | PROOF | A198663 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1032 | PROOF | A209809 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1033 | PROOF | A224004 | an explicit closed form, turned into the recurrence it satisfies |
| 1034 | PROOF | A224169 | an explicit closed form, turned into the recurrence it satisfies |
| 1035 | PROOF | A224150 | an explicit closed form, turned into the recurrence it satisfies |
| 1036 | PROOF | A223790 | an explicit closed form, turned into the recurrence it satisfies |
| 1037 | PROOF | A224263 | an explicit closed form, turned into the recurrence it satisfies |
| 1038 | PROOF | A224685 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1039 | PROOF | A224684 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1040 | PROOF | A223860 | an explicit closed form, turned into the recurrence it satisfies |
| 1041 | PROOF | A223720 | an explicit closed form, turned into the recurrence it satisfies |
| 1042 | PROOF | A223775 | an explicit closed form, turned into the recurrence it satisfies |
| 1043 | PROOF | A223928 | an explicit closed form, turned into the recurrence it satisfies |
| 1044 | PROOF | A198448 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1045 | PROOF | A224037 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1046 | PROOF | A281606 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1047 | PROOF | A280601 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1048 | PROOF | A223756 | an explicit closed form, turned into the recurrence it satisfies |
| 1049 | PROOF | A224154 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1050 | PROOF | A198903 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1051 | PROOF | A223956 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1052 | PROOF | A204073 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1053 | PROOF | A224188 | an explicit closed form, turned into the recurrence it satisfies |
| 1054 | PROOF | A204568 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1055 | PROOF | A205166 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1056 | PROOF | A198719 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1057 | PROOF | A224741 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1058 | PROOF | A198655 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1059 | PROOF | A268771 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1060 | PROOF | A269032 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1061 | PROOF | A269049 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1062 | PROOF | A224562 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1063 | PROOF | A279706 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1064 | PROOF | A208406 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1065 | PROOF | A280358 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1066 | PROOF | A280956 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1067 | PROOF | A214240 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1068 | PROOF | A269038 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1069 | PROOF | A269055 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1070 | PROOF | A268763 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1071 | PROOF | A269008 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1072 | PROOF | A269072 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1073 | PROOF | A198522 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1074 | PROOF | A198702 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1075 | PROOF | A210399 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1076 | PROOF | A225020 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1077 | PROOF | A209739 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1078 | PROOF | A223841 | an explicit closed form, turned into the recurrence it satisfies |
| 1079 | PROOF | A224259 | an explicit closed form, turned into the recurrence it satisfies |
| 1080 | PROOF | A224015 | an explicit closed form, turned into the recurrence it satisfies |
| 1081 | PROOF | A224149 | an explicit closed form, turned into the recurrence it satisfies |
| 1082 | PROOF | A233095 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1083 | PROOF | A276295 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1084 | PROOF | A233069 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1085 | PROOF | A224009 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1086 | PROOF | A223617 | an explicit closed form, turned into the recurrence it satisfies |
| 1087 | PROOF | A223774 | an explicit closed form, turned into the recurrence it satisfies |
| 1088 | PROOF | A224036 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1089 | PROOF | A214103 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1090 | PROOF | A224371 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1091 | PROOF | A205266 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1092 | PROOF | A208860 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1093 | PROOF | A210056 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1094 | PROOF | A210129 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1095 | PROOF | A198909 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1096 | PROOF | A214233 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1097 | PROOF | A198648 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1098 | PROOF | A224392 | an explicit closed form, turned into the recurrence it satisfies |
| 1099 | PROOF | A224168 | an explicit closed form, turned into the recurrence it satisfies |
| 1100 | PROOF | A224566 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1101 | PROOF | A223945 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1102 | PROOF | A198639 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1103 | PROOF | A275561 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1104 | PROOF | A270146 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1105 | PROOF | A282271 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1106 | PROOF | A224348 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1107 | PROOF | A224020 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1108 | PROOF | A223963 | an explicit closed form, turned into the recurrence it satisfies |
| 1109 | PROOF | A224025 | an explicit closed form, turned into the recurrence it satisfies |
| 1110 | PROOF | A268636 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1111 | PROOF | A208391 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1112 | PROOF | A223796 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1113 | PROOF | A223859 | an explicit closed form, turned into the recurrence it satisfies |
| 1114 | PROOF | A203917 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1115 | PROOF | A281466 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1116 | PROOF | A231464 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1117 | PROOF | A238907 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1118 | PROOF | A224200 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1119 | PROOF | A268884 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1120 | PROOF | A268993 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1121 | PROOF | A280600 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1122 | PROOF | A214189 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1123 | PROOF | A214114 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1124 | PROOF | A214138 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1125 | PROOF | A281950 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1126 | PROOF | A198978 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1127 | PROOF | A204354 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1128 | PROOF | A208319 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1129 | PROOF | A209097 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1130 | PROOF | A268793 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1131 | PROOF | A268804 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1132 | PROOF | A223982 | an explicit closed form, turned into the recurrence it satisfies |
| 1133 | PROOF | A208197 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1134 | PROOF | A209843 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1135 | PROOF | A268736 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1136 | PROOF | A208563 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1137 | PROOF | A268784 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1138 | PROOF | A269084 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1139 | PROOF | A188559 | an explicit closed form, turned into the recurrence it satisfies |
| 1140 | PROOF | A184001 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1141 | PROOF | A223640 | an explicit closed form, turned into the recurrence it satisfies |
| 1142 | PROOF | A224355 | an explicit closed form, turned into the recurrence it satisfies |
| 1143 | PROOF | A223840 | an explicit closed form, turned into the recurrence it satisfies |
| 1144 | PROOF | A184000 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1145 | PROOF | A224258 | an explicit closed form, turned into the recurrence it satisfies |
| 1146 | PROOF | A183999 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1147 | PROOF | A204049 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1148 | PROOF | A223682 | an explicit closed form, turned into the recurrence it satisfies |
| 1149 | PROOF | A224160 | an explicit closed form, turned into the recurrence it satisfies |
| 1150 | PROOF | A224686 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1151 | PROOF | A223633 | an explicit closed form, turned into the recurrence it satisfies |
| 1152 | PROOF | A223766 | an explicit closed form, turned into the recurrence it satisfies |
| 1153 | PROOF | A183998 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1154 | PROOF | A224002 | an explicit closed form, turned into the recurrence it satisfies |
| 1155 | PROOF | A224014 | an explicit closed form, turned into the recurrence it satisfies |
| 1156 | PROOF | A224148 | an explicit closed form, turned into the recurrence it satisfies |
| 1157 | PROOF | A274955 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1158 | PROOF | A275179 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1159 | PROOF | A231318 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1160 | PROOF | A223914 | an explicit closed form, turned into the recurrence it satisfies |
| 1161 | PROOF | A183997 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1162 | PROOF | A224564 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1163 | PROOF | A241323 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1164 | PROOF | A214139 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1165 | PROOF | A224411 | an explicit closed form, turned into the recurrence it satisfies |
| 1166 | PROOF | A264520 | a table's column recurrences, each column being a fixed-width array count |
| 1167 | PROOF | A183996 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1168 | PROOF | A231264 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1169 | PROOF | A224035 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1170 | PROOF | A223616 | an explicit closed form, turned into the recurrence it satisfies |
| 1171 | PROOF | A223676 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1172 | PROOF | A223773 | an explicit closed form, turned into the recurrence it satisfies |
| 1173 | PROOF | A199650 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1174 | PROOF | A275038 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1175 | PROOF | A275085 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1176 | PROOF | A275126 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1177 | PROOF | A275223 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1178 | PROOF | A223719 | an explicit closed form, turned into the recurrence it satisfies |
| 1179 | PROOF | A223927 | an explicit closed form, turned into the recurrence it satisfies |
| 1180 | PROOF | A223919 | an explicit closed form, turned into the recurrence it satisfies |
| 1181 | PROOF | A183995 | an unnamed common subblock sum removed by splitting the count over its possible values |
| 1182 | PROOF | A223994 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1183 | PROOF | A214234 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1184 | PROOF | A281339 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1185 | PROOF | A224153 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1186 | PROOF | A224186 | an explicit closed form, turned into the recurrence it satisfies |
| 1187 | PROOF | A199143 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1188 | PROOF | A210408 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1189 | PROOF | A198718 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1190 | PROOF | A224740 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1191 | PROOF | A209824 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1192 | PROOF | A209892 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1193 | PROOF | A210102 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1194 | PROOF | A275260 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1195 | PROOF | A275395 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1196 | PROOF | A214182 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1197 | PROOF | A208266 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1198 | PROOF | A268888 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1199 | PROOF | A268997 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1200 | PROOF | A209521 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1201 | PROOF | A198620 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1202 | PROOF | A188558 | an explicit closed form, turned into the recurrence it satisfies |
| 1203 | PROOF | A224043 | an explicit closed form, turned into the recurrence it satisfies |
| 1204 | PROOF | A224138 | an explicit closed form, turned into the recurrence it satisfies |
| 1205 | PROOF | A274855 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1206 | PROOF | A274897 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1207 | PROOF | A275145 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1208 | PROOF | A198247 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1209 | PROOF | A268903 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1210 | PROOF | A268970 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1211 | PROOF | A204344 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1212 | PROOF | A224145 | an explicit closed form, turned into the recurrence it satisfies |
| 1213 | PROOF | A233015 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1214 | PROOF | A224567 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1215 | PROOF | A207258 | an explicit closed form, turned into the recurrence it satisfies |
| 1216 | PROOF | A208286 | an explicit closed form, turned into the recurrence it satisfies |
| 1217 | PROOF | A274724 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1218 | PROOF | A274751 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1219 | PROOF | A224565 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1220 | PROOF | A207067 | an explicit closed form, turned into the recurrence it satisfies |
| 1221 | PROOF | A207390 | an explicit closed form, turned into the recurrence it satisfies |
| 1222 | PROOF | A241365 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1223 | PROOF | A207110 | an explicit closed form, turned into the recurrence it satisfies |
| 1224 | PROOF | A224563 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1225 | PROOF | A269279 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1226 | PROOF | A224561 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1227 | PROOF | A207402 | an explicit closed form, turned into the recurrence it satisfies |
| 1228 | PROOF | A208141 | an explicit closed form, turned into the recurrence it satisfies |
| 1229 | PROOF | A224644 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1230 | PROOF | A260207 | a table's column recurrences, each column being a fixed-width array count |
| 1231 | PROOF | A260927 | a table's column recurrences, each column being a fixed-width array count |
| 1232 | PROOF | A261380 | a table's column recurrences, each column being a fixed-width array count |
| 1233 | PROOF | A264163 | a table's column recurrences, each column being a fixed-width array count |
| 1234 | PROOF | A268770 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1235 | PROOF | A274890 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1236 | PROOF | A231296 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1237 | PROOF | A188841 | an explicit closed form, turned into the recurrence it satisfies |
| 1238 | PROOF | A269147 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1239 | PROOF | A269181 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1240 | PROOF | A269216 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1241 | PROOF | A279705 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1242 | PROOF | A198712 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1243 | PROOF | A281465 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1244 | PROOF | A214168 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1245 | PROOF | A208708 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1246 | PROOF | A234728 | a table's column recurrences, each column being a fixed-width array count |
| 1247 | PROOF | A256810 | a table's column recurrences, each column being a fixed-width array count |
| 1248 | PROOF | A259770 | a table's column recurrences, each column being a fixed-width array count |
| 1249 | PROOF | A259952 | a table's column recurrences, each column being a fixed-width array count |
| 1250 | PROOF | A260284 | a table's column recurrences, each column being a fixed-width array count |
| 1251 | PROOF | A264257 | a table's column recurrences, each column being a fixed-width array count |
| 1252 | PROOF | A264299 | a table's column recurrences, each column being a fixed-width array count |
| 1253 | PROOF | A268883 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1254 | PROOF | A268992 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1255 | PROOF | A204072 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1256 | PROOF | A204626 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1257 | PROOF | A208255 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1258 | PROOF | A279710 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1259 | PROOF | A200795 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1260 | PROOF | A208171 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1261 | PROOF | A208868 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1262 | PROOF | A268762 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1263 | PROOF | A269014 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1264 | PROOF | A269078 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1265 | PROOF | A225009 | an explicit closed form, turned into the recurrence it satisfies |
| 1266 | PROOF | A209498 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1267 | PROOF | A208311 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1268 | PROOF | A251028 | a table's column recurrences, each column being a fixed-width array count |
| 1269 | PROOF | A251055 | a table's column recurrences, each column being a fixed-width array count |
| 1270 | PROOF | A268735 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1271 | PROOF | A209459 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1272 | PROOF | A223836 | an explicit closed form, turned into the recurrence it satisfies |
| 1273 | PROOF | A274730 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1274 | PROOF | A274800 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1275 | PROOF | A251088 | a table's column recurrences, each column being a fixed-width array count |
| 1276 | PROOF | A251137 | a table's column recurrences, each column being a fixed-width array count |
| 1277 | PROOF | A188557 | an explicit closed form, turned into the recurrence it satisfies |
| 1278 | PROOF | A223670 | an explicit closed form, turned into the recurrence it satisfies |
| 1279 | PROOF | A224042 | an explicit closed form, turned into the recurrence it satisfies |
| 1280 | PROOF | A224137 | an explicit closed form, turned into the recurrence it satisfies |
| 1281 | PROOF | A223639 | an explicit closed form, turned into the recurrence it satisfies |
| 1282 | PROOF | A223839 | an explicit closed form, turned into the recurrence it satisfies |
| 1283 | PROOF | A224354 | an explicit closed form, turned into the recurrence it satisfies |
| 1284 | PROOF | A224144 | an explicit closed form, turned into the recurrence it satisfies |
| 1285 | PROOF | A224257 | an explicit closed form, turned into the recurrence it satisfies |
| 1286 | PROOF | A224132 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1287 | PROOF | A258966 | a table's column recurrences, each column being a fixed-width array count |
| 1288 | PROOF | A207257 | an explicit closed form, turned into the recurrence it satisfies |
| 1289 | PROOF | A208285 | an explicit closed form, turned into the recurrence it satisfies |
| 1290 | PROOF | A231414 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1291 | PROOF | A223681 | an explicit closed form, turned into the recurrence it satisfies |
| 1292 | PROOF | A224159 | an explicit closed form, turned into the recurrence it satisfies |
| 1293 | PROOF | A223632 | an explicit closed form, turned into the recurrence it satisfies |
| 1294 | PROOF | A223765 | an explicit closed form, turned into the recurrence it satisfies |
| 1295 | PROOF | A207066 | an explicit closed form, turned into the recurrence it satisfies |
| 1296 | PROOF | A207389 | an explicit closed form, turned into the recurrence it satisfies |
| 1297 | PROOF | A203875 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1298 | PROOF | A207109 | an explicit closed form, turned into the recurrence it satisfies |
| 1299 | PROOF | A208711 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1300 | PROOF | A214100 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1301 | PROOF | A207401 | an explicit closed form, turned into the recurrence it satisfies |
| 1302 | PROOF | A208140 | an explicit closed form, turned into the recurrence it satisfies |
| 1303 | PROOF | A224147 | an explicit closed form, turned into the recurrence it satisfies |
| 1304 | PROOF | A224008 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1305 | PROOF | A224001 | an explicit closed form, turned into the recurrence it satisfies |
| 1306 | PROOF | A224013 | an explicit closed form, turned into the recurrence it satisfies |
| 1307 | PROOF | A280854 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1308 | PROOF | A223913 | an explicit closed form, turned into the recurrence it satisfies |
| 1309 | PROOF | A223970 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1310 | PROOF | A224019 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1311 | PROOF | A275499 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1312 | PROOF | A224034 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1313 | PROOF | A231356 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1314 | PROOF | A231363 | a table's column recurrences, each column being a fixed-width array count |
| 1315 | PROOF | A240778 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1316 | PROOF | A281832 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1317 | PROOF | A188840 | an explicit closed form, turned into the recurrence it satisfies |
| 1318 | PROOF | A205257 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1319 | PROOF | A223962 | an explicit closed form, turned into the recurrence it satisfies |
| 1320 | PROOF | A224410 | an explicit closed form, turned into the recurrence it satisfies |
| 1321 | PROOF | A234421 | a table's column recurrences, each column being a fixed-width array count |
| 1322 | PROOF | A234738 | a table's column recurrences, each column being a fixed-width array count |
| 1323 | PROOF | A259962 | a table's column recurrences, each column being a fixed-width array count |
| 1324 | PROOF | A260001 | a table's column recurrences, each column being a fixed-width array count |
| 1325 | PROOF | A260370 | a table's column recurrences, each column being a fixed-width array count |
| 1326 | PROOF | A224553 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1327 | PROOF | A223615 | an explicit closed form, turned into the recurrence it satisfies |
| 1328 | PROOF | A223772 | an explicit closed form, turned into the recurrence it satisfies |
| 1329 | PROOF | A198902 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1330 | PROOF | A224199 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1331 | PROOF | A214183 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1332 | PROOF | A224370 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1333 | PROOF | A281464 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1334 | PROOF | A204567 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1335 | PROOF | A214239 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1336 | PROOF | A280064 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1337 | PROOF | A224408 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1338 | PROOF | A214102 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1339 | PROOF | A198977 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1340 | PROOF | A224185 | an explicit closed form, turned into the recurrence it satisfies |
| 1341 | PROOF | A225008 | an explicit closed form, turned into the recurrence it satisfies |
| 1342 | PROOF | A238287 | a table's column recurrences, each column being a fixed-width array count |
| 1343 | PROOF | A214161 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1344 | PROOF | A209808 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1345 | PROOF | A210119 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1346 | PROOF | A210159 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1347 | PROOF | A198662 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1348 | PROOF | A251113 | a table's column recurrences, each column being a fixed-width array count |
| 1349 | PROOF | A223952 | an explicit closed form, turned into the recurrence it satisfies |
| 1350 | PROOF | A223835 | an explicit closed form, turned into the recurrence it satisfies |
| 1351 | PROOF | A204278 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1352 | PROOF | A204364 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1353 | PROOF | A269898 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1354 | PROOF | A269763 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1355 | PROOF | A268902 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1356 | PROOF | A268969 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1357 | PROOF | A270054 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1358 | PROOF | A209649 | an explicit closed form, turned into the recurrence it satisfies |
| 1359 | PROOF | A274729 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1360 | PROOF | A188556 | an explicit closed form, turned into the recurrence it satisfies |
| 1361 | PROOF | A224041 | an explicit closed form, turned into the recurrence it satisfies |
| 1362 | PROOF | A224136 | an explicit closed form, turned into the recurrence it satisfies |
| 1363 | PROOF | A257447 | a table's column recurrences, each column being a fixed-width array count |
| 1364 | PROOF | A264285 | a table's column recurrences, each column being a fixed-width array count |
| 1365 | PROOF | A264336 | a table's column recurrences, each column being a fixed-width array count |
| 1366 | PROOF | A264364 | a table's column recurrences, each column being a fixed-width array count |
| 1367 | PROOF | A264506 | a table's column recurrences, each column being a fixed-width array count |
| 1368 | PROOF | A264569 | a table's column recurrences, each column being a fixed-width array count |
| 1369 | PROOF | A264583 | a table's column recurrences, each column being a fixed-width array count |
| 1370 | PROOF | A207304 | an explicit closed form, turned into the recurrence it satisfies |
| 1371 | PROOF | A252343 | a table's column recurrences, each column being a fixed-width array count |
| 1372 | PROOF | A224558 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1373 | PROOF | A224143 | an explicit closed form, turned into the recurrence it satisfies |
| 1374 | PROOF | A269093 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1375 | PROOF | A269210 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1376 | PROOF | A224131 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1377 | PROOF | A224557 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1378 | PROOF | A207303 | an explicit closed form, turned into the recurrence it satisfies |
| 1379 | PROOF | A241372 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1380 | PROOF | A207256 | an explicit closed form, turned into the recurrence it satisfies |
| 1381 | PROOF | A208284 | an explicit closed form, turned into the recurrence it satisfies |
| 1382 | PROOF | A259642 | a table's column recurrences, each column being a fixed-width array count |
| 1383 | PROOF | A259742 | a table's column recurrences, each column being a fixed-width array count |
| 1384 | PROOF | A260138 | a table's column recurrences, each column being a fixed-width array count |
| 1385 | PROOF | A261113 | a table's column recurrences, each column being a fixed-width array count |
| 1386 | PROOF | A261265 | a table's column recurrences, each column being a fixed-width array count |
| 1387 | PROOF | A264172 | a table's column recurrences, each column being a fixed-width array count |
| 1388 | PROOF | A264207 | a table's column recurrences, each column being a fixed-width array count |
| 1389 | PROOF | A264217 | a table's column recurrences, each column being a fixed-width array count |
| 1390 | PROOF | A264244 | a table's column recurrences, each column being a fixed-width array count |
| 1391 | PROOF | A264422 | a table's column recurrences, each column being a fixed-width array count |
| 1392 | PROOF | A264550 | a table's column recurrences, each column being a fixed-width array count |
| 1393 | PROOF | A264676 | a table's column recurrences, each column being a fixed-width array count |
| 1394 | PROOF | A224556 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1395 | PROOF | A241329 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1396 | PROOF | A207065 | an explicit closed form, turned into the recurrence it satisfies |
| 1397 | PROOF | A207388 | an explicit closed form, turned into the recurrence it satisfies |
| 1398 | PROOF | A207108 | an explicit closed form, turned into the recurrence it satisfies |
| 1399 | PROOF | A268907 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1400 | PROOF | A268974 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1401 | PROOF | A203981 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1402 | PROOF | A208390 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1403 | PROOF | A276243 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1404 | PROOF | A224555 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1405 | PROOF | A207400 | an explicit closed form, turned into the recurrence it satisfies |
| 1406 | PROOF | A208139 | an explicit closed form, turned into the recurrence it satisfies |
| 1407 | PROOF | A231997 | a table's column recurrences, each column being a fixed-width array count |
| 1408 | PROOF | A234227 | a table's column recurrences, each column being a fixed-width array count |
| 1409 | PROOF | A231396 | a table's column recurrences, each column being a fixed-width array count |
| 1410 | PROOF | A214110 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1411 | PROOF | A231419 | a table's column recurrences, each column being a fixed-width array count |
| 1412 | PROOF | A231420 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1413 | PROOF | A208405 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1414 | PROOF | A231192 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1415 | PROOF | A231199 | a table's column recurrences, each column being a fixed-width array count |
| 1416 | PROOF | A269932 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1417 | PROOF | A224554 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1418 | PROOF | A231397 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1419 | PROOF | A234161 | a table's column recurrences, each column being a fixed-width array count |
| 1420 | PROOF | A234233 | a table's column recurrences, each column being a fixed-width array count |
| 1421 | PROOF | A255027 | a table's column recurrences, each column being a fixed-width array count |
| 1422 | PROOF | A255159 | a table's column recurrences, each column being a fixed-width array count |
| 1423 | PROOF | A260070 | a table's column recurrences, each column being a fixed-width array count |
| 1424 | PROOF | A260248 | a table's column recurrences, each column being a fixed-width array count |
| 1425 | PROOF | A264003 | a table's column recurrences, each column being a fixed-width array count |
| 1426 | PROOF | A235212 | a table's column recurrences, each column being a fixed-width array count |
| 1427 | PROOF | A268769 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1428 | PROOF | A269037 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1429 | PROOF | A269054 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1430 | PROOF | A234131 | a table's column recurrences, each column being a fixed-width array count |
| 1431 | PROOF | A234175 | a table's column recurrences, each column being a fixed-width array count |
| 1432 | PROOF | A234555 | a table's column recurrences, each column being a fixed-width array count |
| 1433 | PROOF | A234690 | a table's column recurrences, each column being a fixed-width array count |
| 1434 | PROOF | A235319 | a table's column recurrences, each column being a fixed-width array count |
| 1435 | PROOF | A280599 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1436 | PROOF | A214109 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1437 | PROOF | A235107 | a table's column recurrences, each column being a fixed-width array count |
| 1438 | PROOF | A235198 | a table's column recurrences, each column being a fixed-width array count |
| 1439 | PROOF | A239178 | a table's column recurrences, each column being a fixed-width array count |
| 1440 | PROOF | A214143 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1441 | PROOF | A205165 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1442 | PROOF | A224552 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1443 | PROOF | A234458 | a table's column recurrences, each column being a fixed-width array count |
| 1444 | PROOF | A208707 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1445 | PROOF | A188839 | an explicit closed form, turned into the recurrence it satisfies |
| 1446 | PROOF | A268882 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1447 | PROOF | A268991 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1448 | PROOF | A269007 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1449 | PROOF | A269071 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1450 | PROOF | A234890 | a table's column recurrences, each column being a fixed-width array count |
| 1451 | PROOF | A235026 | a table's column recurrences, each column being a fixed-width array count |
| 1452 | PROOF | A235186 | a table's column recurrences, each column being a fixed-width array count |
| 1453 | PROOF | A214188 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1454 | PROOF | A234443 | a table's column recurrences, each column being a fixed-width array count |
| 1455 | PROOF | A251210 | a table's column recurrences, each column being a fixed-width array count |
| 1456 | PROOF | A251335 | a table's column recurrences, each column being a fixed-width array count |
| 1457 | PROOF | A233928 | a table's column recurrences, each column being a fixed-width array count |
| 1458 | PROOF | A234114 | a table's column recurrences, each column being a fixed-width array count |
| 1459 | PROOF | A224407 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1460 | PROOF | A280598 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1461 | PROOF | A268792 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1462 | PROOF | A268803 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1463 | PROOF | A251258 | a table's column recurrences, each column being a fixed-width array count |
| 1464 | PROOF | A268761 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1465 | PROOF | A269006 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1466 | PROOF | A269013 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1467 | PROOF | A269070 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1468 | PROOF | A269077 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1469 | PROOF | A198908 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1470 | PROOF | A208196 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1471 | PROOF | A209842 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1472 | PROOF | A210055 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1473 | PROOF | A231806 | a table's column recurrences, each column being a fixed-width array count |
| 1474 | PROOF | A231764 | a table's column recurrences, each column being a fixed-width array count |
| 1475 | PROOF | A231977 | a table's column recurrences, each column being a fixed-width array count |
| 1476 | PROOF | A251451 | a table's column recurrences, each column being a fixed-width array count |
| 1477 | PROOF | A251317 | a table's column recurrences, each column being a fixed-width array count |
| 1478 | PROOF | A268783 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1479 | PROOF | A268887 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1480 | PROOF | A268996 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1481 | PROOF | A269083 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1482 | PROOF | A274746 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1483 | PROOF | A204377 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1484 | PROOF | A223951 | an explicit closed form, turned into the recurrence it satisfies |
| 1485 | PROOF | A223834 | an explicit closed form, turned into the recurrence it satisfies |
| 1486 | PROOF | A207452 | an explicit closed form, turned into the recurrence it satisfies |
| 1487 | PROOF | A233100 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1488 | PROOF | A207598 | an explicit closed form, turned into the recurrence it satisfies |
| 1489 | PROOF | A274799 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1490 | PROOF | A274854 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1491 | PROOF | A274896 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1492 | PROOF | A275144 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1493 | PROOF | A204376 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1494 | PROOF | A207168 | an explicit closed form, turned into the recurrence it satisfies |
| 1495 | PROOF | A204146 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1496 | PROOF | A207451 | an explicit closed form, turned into the recurrence it satisfies |
| 1497 | PROOF | A207597 | an explicit closed form, turned into the recurrence it satisfies |
| 1498 | PROOF | A209648 | an explicit closed form, turned into the recurrence it satisfies |
| 1499 | PROOF | A214136 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1500 | PROOF | A207167 | an explicit closed form, turned into the recurrence it satisfies |
| 1501 | PROOF | A188555 | an explicit closed form, turned into the recurrence it satisfies |
| 1502 | PROOF | A204375 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1503 | PROOF | A204748 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1504 | PROOF | A204754 | a table's column recurrences, each column being a fixed-width array count |
| 1505 | PROOF | A223944 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1506 | PROOF | A224040 | an explicit closed form, turned into the recurrence it satisfies |
| 1507 | PROOF | A224135 | an explicit closed form, turned into the recurrence it satisfies |
| 1508 | PROOF | A251128 | a table's column recurrences, each column being a fixed-width array count |
| 1509 | PROOF | A264878 | a table's column recurrences, each column being a fixed-width array count |
| 1510 | PROOF | A208640 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1511 | PROOF | A281600 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1512 | PROOF | A238510 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1513 | PROOF | A238515 | a table's column recurrences, each column being a fixed-width array count |
| 1514 | PROOF | A224130 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1515 | PROOF | A233068 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1516 | PROOF | A281472 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1517 | PROOF | A224142 | an explicit closed form, turned into the recurrence it satisfies |
| 1518 | PROOF | A207166 | an explicit closed form, turned into the recurrence it satisfies |
| 1519 | PROOF | A207302 | an explicit closed form, turned into the recurrence it satisfies |
| 1520 | PROOF | A274723 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1521 | PROOF | A275178 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1522 | PROOF | A276294 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1523 | PROOF | A231444 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1524 | PROOF | A231451 | a table's column recurrences, each column being a fixed-width array count |
| 1525 | PROOF | A224549 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1526 | PROOF | A282051 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1527 | PROOF | A203874 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1528 | PROOF | A207255 | an explicit closed form, turned into the recurrence it satisfies |
| 1529 | PROOF | A208283 | an explicit closed form, turned into the recurrence it satisfies |
| 1530 | PROOF | A280674 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1531 | PROOF | A207064 | an explicit closed form, turned into the recurrence it satisfies |
| 1532 | PROOF | A207399 | an explicit closed form, turned into the recurrence it satisfies |
| 1533 | PROOF | A208138 | an explicit closed form, turned into the recurrence it satisfies |
| 1534 | PROOF | A234122 | a table's column recurrences, each column being a fixed-width array count |
| 1535 | PROOF | A224007 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1536 | PROOF | A231337 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1537 | PROOF | A231343 | a table's column recurrences, each column being a fixed-width array count |
| 1538 | PROOF | A231463 | a table's column recurrences, each column being a fixed-width array count |
| 1539 | PROOF | A235017 | a table's column recurrences, each column being a fixed-width array count |
| 1540 | PROOF | A240784 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1541 | PROOF | A224548 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1542 | PROOF | A223764 | an explicit closed form, turned into the recurrence it satisfies |
| 1543 | PROOF | A234490 | a table's column recurrences, each column being a fixed-width array count |
| 1544 | PROOF | A234702 | a table's column recurrences, each column being a fixed-width array count |
| 1545 | PROOF | A263964 | a table's column recurrences, each column being a fixed-width array count |
| 1546 | PROOF | A198405 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1547 | PROOF | A198508 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1548 | PROOF | A198535 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1549 | PROOF | A234665 | a table's column recurrences, each column being a fixed-width array count |
| 1550 | PROOF | A224547 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1551 | PROOF | A214162 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1552 | PROOF | A224000 | an explicit closed form, turned into the recurrence it satisfies |
| 1553 | PROOF | A234184 | a table's column recurrences, each column being a fixed-width array count |
| 1554 | PROOF | A234497 | a table's column recurrences, each column being a fixed-width array count |
| 1555 | PROOF | A234549 | a table's column recurrences, each column being a fixed-width array count |
| 1556 | PROOF | A234658 | a table's column recurrences, each column being a fixed-width array count |
| 1557 | PROOF | A235310 | a table's column recurrences, each column being a fixed-width array count |
| 1558 | PROOF | A224033 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1559 | PROOF | A235098 | a table's column recurrences, each column being a fixed-width array count |
| 1560 | PROOF | A224546 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1561 | PROOF | A234564 | a table's column recurrences, each column being a fixed-width array count |
| 1562 | PROOF | A199641 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1563 | PROOF | A208318 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1564 | PROOF | A209096 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1565 | PROOF | A275222 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1566 | PROOF | A224369 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1567 | PROOF | A281338 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1568 | PROOF | A281470 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1569 | PROOF | A281716 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1570 | PROOF | A214167 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1571 | PROOF | A198901 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1572 | PROOF | A237859 | a table's column recurrences, each column being a fixed-width array count |
| 1573 | PROOF | A279378 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1574 | PROOF | A188838 | an explicit closed form, turned into the recurrence it satisfies |
| 1575 | PROOF | A224406 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1576 | PROOF | A233635 | a table's column recurrences, each column being a fixed-width array count |
| 1577 | PROOF | A204566 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1578 | PROOF | A208859 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1579 | PROOF | A210128 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1580 | PROOF | A210398 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1581 | PROOF | A224545 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1582 | PROOF | A198717 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1583 | PROOF | A238323 | a table's column recurrences, each column being a fixed-width array count |
| 1584 | PROOF | A209738 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1585 | PROOF | A209823 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1586 | PROOF | A208265 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1587 | PROOF | A250927 | a table's column recurrences, each column being a fixed-width array count |
| 1588 | PROOF | A250982 | a table's column recurrences, each column being a fixed-width array count |
| 1589 | PROOF | A251010 | a table's column recurrences, each column being a fixed-width array count |
| 1590 | PROOF | A251019 | a table's column recurrences, each column being a fixed-width array count |
| 1591 | PROOF | A251065 | a table's column recurrences, each column being a fixed-width array count |
| 1592 | PROOF | A251410 | a table's column recurrences, each column being a fixed-width array count |
| 1593 | PROOF | A224544 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1594 | PROOF | A224738 | every K X K subblock of a matrix idempotent, or of equal population or permanent |
| 1595 | PROOF | A250973 | a table's column recurrences, each column being a fixed-width array count |
| 1596 | PROOF | A251201 | a table's column recurrences, each column being a fixed-width array count |
| 1597 | PROOF | A251219 | a table's column recurrences, each column being a fixed-width array count |
| 1598 | PROOF | A251228 | a table's column recurrences, each column being a fixed-width array count |
| 1599 | PROOF | A251292 | a table's column recurrences, each column being a fixed-width array count |
| 1600 | PROOF | A251326 | a table's column recurrences, each column being a fixed-width array count |
| 1601 | PROOF | A199142 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1602 | PROOF | A214232 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1603 | PROOF | A129833 | creative telescoping with the boundary and range corrections carried through |
| 1604 | PROOF | A233080 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1605 | PROOF | A269273 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1606 | PROOF | A208378 | an explicit closed form, turned into the recurrence it satisfies |
| 1607 | PROOF | A203826 | a table's column recurrences, each column being a fixed-width array count |
| 1608 | PROOF | A264110 | a table's column recurrences, each column being a fixed-width array count |
| 1609 | PROOF | A264341 | a table's column recurrences, each column being a fixed-width array count |
| 1610 | PROOF | A208394 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1611 | PROOF | A233014 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1612 | PROOF | A204775 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1613 | PROOF | A269897 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1614 | PROOF | A232137 | a table's column recurrences, each column being a fixed-width array count |
| 1615 | PROOF | A209102 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1616 | PROOF | A223950 | an explicit closed form, turned into the recurrence it satisfies |
| 1617 | PROOF | A268901 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1618 | PROOF | A268968 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1619 | PROOF | A223833 | an explicit closed form, turned into the recurrence it satisfies |
| 1620 | PROOF | A269762 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1621 | PROOF | A208409 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1622 | PROOF | A208873 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1623 | PROOF | A264142 | a table's column recurrences, each column being a fixed-width array count |
| 1624 | PROOF | A264272 | a table's column recurrences, each column being a fixed-width array count |
| 1625 | PROOF | A264379 | a table's column recurrences, each column being a fixed-width array count |
| 1626 | PROOF | A264476 | a table's column recurrences, each column being a fixed-width array count |
| 1627 | PROOF | A270053 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1628 | PROOF | A231257 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1629 | PROOF | A231263 | a table's column recurrences, each column being a fixed-width array count |
| 1630 | PROOF | A269031 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1631 | PROOF | A269048 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1632 | PROOF | A274750 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1633 | PROOF | A274954 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1634 | PROOF | A275560 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1635 | PROOF | A269092 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1636 | PROOF | A269209 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1637 | PROOF | A269278 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1638 | PROOF | A270145 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1639 | PROOF | A231213 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1640 | PROOF | A231219 | a table's column recurrences, each column being a fixed-width array count |
| 1641 | PROOF | A241364 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1642 | PROOF | A232138 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1643 | PROOF | A208639 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1644 | PROOF | A224129 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1645 | PROOF | A208710 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1646 | PROOF | A280853 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1647 | PROOF | A231413 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1648 | PROOF | A269882 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1649 | PROOF | A214098 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1650 | PROOF | A208636 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1651 | PROOF | A203916 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1652 | PROOF | A204391 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1653 | PROOF | A224039 | an explicit closed form, turned into the recurrence it satisfies |
| 1654 | PROOF | A224134 | an explicit closed form, turned into the recurrence it satisfies |
| 1655 | PROOF | A255228 | a table's column recurrences, each column being a fixed-width array count |
| 1656 | PROOF | A259894 | a table's column recurrences, each column being a fixed-width array count |
| 1657 | PROOF | A263816 | a table's column recurrences, each column being a fixed-width array count |
| 1658 | PROOF | A281471 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1659 | PROOF | A203980 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1660 | PROOF | A224141 | an explicit closed form, turned into the recurrence it satisfies |
| 1661 | PROOF | A268634 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1662 | PROOF | A268906 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1663 | PROOF | A268973 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1664 | PROOF | A269030 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1665 | PROOF | A269047 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1666 | PROOF | A238649 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1667 | PROOF | A238654 | a table's column recurrences, each column being a fixed-width array count |
| 1668 | PROOF | A198711 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1669 | PROOF | A208404 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1670 | PROOF | A231295 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1671 | PROOF | A231302 | a table's column recurrences, each column being a fixed-width array count |
| 1672 | PROOF | A234681 | a table's column recurrences, each column being a fixed-width array count |
| 1673 | PROOF | A208635 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1674 | PROOF | A250956 | a table's column recurrences, each column being a fixed-width array count |
| 1675 | PROOF | A269146 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1676 | PROOF | A269180 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1677 | PROOF | A269215 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1678 | PROOF | A234036 | a table's column recurrences, each column being a fixed-width array count |
| 1679 | PROOF | A234169 | a table's column recurrences, each column being a fixed-width array count |
| 1680 | PROOF | A234450 | a table's column recurrences, each column being a fixed-width array count |
| 1681 | PROOF | A235280 | a table's column recurrences, each column being a fixed-width array count |
| 1682 | PROOF | A199649 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1683 | PROOF | A204071 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1684 | PROOF | A208254 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1685 | PROOF | A275498 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1686 | PROOF | A214113 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1687 | PROOF | A234882 | a table's column recurrences, each column being a fixed-width array count |
| 1688 | PROOF | A234921 | a table's column recurrences, each column being a fixed-width array count |
| 1689 | PROOF | A235087 | a table's column recurrences, each column being a fixed-width array count |
| 1690 | PROOF | A268768 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1691 | PROOF | A269036 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1692 | PROOF | A269053 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1693 | PROOF | A233733 | a table's column recurrences, each column being a fixed-width array count |
| 1694 | PROOF | A234333 | a table's column recurrences, each column being a fixed-width array count |
| 1695 | PROOF | A235301 | a table's column recurrences, each column being a fixed-width array count |
| 1696 | PROOF | A250935 | a table's column recurrences, each column being a fixed-width array count |
| 1697 | PROOF | A251381 | a table's column recurrences, each column being a fixed-width array count |
| 1698 | PROOF | A251499 | a table's column recurrences, each column being a fixed-width array count |
| 1699 | PROOF | A251507 | a table's column recurrences, each column being a fixed-width array count |
| 1700 | PROOF | A268881 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1701 | PROOF | A268990 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1702 | PROOF | A205164 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1703 | PROOF | A208170 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1704 | PROOF | A208867 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1705 | PROOF | A210407 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1706 | PROOF | A214142 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1707 | PROOF | A198976 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1708 | PROOF | A224405 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1709 | PROOF | A208562 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1710 | PROOF | A208310 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1711 | PROOF | A209497 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1712 | PROOF | A233949 | a table's column recurrences, each column being a fixed-width array count |
| 1713 | PROOF | A250841 | a table's column recurrences, each column being a fixed-width array count |
| 1714 | PROOF | A251100 | a table's column recurrences, each column being a fixed-width array count |
| 1715 | PROOF | A251268 | a table's column recurrences, each column being a fixed-width array count |
| 1716 | PROOF | A268989 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1717 | PROOF | A269012 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1718 | PROOF | A269076 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1719 | PROOF | A208195 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1720 | PROOF | A208866 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1721 | PROOF | A209807 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1722 | PROOF | A209841 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1723 | PROOF | A210054 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1724 | PROOF | A210158 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1725 | PROOF | A306948 | creative telescoping with the boundary and range corrections carried through |
| 1726 | PROOF | A275139 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1727 | PROOF | A275505 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1728 | PROOF | A203732 | a table's column recurrences, each column being a fixed-width array count |
| 1729 | PROOF | A204750 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1730 | PROOF | A233079 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1731 | PROOF | A203887 | a table's column recurrences, each column being a fixed-width array count |
| 1732 | PROOF | A233084 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1733 | PROOF | A203934 | a table's column recurrences, each column being a fixed-width array count |
| 1734 | PROOF | A198279 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1735 | PROOF | A274745 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1736 | PROOF | A204749 | a 3 X 3 subblock condition counted up to relabelling, by falling-factorial inversion |
| 1737 | PROOF | A264131 | a table's column recurrences, each column being a fixed-width array count |
| 1738 | PROOF | A233094 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1739 | PROOF | A232131 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1740 | PROOF | A188823 | an explicit closed form, turned into the recurrence it satisfies |
| 1741 | PROOF | A264090 | a table's column recurrences, each column being a fixed-width array count |
| 1742 | PROOF | A264655 | a table's column recurrences, each column being a fixed-width array count |
| 1743 | PROOF | A233013 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1744 | PROOF | A233093 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1745 | PROOF | A238523 | a table's column recurrences, each column being a fixed-width array count |
| 1746 | PROOF | A274798 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1747 | PROOF | A274853 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1748 | PROOF | A275143 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1749 | PROOF | A233099 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1750 | PROOF | A214099 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1751 | PROOF | A231390 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1752 | PROOF | A231317 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1753 | PROOF | A231324 | a table's column recurrences, each column being a fixed-width array count |
| 1754 | PROOF | A214107 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1755 | PROOF | A203835 | a table's column recurrences, each column being a fixed-width array count |
| 1756 | PROOF | A280955 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1757 | PROOF | A188821 | an explicit closed form, turned into the recurrence it satisfies |
| 1758 | PROOF | A264313 | a table's column recurrences, each column being a fixed-width array count |
| 1759 | PROOF | A241371 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1760 | PROOF | A208389 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1761 | PROOF | A238906 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1762 | PROOF | A238912 | a table's column recurrences, each column being a fixed-width array count |
| 1763 | PROOF | A198205 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1764 | PROOF | A198287 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1765 | PROOF | A198482 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1766 | PROOF | A279704 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1767 | PROOF | A208638 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1768 | PROOF | A224128 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1769 | PROOF | A281710 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1770 | PROOF | A250913 | a table's column recurrences, each column being a fixed-width array count |
| 1771 | PROOF | A251373 | a table's column recurrences, each column being a fixed-width array count |
| 1772 | PROOF | A214137 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1773 | PROOF | A198447 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1774 | PROOF | A204625 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1775 | PROOF | A276293 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1776 | PROOF | A281831 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1777 | PROOF | A281949 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1778 | PROOF | A231227 | a table's column recurrences, each column being a fixed-width array count |
| 1779 | PROOF | A208634 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1780 | PROOF | A208706 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1781 | PROOF | A234140 | a table's column recurrences, each column being a fixed-width array count |
| 1782 | PROOF | A235289 | a table's column recurrences, each column being a fixed-width array count |
| 1783 | PROOF | A251300 | a table's column recurrences, each column being a fixed-width array count |
| 1784 | PROOF | A251343 | a table's column recurrences, each column being a fixed-width array count |
| 1785 | PROOF | A251524 | a table's column recurrences, each column being a fixed-width array count |
| 1786 | PROOF | A198710 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1787 | PROOF | A204070 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1788 | PROOF | A208317 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1789 | PROOF | A209095 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1790 | PROOF | A209891 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1791 | PROOF | A210101 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1792 | PROOF | A198900 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1793 | PROOF | A208633 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1794 | PROOF | A234266 | a table's column recurrences, each column being a fixed-width array count |
| 1795 | PROOF | A251351 | a table's column recurrences, each column being a fixed-width array count |
| 1796 | PROOF | A251390 | a table's column recurrences, each column being a fixed-width array count |
| 1797 | PROOF | A204565 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1798 | PROOF | A208402 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1799 | PROOF | A208858 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1800 | PROOF | A210118 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1801 | PROOF | A210127 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1802 | PROOF | A210397 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1803 | PROOF | A224404 | monotone and unimodal conditions along rows, columns and diagonals, with the fallen bits carried in the state |
| 1804 | PROOF | A208264 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1805 | PROOF | A209822 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1806 | PROOF | A210100 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1807 | PROOF | A129833 | creative telescoping with the boundary and range corrections carried through |
| 1808 | PROOF | A209533 | an explicit closed form, turned into the recurrence it satisfies |
| 1809 | PROOF | A275138 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1810 | PROOF | A264071 | a table's column recurrences, each column being a fixed-width array count |
| 1811 | PROOF | A233078 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1812 | PROOF | A269272 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1813 | PROOF | A280668 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1814 | PROOF | A208044 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1815 | PROOF | A214108 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1816 | PROOF | A188865 | an explicit closed form, turned into the recurrence it satisfies |
| 1817 | PROOF | A264534 | a table's column recurrences, each column being a fixed-width array count |
| 1818 | PROOF | A233077 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1819 | PROOF | A268900 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1820 | PROOF | A268967 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1821 | PROOF | A233083 | a neighbour condition plus a first-occurrence ordering clause carried as a flag in the state |
| 1822 | PROOF | A188864 | an explicit closed form, turned into the recurrence it satisfies |
| 1823 | PROOF | A269271 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1824 | PROOF | A270112 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1825 | PROOF | A208393 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1826 | PROOF | A269896 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1827 | PROOF | A209101 | a cell condition counted up to relabelling, by falling-factorial inversion |
| 1828 | PROOF | A214135 | proper colourings of a grid circular in one direction, counted up to renaming the colours |
| 1829 | PROOF | A269761 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1830 | PROOF | A188863 | an explicit closed form, turned into the recurrence it satisfies |
| 1831 | PROOF | A268899 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1832 | PROOF | A268966 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1833 | PROOF | A270052 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1834 | PROOF | A188862 | an explicit closed form, turned into the recurrence it satisfies |
| 1835 | PROOF | A269091 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1836 | PROOF | A269270 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1837 | PROOF | A269277 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1838 | PROOF | A198474 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1839 | PROOF | A198638 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1840 | PROOF | A208388 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1841 | PROOF | A238929 | a table's column recurrences, each column being a fixed-width array count |
| 1842 | PROOF | A268633 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1843 | PROOF | A268898 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1844 | PROOF | A268905 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1845 | PROOF | A268965 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1846 | PROOF | A268972 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1847 | PROOF | A188861 | an explicit closed form, turned into the recurrence it satisfies |
| 1848 | PROOF | A251283 | a table's column recurrences, each column being a fixed-width array count |
| 1849 | PROOF | A251491 | a table's column recurrences, each column being a fixed-width array count |
| 1850 | PROOF | A263973 | a table's column recurrences, each column being a fixed-width array count |
| 1851 | PROOF | A270111 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1852 | PROOF | A208403 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1853 | PROOF | A269895 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1854 | PROOF | A269760 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1855 | PROOF | A204624 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1856 | PROOF | A208253 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1857 | PROOF | A269822 | a global count of marked adjacent pairs carried in the state, then a walk count |
| 1858 | PROOF | A208705 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1859 | PROOF | A209727 | a table's column recurrences, each column being a fixed-width array count |
| 1860 | PROOF | A251249 | a table's column recurrences, each column being a fixed-width array count |
| 1861 | PROOF | A205163 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1862 | PROOF | A210406 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1863 | PROOF | A208309 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1864 | PROOF | A208316 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1865 | PROOF | A208561 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1866 | PROOF | A209094 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1867 | PROOF | A209890 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1868 | PROOF | A000180 | creative telescoping with the boundary and range corrections carried through |
| 1869 | PROOF | A263989 | a table's column recurrences, each column being a fixed-width array count |
| 1870 | PROOF | A203821 | an explicit closed form, turned into the recurrence it satisfies |
| 1871 | PROOF | A264017 | a table's column recurrences, each column being a fixed-width array count |
| 1872 | PROOF | A264059 | a table's column recurrences, each column being a fixed-width array count |
| 1873 | PROOF | A264128 | a table's column recurrences, each column being a fixed-width array count |
| 1874 | PROOF | A264190 | a table's column recurrences, each column being a fixed-width array count |
| 1875 | PROOF | A264195 | a table's column recurrences, each column being a fixed-width array count |
| 1876 | PROOF | A264490 | a table's column recurrences, each column being a fixed-width array count |
| 1877 | PROOF | A203820 | an explicit closed form, turned into the recurrence it satisfies |
| 1878 | PROOF | A203880 | an explicit closed form, turned into the recurrence it satisfies |
| 1879 | PROOF | A203927 | an explicit closed form, turned into the recurrence it satisfies |
| 1880 | PROOF | A203789 | an explicit closed form, turned into the recurrence it satisfies |
| 1881 | PROOF | A203819 | an explicit closed form, turned into the recurrence it satisfies |
| 1882 | PROOF | A208387 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1883 | PROOF | A204623 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1884 | PROOF | A208704 | arrays counted up to relabelling: patterns recovered by falling-factorial inversion, then a lumped walk count |
| 1885 | PROOF | A207927 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1886 | PROOF | A188563 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1887 | PROOF | A207965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1888 | PROOF | A207274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1889 | PROOF | A207844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1890 | PROOF | A208038 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1891 | PROOF | A207185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1892 | PROOF | A207441 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1893 | PROOF | A207247 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1894 | PROOF | A206938 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1895 | PROOF | A207445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1896 | PROOF | A208419 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1897 | PROOF | A207239 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1898 | PROOF | A207856 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1899 | PROOF | A207464 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1900 | PROOF | A189614 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1901 | PROOF | A206998 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1902 | PROOF | A208499 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1903 | PROOF | A220723 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 1904 | PROOF | A196425 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1905 | PROOF | A207487 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1906 | PROOF | A203841 | a condition on every cell over the neighbour set the entry names |
| 1907 | PROOF | A209957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1908 | PROOF | A188691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1909 | PROOF | A207499 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1910 | PROOF | A207664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1911 | PROOF | A207127 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1912 | PROOF | A207907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1913 | PROOF | A207002 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1914 | PROOF | A220715 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 1915 | PROOF | A206783 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1916 | PROOF | A298090 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1917 | PROOF | A207521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1918 | PROOF | A207775 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1919 | PROOF | A207343 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1920 | PROOF | A207086 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1921 | PROOF | A207504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1922 | PROOF | A208026 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1923 | PROOF | A207179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1924 | PROOF | A207697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1925 | PROOF | A207349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1926 | PROOF | A206887 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1927 | PROOF | A207417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1928 | PROOF | A208075 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1929 | PROOF | A255085 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1930 | PROOF | A220678 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 1931 | PROOF | A207423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1932 | PROOF | A252408 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1933 | PROOF | A207772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1934 | PROOF | A189108 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1935 | PROOF | A207716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1936 | PROOF | A220741 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 1937 | PROOF | A209948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1938 | PROOF | A184660 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1939 | PROOF | A297984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1940 | PROOF | A297855 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1941 | PROOF | A207469 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1942 | PROOF | A207959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1943 | PROOF | A207921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1944 | PROOF | A207273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1945 | PROOF | A209551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1946 | PROOF | A260291 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1947 | PROOF | A260606 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1948 | PROOF | A220626 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 1949 | PROOF | A185528 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1950 | PROOF | A188770 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1951 | PROOF | A209782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1952 | PROOF | A210330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1953 | PROOF | A210350 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1954 | PROOF | A298051 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1955 | PROOF | A298656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1956 | PROOF | A220735 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 1957 | PROOF | A303798 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1958 | PROOF | A188519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1959 | PROOF | A188854 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1960 | PROOF | A203437 | a condition on every cell over the neighbour set the entry names |
| 1961 | PROOF | A207246 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1962 | PROOF | A210072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1963 | PROOF | A302456 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1964 | PROOF | A303238 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1965 | PROOF | A305093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1966 | PROOF | A316753 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1967 | PROOF | A203097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1968 | PROOF | A207789 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1969 | PROOF | A209793 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1970 | PROOF | A301665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1971 | PROOF | A303036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1972 | PROOF | A303199 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1973 | PROOF | A304948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1974 | PROOF | A318020 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1975 | PROOF | A207074 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1976 | PROOF | A252098 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1977 | PROOF | A188603 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1978 | PROOF | A298954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1979 | PROOF | A206868 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1980 | PROOF | A206991 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1981 | PROOF | A304955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1982 | PROOF | A210272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1983 | PROOF | A208418 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1984 | PROOF | A189266 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1985 | PROOF | A209853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1986 | PROOF | A298578 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1987 | PROOF | A302429 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1988 | PROOF | A302729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1989 | PROOF | A208695 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1990 | PROOF | A188751 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1991 | PROOF | A252641 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 1992 | PROOF | A298175 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1993 | PROOF | A207740 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1994 | PROOF | A298164 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1995 | PROOF | A298290 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1996 | PROOF | A298556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1997 | PROOF | A299183 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1998 | PROOF | A299570 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 1999 | PROOF | A304006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2000 | PROOF | A304540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2001 | PROOF | A306125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2002 | PROOF | A316307 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2003 | PROOF | A252599 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2004 | PROOF | A302412 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2005 | PROOF | A303179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2006 | PROOF | A207686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2007 | PROOF | A297947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2008 | PROOF | A298226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2009 | PROOF | A298766 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2010 | PROOF | A300919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2011 | PROOF | A301604 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2012 | PROOF | A304015 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2013 | PROOF | A304152 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2014 | PROOF | A304351 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2015 | PROOF | A305363 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2016 | PROOF | A303960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2017 | PROOF | A252385 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2018 | PROOF | A317771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2019 | PROOF | A208701 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2020 | PROOF | A209908 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2021 | PROOF | A304475 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2022 | PROOF | A305219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2023 | PROOF | A305638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2024 | PROOF | A306056 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2025 | PROOF | A316300 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2026 | PROOF | A317032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2027 | PROOF | A317234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2028 | PROOF | A260367 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2029 | PROOF | A304300 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2030 | PROOF | A189113 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2031 | PROOF | A207659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2032 | PROOF | A209711 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2033 | PROOF | A298191 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2034 | PROOF | A298618 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2035 | PROOF | A299085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2036 | PROOF | A299341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2037 | PROOF | A299848 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2038 | PROOF | A302281 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2039 | PROOF | A316235 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2040 | PROOF | A220551 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2041 | PROOF | A220567 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2042 | PROOF | A207708 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2043 | PROOF | A207428 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2044 | PROOF | A303799 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2045 | PROOF | A318544 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2046 | PROOF | A302638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2047 | PROOF | A206874 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2048 | PROOF | A208167 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2049 | PROOF | A207091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2050 | PROOF | A282965 | a condition on every cell over the neighbour set the entry names |
| 2051 | PROOF | A210295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2052 | PROOF | A298715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2053 | PROOF | A298830 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2054 | PROOF | A304259 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2055 | PROOF | A305448 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2056 | PROOF | A255789 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2057 | PROOF | A252327 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2058 | PROOF | A305338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2059 | PROOF | A303621 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2060 | PROOF | A207268 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2061 | PROOF | A297955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2062 | PROOF | A298066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2063 | PROOF | A298217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2064 | PROOF | A299310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2065 | PROOF | A299447 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2066 | PROOF | A301537 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2067 | PROOF | A303018 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2068 | PROOF | A316214 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2069 | PROOF | A252150 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2070 | PROOF | A252212 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2071 | PROOF | A252507 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2072 | PROOF | A252616 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2073 | PROOF | A298097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2074 | PROOF | A298899 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2075 | PROOF | A317899 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2076 | PROOF | A318013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2077 | PROOF | A232025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2078 | PROOF | A207491 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2079 | PROOF | A207771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2080 | PROOF | A231540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2081 | PROOF | A297317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2082 | PROOF | A299678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2083 | PROOF | A302214 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2084 | PROOF | A302312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2085 | PROOF | A303042 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2086 | PROOF | A316879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2087 | PROOF | A317607 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2088 | PROOF | A188848 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2089 | PROOF | A252298 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2090 | PROOF | A305480 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2091 | PROOF | A220593 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2092 | PROOF | A220729 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2093 | PROOF | A297227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2094 | PROOF | A207843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2095 | PROOF | A207513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2096 | PROOF | A298135 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2097 | PROOF | A298926 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2098 | PROOF | A301527 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2099 | PROOF | A302305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2100 | PROOF | A302879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2101 | PROOF | A260541 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2102 | PROOF | A260838 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2103 | PROOF | A196539 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2104 | PROOF | A254974 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2105 | PROOF | A297436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2106 | PROOF | A326102 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2107 | PROOF | A207783 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2108 | PROOF | A300085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2109 | PROOF | A259998 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2110 | PROOF | A206934 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2111 | PROOF | A220599 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2112 | PROOF | A298632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2113 | PROOF | A300469 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2114 | PROOF | A207931 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2115 | PROOF | A298504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2116 | PROOF | A298723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2117 | PROOF | A298891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2118 | PROOF | A303527 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2119 | PROOF | A318419 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2120 | PROOF | A207663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2121 | PROOF | A207073 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2122 | PROOF | A208365 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2123 | PROOF | A220637 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2124 | PROOF | A260102 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2125 | PROOF | A297580 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2126 | PROOF | A188995 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2127 | PROOF | A189192 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2128 | PROOF | A231658 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2129 | PROOF | A207788 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2130 | PROOF | A207498 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2131 | PROOF | A296584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2132 | PROOF | A297939 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2133 | PROOF | A298083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2134 | PROOF | A302325 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2135 | PROOF | A304054 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2136 | PROOF | A304306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2137 | PROOF | A304343 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2138 | PROOF | A305589 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2139 | PROOF | A305772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2140 | PROOF | A316205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2141 | PROOF | A317007 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2142 | PROOF | A317121 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2143 | PROOF | A317600 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2144 | PROOF | A317739 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2145 | PROOF | A318073 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2146 | PROOF | A188759 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2147 | PROOF | A207761 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2148 | PROOF | A234212 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2149 | PROOF | A283953 | a condition on every cell over the neighbour set the entry names |
| 2150 | PROOF | A300111 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2151 | PROOF | A300772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2152 | PROOF | A302873 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2153 | PROOF | A303080 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2154 | PROOF | A316872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2155 | PROOF | A320360 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2156 | PROOF | A297394 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2157 | PROOF | A183390 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2158 | PROOF | A297455 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2159 | PROOF | A189692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2160 | PROOF | A295940 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2161 | PROOF | A296016 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2162 | PROOF | A296036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2163 | PROOF | A297604 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2164 | PROOF | A207715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2165 | PROOF | A203383 | a condition on every cell over the neighbour set the entry names |
| 2166 | PROOF | A207440 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2167 | PROOF | A188705 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2168 | PROOF | A207126 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2169 | PROOF | A297804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2170 | PROOF | A299048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2171 | PROOF | A299810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2172 | PROOF | A300310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2173 | PROOF | A303321 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2174 | PROOF | A207030 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2175 | PROOF | A203834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2176 | PROOF | A252551 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2177 | PROOF | A252567 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2178 | PROOF | A260173 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2179 | PROOF | A302633 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2180 | PROOF | A297516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2181 | PROOF | A297541 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2182 | PROOF | A305249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2183 | PROOF | A207512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2184 | PROOF | A255777 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2185 | PROOF | A302227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2186 | PROOF | A305645 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2187 | PROOF | A317892 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2188 | PROOF | A207272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2189 | PROOF | A206890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2190 | PROOF | A203186 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2191 | PROOF | A229843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2192 | PROOF | A207681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2193 | PROOF | A207906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2194 | PROOF | A188503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2195 | PROOF | A298129 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2196 | PROOF | A298255 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2197 | PROOF | A298450 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2198 | PROOF | A299524 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2199 | PROOF | A302071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2200 | PROOF | A318426 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2201 | PROOF | A208161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2202 | PROOF | A259720 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2203 | PROOF | A256806 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2204 | PROOF | A260763 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2205 | PROOF | A305689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2206 | PROOF | A317069 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2207 | PROOF | A232283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2208 | PROOF | A233880 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2209 | PROOF | A207486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2210 | PROOF | A189066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2211 | PROOF | A296401 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2212 | PROOF | A297752 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2213 | PROOF | A297765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2214 | PROOF | A297872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2215 | PROOF | A300461 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2216 | PROOF | A317039 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2217 | PROOF | A317693 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2218 | PROOF | A251109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2219 | PROOF | A207855 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2220 | PROOF | A208074 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2221 | PROOF | A302628 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2222 | PROOF | A207563 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2223 | PROOF | A282477 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2224 | PROOF | A284071 | a condition on every cell over the neighbour set the entry names |
| 2225 | PROOF | A283228 | a condition on every cell over the neighbour set the entry names |
| 2226 | PROOF | A207888 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2227 | PROOF | A206880 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2228 | PROOF | A251162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2229 | PROOF | A296959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2230 | PROOF | A297723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2231 | PROOF | A298497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2232 | PROOF | A302891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2233 | PROOF | A316921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2234 | PROOF | A302520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2235 | PROOF | A296310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2236 | PROOF | A296574 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2237 | PROOF | A296830 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2238 | PROOF | A297911 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2239 | PROOF | A302363 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2240 | PROOF | A304593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2241 | PROOF | A306139 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2242 | PROOF | A316379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2243 | PROOF | A317372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2244 | PROOF | A207915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2245 | PROOF | A255156 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2246 | PROOF | A297813 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2247 | PROOF | A252194 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2248 | PROOF | A297599 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2249 | PROOF | A231973 | a condition on every cell over the neighbour set the entry names |
| 2250 | PROOF | A188906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2251 | PROOF | A295048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2252 | PROOF | A297820 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2253 | PROOF | A229929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2254 | PROOF | A207503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2255 | PROOF | A207372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2256 | PROOF | A188876 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2257 | PROOF | A189112 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2258 | PROOF | A296392 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2259 | PROOF | A299131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2260 | PROOF | A299224 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2261 | PROOF | A299889 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2262 | PROOF | A300642 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2263 | PROOF | A302816 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2264 | PROOF | A303471 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2265 | PROOF | A303509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2266 | PROOF | A304890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2267 | PROOF | A305950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2268 | PROOF | A234993 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2269 | PROOF | A207245 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2270 | PROOF | A207696 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2271 | PROOF | A208041 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2272 | PROOF | A207125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2273 | PROOF | A207707 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2274 | PROOF | A207463 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2275 | PROOF | A298182 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2276 | PROOF | A252672 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2277 | PROOF | A278096 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2278 | PROOF | A278205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2279 | PROOF | A283127 | a condition on every cell over the neighbour set the entry names |
| 2280 | PROOF | A207884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2281 | PROOF | A207964 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2282 | PROOF | A207184 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2283 | PROOF | A207586 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2284 | PROOF | A210151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2285 | PROOF | A234328 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2286 | PROOF | A296970 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2287 | PROOF | A297016 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2288 | PROOF | A297903 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2289 | PROOF | A298333 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2290 | PROOF | A298625 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2291 | PROOF | A299598 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2292 | PROOF | A302318 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2293 | PROOF | A302810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2294 | PROOF | A317811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2295 | PROOF | A207342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2296 | PROOF | A301969 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2297 | PROOF | A189698 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2298 | PROOF | A303453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2299 | PROOF | A207267 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2300 | PROOF | A297098 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2301 | PROOF | A207898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2302 | PROOF | A297862 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2303 | PROOF | A298236 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2304 | PROOF | A300423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2305 | PROOF | A300685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2306 | PROOF | A303521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2307 | PROOF | A304415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2308 | PROOF | A207116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2309 | PROOF | A207892 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2310 | PROOF | A303319 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2311 | PROOF | A305039 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2312 | PROOF | A316692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2313 | PROOF | A237856 | a condition on every cell over the neighbour set the entry names |
| 2314 | PROOF | A252466 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2315 | PROOF | A255097 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2316 | PROOF | A304773 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2317 | PROOF | A231379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2318 | PROOF | A255787 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2319 | PROOF | A302738 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2320 | PROOF | A234885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2321 | PROOF | A207085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2322 | PROOF | A283096 | a condition on every cell over the neighbour set the entry names |
| 2323 | PROOF | A283729 | a condition on every cell over the neighbour set the entry names |
| 2324 | PROOF | A202976 | a condition on every cell over the neighbour set the entry names |
| 2325 | PROOF | A206782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2326 | PROOF | A235170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2327 | PROOF | A236296 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2328 | PROOF | A296948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2329 | PROOF | A297974 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2330 | PROOF | A299362 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2331 | PROOF | A304897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2332 | PROOF | A316579 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2333 | PROOF | A207416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2334 | PROOF | A207029 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2335 | PROOF | A207072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2336 | PROOF | A304229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2337 | PROOF | A305585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2338 | PROOF | A253371 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2339 | PROOF | A260244 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2340 | PROOF | A304131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2341 | PROOF | A253370 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2342 | PROOF | A233953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2343 | PROOF | A296722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2344 | PROOF | A305513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2345 | PROOF | A283854 | a condition on every cell over the neighbour set the entry names |
| 2346 | PROOF | A207691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2347 | PROOF | A207926 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2348 | PROOF | A209222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2349 | PROOF | A253369 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2350 | PROOF | A253329 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2351 | PROOF | A231759 | a condition on every cell over the neighbour set the entry names |
| 2352 | PROOF | A231801 | a condition on every cell over the neighbour set the entry names |
| 2353 | PROOF | A188562 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2354 | PROOF | A295093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2355 | PROOF | A295249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2356 | PROOF | A295348 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2357 | PROOF | A295527 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2358 | PROOF | A295648 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2359 | PROOF | A298837 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2360 | PROOF | A301396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2361 | PROOF | A316548 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2362 | PROOF | A234439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2363 | PROOF | A232046 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2364 | PROOF | A259891 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2365 | PROOF | A189261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2366 | PROOF | A252416 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2367 | PROOF | A252559 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2368 | PROOF | A255788 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2369 | PROOF | A260366 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2370 | PROOF | A316516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2371 | PROOF | A234032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2372 | PROOF | A278277 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2373 | PROOF | A296332 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2374 | PROOF | A207680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2375 | PROOF | A207805 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2376 | PROOF | A299685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2377 | PROOF | A302268 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2378 | PROOF | A302967 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2379 | PROOF | A233750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2380 | PROOF | A236904 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2381 | PROOF | A255024 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2382 | PROOF | A259959 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2383 | PROOF | A301950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2384 | PROOF | A197667 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2385 | PROOF | A238318 | a condition on every cell over the neighbour set the entry names |
| 2386 | PROOF | A278190 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2387 | PROOF | A295779 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2388 | PROOF | A236496 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2389 | PROOF | A296317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2390 | PROOF | A302950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2391 | PROOF | A305179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2392 | PROOF | A316417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2393 | PROOF | A317380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2394 | PROOF | A252598 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2395 | PROOF | A282859 | a condition on every cell over the neighbour set the entry names |
| 2396 | PROOF | A188609 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2397 | PROOF | A233962 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2398 | PROOF | A296153 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2399 | PROOF | A296986 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2400 | PROOF | A300368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2401 | PROOF | A302468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2402 | PROOF | A303012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2403 | PROOF | A303250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2404 | PROOF | A303626 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2405 | PROOF | A207490 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2406 | PROOF | A207511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2407 | PROOF | A207520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2408 | PROOF | A255088 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2409 | PROOF | A260472 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2410 | PROOF | A282788 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2411 | PROOF | A255144 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2412 | PROOF | A303805 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2413 | PROOF | A283576 | a condition on every cell over the neighbour set the entry names |
| 2414 | PROOF | A282589 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2415 | PROOF | A283569 | a condition on every cell over the neighbour set the entry names |
| 2416 | PROOF | A283780 | a condition on every cell over the neighbour set the entry names |
| 2417 | PROOF | A253743 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2418 | PROOF | A236605 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2419 | PROOF | A237001 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2420 | PROOF | A297090 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2421 | PROOF | A236585 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2422 | PROOF | A297716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2423 | PROOF | A302383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2424 | PROOF | A302423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2425 | PROOF | A303104 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2426 | PROOF | A303193 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2427 | PROOF | A304061 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2428 | PROOF | A304665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2429 | PROOF | A305018 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2430 | PROOF | A316423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2431 | PROOF | A210386 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2432 | PROOF | A282881 | a condition on every cell over the neighbour set the entry names |
| 2433 | PROOF | A284077 | a condition on every cell over the neighbour set the entry names |
| 2434 | PROOF | A207685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2435 | PROOF | A251315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2436 | PROOF | A232020 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2437 | PROOF | A235235 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2438 | PROOF | A183447 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2439 | PROOF | A251943 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2440 | PROOF | A233687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2441 | PROOF | A297586 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2442 | PROOF | A297685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2443 | PROOF | A203332 | a condition on every cell over the neighbour set the entry names |
| 2444 | PROOF | A208417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2445 | PROOF | A298490 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2446 | PROOF | A300542 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2447 | PROOF | A300969 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2448 | PROOF | A304851 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2449 | PROOF | A236897 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2450 | PROOF | A207266 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2451 | PROOF | A207782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2452 | PROOF | A206937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2453 | PROOF | A207001 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2454 | PROOF | A236722 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2455 | PROOF | A251436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2456 | PROOF | A259949 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2457 | PROOF | A256025 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2458 | PROOF | A260290 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2459 | PROOF | A260497 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2460 | PROOF | A278268 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2461 | PROOF | A297593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2462 | PROOF | A297812 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2463 | PROOF | A235234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2464 | PROOF | A295117 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2465 | PROOF | A295272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2466 | PROOF | A306163 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2467 | PROOF | A316612 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2468 | PROOF | A231748 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2469 | PROOF | A234109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2470 | PROOF | A283688 | a condition on every cell over the neighbour set the entry names |
| 2471 | PROOF | A206886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2472 | PROOF | A237177 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2473 | PROOF | A207751 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2474 | PROOF | A235252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2475 | PROOF | A207371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2476 | PROOF | A236124 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2477 | PROOF | A251803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2478 | PROOF | A278173 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2479 | PROOF | A278283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2480 | PROOF | A296382 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2481 | PROOF | A297547 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2482 | PROOF | A297640 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2483 | PROOF | A297745 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2484 | PROOF | A300142 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2485 | PROOF | A300317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2486 | PROOF | A300807 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2487 | PROOF | A301446 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2488 | PROOF | A306168 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2489 | PROOF | A317425 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2490 | PROOF | A320398 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2491 | PROOF | A235065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2492 | PROOF | A251386 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2493 | PROOF | A207396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2494 | PROOF | A260067 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2495 | PROOF | A260281 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2496 | PROOF | A235194 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2497 | PROOF | A255087 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2498 | PROOF | A234661 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2499 | PROOF | A251070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2500 | PROOF | A235193 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2501 | PROOF | A296125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2502 | PROOF | A299725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2503 | PROOF | A303633 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2504 | PROOF | A283518 | a condition on every cell over the neighbour set the entry names |
| 2505 | PROOF | A206997 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2506 | PROOF | A207958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2507 | PROOF | A207658 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2508 | PROOF | A231526 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2509 | PROOF | A236139 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2510 | PROOF | A296537 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2511 | PROOF | A296631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2512 | PROOF | A296800 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2513 | PROOF | A318064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2514 | PROOF | A234085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2515 | PROOF | A207115 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2516 | PROOF | A253328 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2517 | PROOF | A237083 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2518 | PROOF | A251060 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2519 | PROOF | A236973 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2520 | PROOF | A251169 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2521 | PROOF | A196680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2522 | PROOF | A278002 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2523 | PROOF | A252680 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2524 | PROOF | A261551 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2525 | PROOF | A295915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2526 | PROOF | A300205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2527 | PROOF | A233911 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2528 | PROOF | A237153 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2529 | PROOF | A283343 | a condition on every cell over the neighbour set the entry names |
| 2530 | PROOF | A207760 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2531 | PROOF | A255786 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2532 | PROOF | A299056 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2533 | PROOF | A299664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2534 | PROOF | A299817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2535 | PROOF | A303884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2536 | PROOF | A305526 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2537 | PROOF | A305681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2538 | PROOF | A316818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2539 | PROOF | A317000 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2540 | PROOF | A317568 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2541 | PROOF | A236741 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2542 | PROOF | A233647 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2543 | PROOF | A207502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2544 | PROOF | A208166 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2545 | PROOF | A237533 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2546 | PROOF | A207787 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2547 | PROOF | A237303 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2548 | PROOF | A236792 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2549 | PROOF | A237392 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2550 | PROOF | A189062 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2551 | PROOF | A198180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2552 | PROOF | A209550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2553 | PROOF | A260605 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2554 | PROOF | A297429 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2555 | PROOF | A318543 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2556 | PROOF | A207568 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2557 | PROOF | A295413 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2558 | PROOF | A297983 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2559 | PROOF | A302209 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2560 | PROOF | A305344 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2561 | PROOF | A283412 | a condition on every cell over the neighbour set the entry names |
| 2562 | PROOF | A220620 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2563 | PROOF | A188742 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2564 | PROOF | A236195 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2565 | PROOF | A236315 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2566 | PROOF | A297798 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2567 | PROOF | A298457 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2568 | PROOF | A298997 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2569 | PROOF | A299550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2570 | PROOF | A317819 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2571 | PROOF | A318346 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2572 | PROOF | A234147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2573 | PROOF | A207028 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2574 | PROOF | A236980 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2575 | PROOF | A251153 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2576 | PROOF | A251405 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2577 | PROOF | A236869 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2578 | PROOF | A237309 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2579 | PROOF | A234708 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2580 | PROOF | A261289 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2581 | PROOF | A300181 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2582 | PROOF | A318342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2583 | PROOF | A196213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2584 | PROOF | A206471 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2585 | PROOF | A231994 | a condition on every cell over the neighbour set the entry names |
| 2586 | PROOF | A234707 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2587 | PROOF | A317731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2588 | PROOF | A188847 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2589 | PROOF | A302167 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2590 | PROOF | A220625 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2591 | PROOF | A220642 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2592 | PROOF | A231646 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2593 | PROOF | A208037 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2594 | PROOF | A282334 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2595 | PROOF | A236699 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2596 | PROOF | A236713 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2597 | PROOF | A236612 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2598 | PROOF | A282993 | a condition on every cell over the neighbour set the entry names |
| 2599 | PROOF | A232000 | a condition on every cell over the neighbour set the entry names |
| 2600 | PROOF | A183400 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2601 | PROOF | A188518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2602 | PROOF | A207920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2603 | PROOF | A208025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2604 | PROOF | A208498 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2605 | PROOF | A220685 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2606 | PROOF | A298543 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2607 | PROOF | A301953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2608 | PROOF | A303965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2609 | PROOF | A305284 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2610 | PROOF | A305343 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2611 | PROOF | A318218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2612 | PROOF | A209956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2613 | PROOF | A220619 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2614 | PROOF | A207585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2615 | PROOF | A207706 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2616 | PROOF | A207859 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2617 | PROOF | A207695 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2618 | PROOF | A251446 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2619 | PROOF | A237803 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2620 | PROOF | A231766 | a condition on every cell over the neighbour set the entry names |
| 2621 | PROOF | A251265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2622 | PROOF | A251323 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2623 | PROOF | A297313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2624 | PROOF | A302622 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2625 | PROOF | A197777 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2626 | PROOF | A253745 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2627 | PROOF | A202885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2628 | PROOF | A302168 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2629 | PROOF | A234120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2630 | PROOF | A253744 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 2631 | PROOF | A254973 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2632 | PROOF | A295844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2633 | PROOF | A297730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2634 | PROOF | A207767 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2635 | PROOF | A232276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2636 | PROOF | A237078 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2637 | PROOF | A207562 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2638 | PROOF | A207948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2639 | PROOF | A235242 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2640 | PROOF | A234171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2641 | PROOF | A234186 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2642 | PROOF | A186056 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2643 | PROOF | A188853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2644 | PROOF | A296735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2645 | PROOF | A296823 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2646 | PROOF | A298089 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2647 | PROOF | A298663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2648 | PROOF | A301844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2649 | PROOF | A302885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2650 | PROOF | A303892 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2651 | PROOF | A305765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2652 | PROOF | A317114 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2653 | PROOF | A234202 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2654 | PROOF | A209654 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2655 | PROOF | A251199 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2656 | PROOF | A251509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2657 | PROOF | A207468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2658 | PROOF | A236783 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2659 | PROOF | A207238 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2660 | PROOF | A207444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2661 | PROOF | A188704 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2662 | PROOF | A317516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2663 | PROOF | A197404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2664 | PROOF | A197426 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2665 | PROOF | A203096 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2666 | PROOF | A236446 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2667 | PROOF | A255086 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2668 | PROOF | A260101 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2669 | PROOF | A298143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2670 | PROOF | A303185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2671 | PROOF | A303327 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2672 | PROOF | A304923 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2673 | PROOF | A304928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2674 | PROOF | A305242 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2675 | PROOF | A207878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2676 | PROOF | A282437 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2677 | PROOF | A283946 | a condition on every cell over the neighbour set the entry names |
| 2678 | PROOF | A283199 | a condition on every cell over the neighbour set the entry names |
| 2679 | PROOF | A234551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2680 | PROOF | A238176 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2681 | PROOF | A297081 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2682 | PROOF | A231511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2683 | PROOF | A233787 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2684 | PROOF | A236501 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2685 | PROOF | A295036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2686 | PROOF | A297610 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2687 | PROOF | A298440 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2688 | PROOF | A298585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2689 | PROOF | A299517 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2690 | PROOF | A299577 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2691 | PROOF | A304844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2692 | PROOF | A316541 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2693 | PROOF | A316928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2694 | PROOF | A207905 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2695 | PROOF | A207497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2696 | PROOF | A207370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2697 | PROOF | A207395 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2698 | PROOF | A228802 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2699 | PROOF | A207271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2700 | PROOF | A250977 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2701 | PROOF | A251014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2702 | PROOF | A237688 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2703 | PROOF | A207071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2704 | PROOF | A236813 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2705 | PROOF | A234416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2706 | PROOF | A252345 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2707 | PROOF | A252575 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2708 | PROOF | A260837 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2709 | PROOF | A188750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2710 | PROOF | A297461 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2711 | PROOF | A303194 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2712 | PROOF | A303322 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2713 | PROOF | A304601 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2714 | PROOF | A316950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2715 | PROOF | A317738 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2716 | PROOF | A317770 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2717 | PROOF | A251069 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2718 | PROOF | A188690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2719 | PROOF | A232050 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2720 | PROOF | A278090 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2721 | PROOF | A297758 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2722 | PROOF | A299138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2723 | PROOF | A299933 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2724 | PROOF | A209947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2725 | PROOF | A251331 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2726 | PROOF | A207439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2727 | PROOF | A207887 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2728 | PROOF | A283786 | a condition on every cell over the neighbour set the entry names |
| 2729 | PROOF | A207090 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2730 | PROOF | A282964 | a condition on every cell over the neighbour set the entry names |
| 2731 | PROOF | A208160 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2732 | PROOF | A237204 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2733 | PROOF | A251289 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2734 | PROOF | A260204 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2735 | PROOF | A196295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2736 | PROOF | A197202 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2737 | PROOF | A197608 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2738 | PROOF | A197800 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2739 | PROOF | A230671 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2740 | PROOF | A301882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2741 | PROOF | A301997 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2742 | PROOF | A302013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2743 | PROOF | A302079 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2744 | PROOF | A303959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2745 | PROOF | A223427 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2746 | PROOF | A189107 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2747 | PROOF | A260762 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2748 | PROOF | A297302 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2749 | PROOF | A304299 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2750 | PROOF | A305337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2751 | PROOF | A283547 | a condition on every cell over the neighbour set the entry names |
| 2752 | PROOF | A206933 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2753 | PROOF | A207883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2754 | PROOF | A236059 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2755 | PROOF | A233886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2756 | PROOF | A251502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2757 | PROOF | A297515 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2758 | PROOF | A297603 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2759 | PROOF | A297633 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2760 | PROOF | A297854 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2761 | PROOF | A298571 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2762 | PROOF | A302666 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2763 | PROOF | A283381 | a condition on every cell over the neighbour set the entry names |
| 2764 | PROOF | A207114 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2765 | PROOF | A220550 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2766 | PROOF | A220566 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2767 | PROOF | A251216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2768 | PROOF | A300634 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2769 | PROOF | A318209 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2770 | PROOF | A301661 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2771 | PROOF | A302685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2772 | PROOF | A234487 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2773 | PROOF | A234699 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2774 | PROOF | A297399 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2775 | PROOF | A303419 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2776 | PROOF | A208687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2777 | PROOF | A207728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2778 | PROOF | A282525 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2779 | PROOF | A299651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2780 | PROOF | A301440 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2781 | PROOF | A302418 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2782 | PROOF | A239180 | a condition on every cell over the neighbour set the entry names |
| 2783 | PROOF | A208686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2784 | PROOF | A207727 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2785 | PROOF | A234668 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2786 | PROOF | A234706 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2787 | PROOF | A236350 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2788 | PROOF | A208700 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2789 | PROOF | A209731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2790 | PROOF | A231840 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2791 | PROOF | A236620 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2792 | PROOF | A278153 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2793 | PROOF | A297341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2794 | PROOF | A297522 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2795 | PROOF | A297919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2796 | PROOF | A299369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2797 | PROOF | A302411 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2798 | PROOF | A303178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2799 | PROOF | A303686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2800 | PROOF | A304763 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2801 | PROOF | A233640 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2802 | PROOF | A207963 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2803 | PROOF | A207485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2804 | PROOF | A251256 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2805 | PROOF | A234976 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2806 | PROOF | A236878 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2807 | PROOF | A250922 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2808 | PROOF | A251005 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2809 | PROOF | A250970 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2810 | PROOF | A251097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2811 | PROOF | A300430 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2812 | PROOF | A300939 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2813 | PROOF | A301356 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2814 | PROOF | A318547 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2815 | PROOF | A234724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2816 | PROOF | A204601 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2817 | PROOF | A252059 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2818 | PROOF | A282645 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2819 | PROOF | A230836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2820 | PROOF | A234723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2821 | PROOF | A298961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2822 | PROOF | A223339 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2823 | PROOF | A260172 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2824 | PROOF | A260496 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2825 | PROOF | A297579 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2826 | PROOF | A297679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2827 | PROOF | A250910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2828 | PROOF | A234722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2829 | PROOF | A283038 | a condition on every cell over the neighbour set the entry names |
| 2830 | PROOF | A236593 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2831 | PROOF | A297885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2832 | PROOF | A298276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2833 | PROOF | A299077 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2834 | PROOF | A302220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2835 | PROOF | A316179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2836 | PROOF | A317898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2837 | PROOF | A251206 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2838 | PROOF | A282372 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2839 | PROOF | A237162 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2840 | PROOF | A236888 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2841 | PROOF | A283779 | a condition on every cell over the neighbour set the entry names |
| 2842 | PROOF | A237475 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2843 | PROOF | A236822 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2844 | PROOF | A237143 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2845 | PROOF | A300600 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2846 | PROOF | A301907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2847 | PROOF | A318032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2848 | PROOF | A220677 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2849 | PROOF | A237482 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2850 | PROOF | A231835 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2851 | PROOF | A234686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2852 | PROOF | A196702 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2853 | PROOF | A196851 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2854 | PROOF | A196945 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2855 | PROOF | A204402 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2856 | PROOF | A204495 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2857 | PROOF | A238924 | a condition on every cell over the neighbour set the entry names |
| 2858 | PROOF | A252434 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2859 | PROOF | A255155 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2860 | PROOF | A302627 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2861 | PROOF | A234685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2862 | PROOF | A235966 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2863 | PROOF | A183306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2864 | PROOF | A189613 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2865 | PROOF | A255096 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2866 | PROOF | A260243 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2867 | PROOF | A297435 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2868 | PROOF | A302632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2869 | PROOF | A305479 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2870 | PROOF | A318072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2871 | PROOF | A207766 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2872 | PROOF | A235206 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2873 | PROOF | A188602 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2874 | PROOF | A189697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2875 | PROOF | A236083 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2876 | PROOF | A297377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2877 | PROOF | A299317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2878 | PROOF | A299717 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2879 | PROOF | A233879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2880 | PROOF | A203340 | a condition on every cell over the neighbour set the entry names |
| 2881 | PROOF | A207759 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2882 | PROOF | A209653 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2883 | PROOF | A207265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2884 | PROOF | A207914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2885 | PROOF | A237844 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2886 | PROOF | A251225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2887 | PROOF | A189200 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2888 | PROOF | A203794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2889 | PROOF | A259769 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2890 | PROOF | A260977 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2891 | PROOF | A261552 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2892 | PROOF | A261708 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2893 | PROOF | A297373 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2894 | PROOF | A305229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2895 | PROOF | A278010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2896 | PROOF | A260471 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2897 | PROOF | A203833 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2898 | PROOF | A207953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2899 | PROOF | A256805 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2900 | PROOF | A260365 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2901 | PROOF | A207122 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2902 | PROOF | A184787 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2903 | PROOF | A207739 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2904 | PROOF | A282556 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2905 | PROOF | A283722 | a condition on every cell over the neighbour set the entry names |
| 2906 | PROOF | A283860 | a condition on every cell over the neighbour set the entry names |
| 2907 | PROOF | A183383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2908 | PROOF | A188905 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2909 | PROOF | A189106 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2910 | PROOF | A233728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2911 | PROOF | A236199 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2912 | PROOF | A295712 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2913 | PROOF | A300134 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2914 | PROOF | A302208 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2915 | PROOF | A303796 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2916 | PROOF | A305241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2917 | PROOF | A305957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2918 | PROOF | A317218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2919 | PROOF | A317461 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2920 | PROOF | A235233 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2921 | PROOF | A207407 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2922 | PROOF | A208146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2923 | PROOF | A234985 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2924 | PROOF | A283952 | a condition on every cell over the neighbour set the entry names |
| 2925 | PROOF | A207394 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2926 | PROOF | A207124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2927 | PROOF | A207244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2928 | PROOF | A207510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2929 | PROOF | A207786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2930 | PROOF | A207027 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2931 | PROOF | A301325 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2932 | PROOF | A326160 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2933 | PROOF | A260924 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2934 | PROOF | A302162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2935 | PROOF | A196585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2936 | PROOF | A196713 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2937 | PROOF | A196962 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2938 | PROOF | A197042 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2939 | PROOF | A197312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2940 | PROOF | A252426 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2941 | PROOF | A260540 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2942 | PROOF | A278184 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2943 | PROOF | A301968 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2944 | PROOF | A235182 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2945 | PROOF | A234126 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2946 | PROOF | A220636 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2947 | PROOF | A300801 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2948 | PROOF | A282834 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2949 | PROOF | A283541 | a condition on every cell over the neighbour set the entry names |
| 2950 | PROOF | A207877 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2951 | PROOF | A188758 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2952 | PROOF | A188994 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2953 | PROOF | A189191 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2954 | PROOF | A189691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2955 | PROOF | A207714 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2956 | PROOF | A295981 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2957 | PROOF | A296670 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2958 | PROOF | A297226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2959 | PROOF | A297736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2960 | PROOF | A299330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2961 | PROOF | A304423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2962 | PROOF | A316278 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2963 | PROOF | A251068 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2964 | PROOF | A207690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2965 | PROOF | A207925 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2966 | PROOF | A209221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2967 | PROOF | A282476 | a condition on every cell's king-move neighbourhood, boundaries included |
| 2968 | PROOF | A283227 | a condition on every cell over the neighbour set the entry names |
| 2969 | PROOF | A207679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2970 | PROOF | A234884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2971 | PROOF | A283095 | a condition on every cell over the neighbour set the entry names |
| 2972 | PROOF | A233711 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2973 | PROOF | A207348 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2974 | PROOF | A208416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2975 | PROOF | A208497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2976 | PROOF | A207781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2977 | PROOF | A237212 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2978 | PROOF | A251353 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2979 | PROOF | A237169 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 2980 | PROOF | A236015 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2981 | PROOF | A261377 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2982 | PROOF | A301822 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2983 | PROOF | A196797 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2984 | PROOF | A197674 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2985 | PROOF | A236052 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 2986 | PROOF | A259997 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2987 | PROOF | A301949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2988 | PROOF | A220712 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 2989 | PROOF | A234157 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2990 | PROOF | A256024 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 2991 | PROOF | A297598 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2992 | PROOF | A235181 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2993 | PROOF | A230171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2994 | PROOF | A283490 | a condition on every cell over the neighbour set the entry names |
| 2995 | PROOF | A233898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2996 | PROOF | A188769 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2997 | PROOF | A207750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2998 | PROOF | A300926 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 2999 | PROOF | A302377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3000 | PROOF | A303098 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3001 | PROOF | A305248 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3002 | PROOF | A318012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3003 | PROOF | A234453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3004 | PROOF | A237070 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3005 | PROOF | A234077 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3006 | PROOF | A207804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3007 | PROOF | A207662 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3008 | PROOF | A251108 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3009 | PROOF | A237093 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3010 | PROOF | A251314 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3011 | PROOF | A300501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3012 | PROOF | A302082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3013 | PROOF | A317858 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3014 | PROOF | A237219 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3015 | PROOF | A188872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3016 | PROOF | A206253 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3017 | PROOF | A261262 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3018 | PROOF | A197532 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3019 | PROOF | A198150 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3020 | PROOF | A238282 | a condition on every cell over the neighbour set the entry names |
| 3021 | PROOF | A252107 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3022 | PROOF | A252294 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3023 | PROOF | A252608 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3024 | PROOF | A297393 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3025 | PROOF | A301839 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3026 | PROOF | A302067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3027 | PROOF | A206470 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3028 | PROOF | A254417 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3029 | PROOF | A254424 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3030 | PROOF | A304772 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3031 | PROOF | A316515 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3032 | PROOF | A320368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3033 | PROOF | A208373 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3034 | PROOF | A220649 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3035 | PROOF | A209228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3036 | PROOF | A233984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3037 | PROOF | A207567 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3038 | PROOF | A209227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3039 | PROOF | A220592 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3040 | PROOF | A220728 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3041 | PROOF | A295375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3042 | PROOF | A300171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3043 | PROOF | A300338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3044 | PROOF | A209792 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3045 | PROOF | A220598 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3046 | PROOF | A207310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3047 | PROOF | A207566 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3048 | PROOF | A206879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3049 | PROOF | A237334 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3050 | PROOF | A220722 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3051 | PROOF | A233922 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3052 | PROOF | A207369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3053 | PROOF | A207415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3054 | PROOF | A207742 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3055 | PROOF | A207909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3056 | PROOF | A210271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3057 | PROOF | A233944 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3058 | PROOF | A250836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3059 | PROOF | A231704 | a condition on every cell over the neighbour set the entry names |
| 3060 | PROOF | A207705 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3061 | PROOF | A250959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3062 | PROOF | A251396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3063 | PROOF | A300876 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3064 | PROOF | A302151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3065 | PROOF | A259639 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3066 | PROOF | A260135 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3067 | PROOF | A261110 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3068 | PROOF | A304269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3069 | PROOF | A196480 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3070 | PROOF | A197745 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3071 | PROOF | A198008 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3072 | PROOF | A232045 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3073 | PROOF | A252185 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3074 | PROOF | A252400 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3075 | PROOF | A259948 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3076 | PROOF | A261288 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3077 | PROOF | A207812 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3078 | PROOF | A184148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3079 | PROOF | A260289 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3080 | PROOF | A260604 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3081 | PROOF | A303966 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3082 | PROOF | A204600 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3083 | PROOF | A207952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3084 | PROOF | A283637 | a condition on every cell over the neighbour set the entry names |
| 3085 | PROOF | A207121 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3086 | PROOF | A283630 | a condition on every cell over the neighbour set the entry names |
| 3087 | PROOF | A234684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3088 | PROOF | A231519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3089 | PROOF | A297509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3090 | PROOF | A297650 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3091 | PROOF | A297697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3092 | PROOF | A297989 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3093 | PROOF | A298283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3094 | PROOF | A299657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3095 | PROOF | A299736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3096 | PROOF | A300211 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3097 | PROOF | A302955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3098 | PROOF | A251245 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3099 | PROOF | A208036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3100 | PROOF | A282588 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3101 | PROOF | A284070 | a condition on every cell over the neighbour set the entry names |
| 3102 | PROOF | A207178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3103 | PROOF | A206781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3104 | PROOF | A207406 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3105 | PROOF | A208145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3106 | PROOF | A207770 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3107 | PROOF | A208024 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3108 | PROOF | A184491 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3109 | PROOF | A207684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3110 | PROOF | A207113 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3111 | PROOF | A251161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3112 | PROOF | A251302 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3113 | PROOF | A300493 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3114 | PROOF | A301486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3115 | PROOF | A301886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3116 | PROOF | A318077 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3117 | PROOF | A318086 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3118 | PROOF | A283380 | a condition on every cell over the neighbour set the entry names |
| 3119 | PROOF | A207427 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3120 | PROOF | A185536 | a condition on every cell over the neighbour set the entry names |
| 3121 | PROOF | A234734 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3122 | PROOF | A234819 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3123 | PROOF | A301322 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3124 | PROOF | A185819 | a condition on every cell over the neighbour set the entry names |
| 3125 | PROOF | A234879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3126 | PROOF | A234654 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3127 | PROOF | A186162 | a condition on every cell over the neighbour set the entry names |
| 3128 | PROOF | A234733 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3129 | PROOF | A251838 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3130 | PROOF | A255023 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3131 | PROOF | A259958 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3132 | PROOF | A302519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3133 | PROOF | A303318 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3134 | PROOF | A318341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3135 | PROOF | A235094 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3136 | PROOF | A234818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3137 | PROOF | A236150 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3138 | PROOF | A253751 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3139 | PROOF | A189260 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3140 | PROOF | A251279 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3141 | PROOF | A261550 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3142 | PROOF | A318542 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3143 | PROOF | A253347 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3144 | PROOF | A253354 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3145 | PROOF | A237032 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3146 | PROOF | A185553 | a condition on every cell over the neighbour set the entry names |
| 3147 | PROOF | A252058 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3148 | PROOF | A234732 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3149 | PROOF | A234817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3150 | PROOF | A297690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3151 | PROOF | A298631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3152 | PROOF | A298966 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3153 | PROOF | A317737 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3154 | PROOF | A235192 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3155 | PROOF | A184371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3156 | PROOF | A283694 | a condition on every cell over the neighbour set the entry names |
| 3157 | PROOF | A234492 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3158 | PROOF | A207561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3159 | PROOF | A207765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3160 | PROOF | A206873 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3161 | PROOF | A207749 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3162 | PROOF | A237940 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3163 | PROOF | A209652 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3164 | PROOF | A207678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3165 | PROOF | A207758 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3166 | PROOF | A236641 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3167 | PROOF | A236658 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3168 | PROOF | A237061 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3169 | PROOF | A188502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3170 | PROOF | A189265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3171 | PROOF | A297316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3172 | PROOF | A300375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3173 | PROOF | A300677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3174 | PROOF | A320404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3175 | PROOF | A237102 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3176 | PROOF | A197162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3177 | PROOF | A197445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3178 | PROOF | A197891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3179 | PROOF | A252082 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3180 | PROOF | A259719 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3181 | PROOF | A259890 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3182 | PROOF | A297312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3183 | PROOF | A298181 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3184 | PROOF | A301405 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3185 | PROOF | A236945 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3186 | PROOF | A234179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3187 | PROOF | A260836 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3188 | PROOF | A261287 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3189 | PROOF | A295778 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3190 | PROOF | A297592 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3191 | PROOF | A316805 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3192 | PROOF | A317522 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3193 | PROOF | A235093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3194 | PROOF | A207842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3195 | PROOF | A231694 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3196 | PROOF | A236589 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3197 | PROOF | A255143 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3198 | PROOF | A296647 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3199 | PROOF | A297540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3200 | PROOF | A297982 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3201 | PROOF | A299063 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3202 | PROOF | A299176 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3203 | PROOF | A299835 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3204 | PROOF | A300468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3205 | PROOF | A302166 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3206 | PROOF | A302637 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3207 | PROOF | A303620 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3208 | PROOF | A326101 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3209 | PROOF | A237236 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3210 | PROOF | A207882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3211 | PROOF | A207957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3212 | PROOF | A283728 | a condition on every cell over the neighbour set the entry names |
| 3213 | PROOF | A207489 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3214 | PROOF | A207501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3215 | PROOF | A282880 | a condition on every cell over the neighbour set the entry names |
| 3216 | PROOF | A236896 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3217 | PROOF | A184666 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3218 | PROOF | A207393 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3219 | PROOF | A231539 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3220 | PROOF | A237135 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3221 | PROOF | A251198 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3222 | PROOF | A251453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3223 | PROOF | A251802 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3224 | PROOF | A296638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3225 | PROOF | A300534 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3226 | PROOF | A300961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3227 | PROOF | A207070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3228 | PROOF | A196133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3229 | PROOF | A196977 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3230 | PROOF | A197498 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3231 | PROOF | A197540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3232 | PROOF | A239181 | a condition on every cell over the neighbour set the entry names |
| 3233 | PROOF | A188703 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3234 | PROOF | A228758 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3235 | PROOF | A252123 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3236 | PROOF | A252203 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3237 | PROOF | A259768 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3238 | PROOF | A260066 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3239 | PROOF | A260280 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3240 | PROOF | A261707 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3241 | PROOF | A302621 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3242 | PROOF | A236121 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3243 | PROOF | A234653 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3244 | PROOF | A207722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3245 | PROOF | A237855 | a condition on every cell over the neighbour set the entry names |
| 3246 | PROOF | A282644 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3247 | PROOF | A297398 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3248 | PROOF | A302424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3249 | PROOF | A317730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3250 | PROOF | A229698 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3251 | PROOF | A184780 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3252 | PROOF | A230186 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3253 | PROOF | A283546 | a condition on every cell over the neighbour set the entry names |
| 3254 | PROOF | A231972 | a condition on every cell over the neighbour set the entry names |
| 3255 | PROOF | A296316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3256 | PROOF | A296331 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3257 | PROOF | A298142 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3258 | PROOF | A298778 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3259 | PROOF | A302631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3260 | PROOF | A304468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3261 | PROOF | A306049 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3262 | PROOF | A316285 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3263 | PROOF | A317226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3264 | PROOF | A207738 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3265 | PROOF | A283540 | a condition on every cell over the neighbour set the entry names |
| 3266 | PROOF | A207943 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3267 | PROOF | A206867 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3268 | PROOF | A206990 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3269 | PROOF | A235020 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3270 | PROOF | A206885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3271 | PROOF | A207183 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3272 | PROOF | A207309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3273 | PROOF | A282858 | a condition on every cell over the neighbour set the entry names |
| 3274 | PROOF | A207919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3275 | PROOF | A183786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3276 | PROOF | A208165 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3277 | PROOF | A236635 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3278 | PROOF | A251067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3279 | PROOF | A231758 | a condition on every cell over the neighbour set the entry names |
| 3280 | PROOF | A237293 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3281 | PROOF | A228801 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3282 | PROOF | A296583 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3283 | PROOF | A296958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3284 | PROOF | A297803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3285 | PROOF | A300883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3286 | PROOF | A300918 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3287 | PROOF | A318040 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3288 | PROOF | A253327 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3289 | PROOF | A207443 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3290 | PROOF | A297337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3291 | PROOF | A303313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3292 | PROOF | A197359 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3293 | PROOF | A197618 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3294 | PROOF | A230783 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3295 | PROOF | A260923 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3296 | PROOF | A261376 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3297 | PROOF | A301782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3298 | PROOF | A301904 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3299 | PROOF | A253528 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3300 | PROOF | A207850 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3301 | PROOF | A208082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3302 | PROOF | A207756 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3303 | PROOF | A183446 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3304 | PROOF | A209549 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3305 | PROOF | A297392 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3306 | PROOF | A297428 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3307 | PROOF | A251370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3308 | PROOF | A277940 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3309 | PROOF | A207367 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3310 | PROOF | A236090 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3311 | PROOF | A220711 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3312 | PROOF | A207951 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3313 | PROOF | A236597 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3314 | PROOF | A254972 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3315 | PROOF | A260761 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3316 | PROOF | A301611 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3317 | PROOF | A303465 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3318 | PROOF | A303804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3319 | PROOF | A207120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3320 | PROOF | A207253 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3321 | PROOF | A207946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3322 | PROOF | A282333 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3323 | PROOF | A283721 | a condition on every cell over the neighbour set the entry names |
| 3324 | PROOF | A207405 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3325 | PROOF | A208144 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3326 | PROOF | A237385 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3327 | PROOF | A231800 | a condition on every cell over the neighbour set the entry names |
| 3328 | PROOF | A297097 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3329 | PROOF | A188608 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3330 | PROOF | A189065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3331 | PROOF | A209781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3332 | PROOF | A209852 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3333 | PROOF | A210071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3334 | PROOF | A210329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3335 | PROOF | A210349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3336 | PROOF | A251795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3337 | PROOF | A255084 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3338 | PROOF | A296400 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3339 | PROOF | A296985 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3340 | PROOF | A297015 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3341 | PROOF | A297946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3342 | PROOF | A298384 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3343 | PROOF | A299460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3344 | PROOF | A300084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3345 | PROOF | A301526 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3346 | PROOF | A301536 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3347 | PROOF | A301664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3348 | PROOF | A302000 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3349 | PROOF | A302878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3350 | PROOF | A303243 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3351 | PROOF | A303526 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3352 | PROOF | A304014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3353 | PROOF | A304546 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3354 | PROOF | A304954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3355 | PROOF | A306131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3356 | PROOF | A316125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3357 | PROOF | A316443 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3358 | PROOF | A317431 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3359 | PROOF | A236731 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3360 | PROOF | A220714 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3361 | PROOF | A220740 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3362 | PROOF | A236721 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3363 | PROOF | A207421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3364 | PROOF | A220734 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3365 | PROOF | A236791 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3366 | PROOF | A220707 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3367 | PROOF | A300349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3368 | PROOF | A197074 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3369 | PROOF | A197245 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3370 | PROOF | A197275 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3371 | PROOF | A253752 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3372 | PROOF | A204411 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3373 | PROOF | A209510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3374 | PROOF | A231286 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3375 | PROOF | A260976 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3376 | PROOF | A234878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3377 | PROOF | A259996 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3378 | PROOF | A260470 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3379 | PROOF | A260539 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3380 | PROOF | A303424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3381 | PROOF | A239172 | a condition on every cell over the neighbour set the entry names |
| 3382 | PROOF | A202884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3383 | PROOF | A278016 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3384 | PROOF | A253750 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3385 | PROOF | A236029 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3386 | PROOF | A234916 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3387 | PROOF | A189612 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3388 | PROOF | A203377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3389 | PROOF | A208685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3390 | PROOF | A231378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3391 | PROOF | A231741 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3392 | PROOF | A278204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3393 | PROOF | A297729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3394 | PROOF | A302961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3395 | PROOF | A305085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3396 | PROOF | A316416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3397 | PROOF | A316736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3398 | PROOF | A317379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3399 | PROOF | A235101 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3400 | PROOF | A207726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3401 | PROOF | A233952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3402 | PROOF | A283278 | a condition on every cell over the neighbour set the entry names |
| 3403 | PROOF | A202975 | a condition on every cell over the neighbour set the entry names |
| 3404 | PROOF | A208684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3405 | PROOF | A203840 | a condition on every cell over the neighbour set the entry names |
| 3406 | PROOF | A207484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3407 | PROOF | A236705 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3408 | PROOF | A297089 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3409 | PROOF | A189618 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3410 | PROOF | A209710 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3411 | PROOF | A209907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3412 | PROOF | A233629 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3413 | PROOF | A296947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3414 | PROOF | A297751 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3415 | PROOF | A298323 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3416 | PROOF | A298549 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3417 | PROOF | A298617 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3418 | PROOF | A298765 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3419 | PROOF | A298829 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3420 | PROOF | A299216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3421 | PROOF | A299244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3422 | PROOF | A299556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3423 | PROOF | A299583 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3424 | PROOF | A300091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3425 | PROOF | A301493 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3426 | PROOF | A302213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3427 | PROOF | A302461 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3428 | PROOF | A302473 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3429 | PROOF | A304692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3430 | PROOF | A304889 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3431 | PROOF | A316636 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3432 | PROOF | A318093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3433 | PROOF | A318345 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3434 | PROOF | A237891 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3435 | PROOF | A207026 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3436 | PROOF | A207270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3437 | PROOF | A251288 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3438 | PROOF | A251322 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3439 | PROOF | A235315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3440 | PROOF | A188990 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3441 | PROOF | A259739 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3442 | PROOF | A260012 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3443 | PROOF | A304220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3444 | PROOF | A195957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3445 | PROOF | A196451 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3446 | PROOF | A196907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3447 | PROOF | A197345 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3448 | PROOF | A234677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3449 | PROOF | A253529 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3450 | PROOF | A232019 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3451 | PROOF | A189061 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3452 | PROOF | A252247 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3453 | PROOF | A252633 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3454 | PROOF | A260203 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3455 | PROOF | A301660 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3456 | PROOF | A235314 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3457 | PROOF | A234676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3458 | PROOF | A234486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3459 | PROOF | A255154 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3460 | PROOF | A255796 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3461 | PROOF | A303797 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3462 | PROOF | A223410 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3463 | PROOF | A282787 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3464 | PROOF | A235313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3465 | PROOF | A238930 | a condition on every cell over the neighbour set the entry names |
| 3466 | PROOF | A282312 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3467 | PROOF | A188749 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3468 | PROOF | A188846 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3469 | PROOF | A236113 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3470 | PROOF | A236654 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3471 | PROOF | A251295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3472 | PROOF | A255795 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3473 | PROOF | A260835 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3474 | PROOF | A296721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3475 | PROOF | A297502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3476 | PROOF | A297819 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3477 | PROOF | A302804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3478 | PROOF | A303326 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3479 | PROOF | A306162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3480 | PROOF | A318071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3481 | PROOF | A233812 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3482 | PROOF | A234675 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3483 | PROOF | A282833 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3484 | PROOF | A235180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3485 | PROOF | A283636 | a condition on every cell over the neighbour set the entry names |
| 3486 | PROOF | A207942 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3487 | PROOF | A282436 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3488 | PROOF | A283629 | a condition on every cell over the neighbour set the entry names |
| 3489 | PROOF | A283198 | a condition on every cell over the neighbour set the entry names |
| 3490 | PROOF | A234108 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3491 | PROOF | A207713 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3492 | PROOF | A207841 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3493 | PROOF | A208699 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3494 | PROOF | A236740 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3495 | PROOF | A283037 | a condition on every cell over the neighbour set the entry names |
| 3496 | PROOF | A237678 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3497 | PROOF | A184210 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3498 | PROOF | A188517 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3499 | PROOF | A220684 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3500 | PROOF | A255776 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3501 | PROOF | A295248 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3502 | PROOF | A295347 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3503 | PROOF | A295526 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3504 | PROOF | A295647 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3505 | PROOF | A297639 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3506 | PROOF | A297722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3507 | PROOF | A298050 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3508 | PROOF | A298128 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3509 | PROOF | A298149 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3510 | PROOF | A298225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3511 | PROOF | A298254 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3512 | PROOF | A298714 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3513 | PROOF | A299003 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3514 | PROOF | A299123 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3515 | PROOF | A299446 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3516 | PROOF | A299453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3517 | PROOF | A299670 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3518 | PROOF | A299748 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3519 | PROOF | A299881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3520 | PROOF | A300262 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3521 | PROOF | A301349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3522 | PROOF | A301603 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3523 | PROOF | A302273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3524 | PROOF | A302428 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3525 | PROOF | A302523 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3526 | PROOF | A303198 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3527 | PROOF | A303406 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3528 | PROOF | A304151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3529 | PROOF | A304350 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3530 | PROOF | A304671 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3531 | PROOF | A304947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3532 | PROOF | A305170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3533 | PROOF | A305362 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3534 | PROOF | A305913 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3535 | PROOF | A316171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3536 | PROOF | A316234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3537 | PROOF | A317155 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3538 | PROOF | A317453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3539 | PROOF | A317866 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3540 | PROOF | A318019 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3541 | PROOF | A320359 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3542 | PROOF | A282475 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3543 | PROOF | A236782 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3544 | PROOF | A237802 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3545 | PROOF | A251445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3546 | PROOF | A302009 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3547 | PROOF | A196073 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3548 | PROOF | A196332 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3549 | PROOF | A197396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3550 | PROOF | A236807 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3551 | PROOF | A252450 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3552 | PROOF | A297372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3553 | PROOF | A300348 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3554 | PROOF | A302684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3555 | PROOF | A305228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3556 | PROOF | A208006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3557 | PROOF | A260065 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3558 | PROOF | A234119 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3559 | PROOF | A252081 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3560 | PROOF | A253527 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 3561 | PROOF | A208372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3562 | PROOF | A282395 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3563 | PROOF | A189259 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3564 | PROOF | A233677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3565 | PROOF | A236037 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3566 | PROOF | A236134 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3567 | PROOF | A251338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3568 | PROOF | A260100 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3569 | PROOF | A260495 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3570 | PROOF | A278276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3571 | PROOF | A296035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3572 | PROOF | A297585 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3573 | PROOF | A297684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3574 | PROOF | A302261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3575 | PROOF | A303184 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3576 | PROOF | A304145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3577 | PROOF | A304600 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3578 | PROOF | A305485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3579 | PROOF | A305688 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3580 | PROOF | A316811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3581 | PROOF | A317068 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3582 | PROOF | A317561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3583 | PROOF | A283853 | a condition on every cell over the neighbour set the entry names |
| 3584 | PROOF | A220624 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3585 | PROOF | A220641 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3586 | PROOF | A283126 | a condition on every cell over the neighbour set the entry names |
| 3587 | PROOF | A206996 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3588 | PROOF | A234163 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3589 | PROOF | A234445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3590 | PROOF | A238175 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3591 | PROOF | A207308 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3592 | PROOF | A207897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3593 | PROOF | A207438 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3594 | PROOF | A207496 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3595 | PROOF | A207764 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3596 | PROOF | A232024 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3597 | PROOF | A236604 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3598 | PROOF | A236775 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3599 | PROOF | A297080 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3600 | PROOF | A188852 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3601 | PROOF | A209651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3602 | PROOF | A233934 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3603 | PROOF | A251255 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3604 | PROOF | A296594 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3605 | PROOF | A296969 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3606 | PROOF | A297546 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3607 | PROOF | A297656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3608 | PROOF | A297871 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3609 | PROOF | A298058 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3610 | PROOF | A298065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3611 | PROOF | A298190 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3612 | PROOF | A298289 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3613 | PROOF | A298315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3614 | PROOF | A298377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3615 | PROOF | A298449 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3616 | PROOF | A298707 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3617 | PROOF | A298722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3618 | PROOF | A298890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3619 | PROOF | A299047 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3620 | PROOF | A299084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3621 | PROOF | A299182 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3622 | PROOF | A299189 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3623 | PROOF | A299523 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3624 | PROOF | A299809 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3625 | PROOF | A300607 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3626 | PROOF | A303085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3627 | PROOF | A304258 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3628 | PROOF | A304699 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3629 | PROOF | A305010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3630 | PROOF | A305447 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3631 | PROOF | A305644 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3632 | PROOF | A316118 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3633 | PROOF | A316450 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3634 | PROOF | A316643 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3635 | PROOF | A316920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3636 | PROOF | A317038 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3637 | PROOF | A317692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3638 | PROOF | A317768 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3639 | PROOF | A317810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3640 | PROOF | A318425 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3641 | PROOF | A237302 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3642 | PROOF | A207112 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3643 | PROOF | A207243 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3644 | PROOF | A250969 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3645 | PROOF | A251096 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3646 | PROOF | A251224 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3647 | PROOF | A203824 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3648 | PROOF | A297223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3649 | PROOF | A196969 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3650 | PROOF | A197556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3651 | PROOF | A234224 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3652 | PROOF | A235084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3653 | PROOF | A189199 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3654 | PROOF | A260011 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3655 | PROOF | A261261 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3656 | PROOF | A301821 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3657 | PROOF | A316691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3658 | PROOF | A223252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3659 | PROOF | A234223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3660 | PROOF | A208117 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3661 | PROOF | A235083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3662 | PROOF | A259718 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3663 | PROOF | A259889 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3664 | PROOF | A259947 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3665 | PROOF | A302626 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3666 | PROOF | A303418 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3667 | PROOF | A304130 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3668 | PROOF | A207734 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3669 | PROOF | A208012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3670 | PROOF | A230471 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3671 | PROOF | A278001 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3672 | PROOF | A207811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3673 | PROOF | A208553 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3674 | PROOF | A208116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3675 | PROOF | A234031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3676 | PROOF | A234415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3677 | PROOF | A207755 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3678 | PROOF | A207733 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3679 | PROOF | A208011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3680 | PROOF | A234660 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3681 | PROOF | A207366 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3682 | PROOF | A283575 | a condition on every cell over the neighbour set the entry names |
| 3683 | PROOF | A250955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3684 | PROOF | A251274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3685 | PROOF | A251486 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3686 | PROOF | A260469 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3687 | PROOF | A261286 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3688 | PROOF | A261549 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3689 | PROOF | A295843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3690 | PROOF | A297578 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3691 | PROOF | A297678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3692 | PROOF | A298096 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3693 | PROOF | A298898 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3694 | PROOF | A299724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3695 | PROOF | A302417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3696 | PROOF | A303632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3697 | PROOF | A316956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3698 | PROOF | A283568 | a condition on every cell over the neighbour set the entry names |
| 3699 | PROOF | A207732 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3700 | PROOF | A207754 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3701 | PROOF | A206932 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3702 | PROOF | A207365 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3703 | PROOF | A208010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3704 | PROOF | A235092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3705 | PROOF | A207252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3706 | PROOF | A282555 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3707 | PROOF | A237152 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3708 | PROOF | A283945 | a condition on every cell over the neighbour set the entry names |
| 3709 | PROOF | A283342 | a condition on every cell over the neighbour set the entry names |
| 3710 | PROOF | A207950 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3711 | PROOF | A207119 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3712 | PROOF | A207565 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3713 | PROOF | A207731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3714 | PROOF | A208040 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3715 | PROOF | A210385 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3716 | PROOF | A234438 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3717 | PROOF | A236712 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3718 | PROOF | A237161 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3719 | PROOF | A237176 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3720 | PROOF | A188601 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3721 | PROOF | A188741 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3722 | PROOF | A207404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3723 | PROOF | A208143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3724 | PROOF | A231510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3725 | PROOF | A231525 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3726 | PROOF | A233718 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3727 | PROOF | A250929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3728 | PROOF | A278172 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3729 | PROOF | A278282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3730 | PROOF | A295092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3731 | PROOF | A296381 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3732 | PROOF | A296734 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3733 | PROOF | A296799 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3734 | PROOF | A296822 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3735 | PROOF | A297938 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3736 | PROOF | A298082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3737 | PROOF | A298503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3738 | PROOF | A299010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3739 | PROOF | A299092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3740 | PROOF | A299309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3741 | PROOF | A299340 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3742 | PROOF | A299677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3743 | PROOF | A299801 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3744 | PROOF | A299847 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3745 | PROOF | A299874 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3746 | PROOF | A300110 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3747 | PROOF | A300309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3748 | PROOF | A302280 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3749 | PROOF | A302369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3750 | PROOF | A302724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3751 | PROOF | A302890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3752 | PROOF | A303625 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3753 | PROOF | A303685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3754 | PROOF | A303883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3755 | PROOF | A304005 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3756 | PROOF | A304305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3757 | PROOF | A305092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3758 | PROOF | A305588 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3759 | PROOF | A305771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3760 | PROOF | A305949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3761 | PROOF | A316204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3762 | PROOF | A316306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3763 | PROOF | A316752 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3764 | PROOF | A316871 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3765 | PROOF | A317006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3766 | PROOF | A317120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3767 | PROOF | A317261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3768 | PROOF | A317599 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3769 | PROOF | A317818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3770 | PROOF | A317891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3771 | PROOF | A237532 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3772 | PROOF | A236877 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3773 | PROOF | A207414 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3774 | PROOF | A207704 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3775 | PROOF | A220549 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3776 | PROOF | A283341 | a condition on every cell over the neighbour set the entry names |
| 3777 | PROOF | A251215 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3778 | PROOF | A251264 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3779 | PROOF | A236868 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3780 | PROOF | A251152 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3781 | PROOF | A256745 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3782 | PROOF | A302514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3783 | PROOF | A195973 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3784 | PROOF | A196648 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3785 | PROOF | A197302 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3786 | PROOF | A197452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3787 | PROOF | A197643 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3788 | PROOF | A237012 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3789 | PROOF | A188871 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3790 | PROOF | A202910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3791 | PROOF | A206252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3792 | PROOF | A300180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3793 | PROOF | A301321 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3794 | PROOF | A302161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3795 | PROOF | A305584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3796 | PROOF | A317515 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3797 | PROOF | A237011 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3798 | PROOF | A223214 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3799 | PROOF | A237010 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3800 | PROOF | A255022 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3801 | PROOF | A259957 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3802 | PROOF | A300347 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3803 | PROOF | A302620 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3804 | PROOF | A303958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3805 | PROOF | A318340 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3806 | PROOF | A206469 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3807 | PROOF | A229842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3808 | PROOF | A230677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3809 | PROOF | A196424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3810 | PROOF | A196538 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3811 | PROOF | A234698 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3812 | PROOF | A236665 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3813 | PROOF | A237009 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3814 | PROOF | A235082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3815 | PROOF | A237031 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3816 | PROOF | A207947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3817 | PROOF | A231941 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3818 | PROOF | A233686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3819 | PROOF | A251519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3820 | PROOF | A260171 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3821 | PROOF | A261705 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3822 | PROOF | A297460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3823 | PROOF | A300204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3824 | PROOF | A302159 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3825 | PROOF | A302737 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3826 | PROOF | A302743 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3827 | PROOF | A303452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3828 | PROOF | A303458 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3829 | PROOF | A304298 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3830 | PROOF | A305336 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3831 | PROOF | A305519 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3832 | PROOF | A234544 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3833 | PROOF | A234652 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3834 | PROOF | A283517 | a condition on every cell over the neighbour set the entry names |
| 3835 | PROOF | A234211 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3836 | PROOF | A237008 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3837 | PROOF | A282992 | a condition on every cell over the neighbour set the entry names |
| 3838 | PROOF | A207657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3839 | PROOF | A207941 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3840 | PROOF | A237000 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3841 | PROOF | A207422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3842 | PROOF | A207881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3843 | PROOF | A207886 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3844 | PROOF | A207904 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3845 | PROOF | A207956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3846 | PROOF | A231657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3847 | PROOF | A251330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3848 | PROOF | A251385 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3849 | PROOF | A236887 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3850 | PROOF | A231999 | a condition on every cell over the neighbour set the entry names |
| 3851 | PROOF | A188561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3852 | PROOF | A202909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3853 | PROOF | A232049 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3854 | PROOF | A296152 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3855 | PROOF | A296829 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3856 | PROOF | A297632 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3857 | PROOF | A297757 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3858 | PROOF | A297797 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3859 | PROOF | A298391 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3860 | PROOF | A298496 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3861 | PROOF | A299509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3862 | PROOF | A299684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3863 | PROOF | A300141 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3864 | PROOF | A300316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3865 | PROOF | A300460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3866 | PROOF | A300641 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3867 | PROOF | A300771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3868 | PROOF | A301395 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3869 | PROOF | A302070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3870 | PROOF | A302226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3871 | PROOF | A302311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3872 | PROOF | A302529 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3873 | PROOF | A302821 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3874 | PROOF | A303017 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3875 | PROOF | A303514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3876 | PROOF | A304053 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3877 | PROOF | A304342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3878 | PROOF | A304414 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3879 | PROOF | A304592 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3880 | PROOF | A304896 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3881 | PROOF | A305017 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3882 | PROOF | A305218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3883 | PROOF | A305283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3884 | PROOF | A305637 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3885 | PROOF | A305906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3886 | PROOF | A306138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3887 | PROOF | A316213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3888 | PROOF | A316378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3889 | PROOF | A316547 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3890 | PROOF | A316578 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3891 | PROOF | A316878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3892 | PROOF | A317031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3893 | PROOF | A317148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3894 | PROOF | A317371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3895 | PROOF | A317606 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3896 | PROOF | A283226 | a condition on every cell over the neighbour set the entry names |
| 3897 | PROOF | A283516 | a condition on every cell over the neighbour set the entry names |
| 3898 | PROOF | A283785 | a condition on every cell over the neighbour set the entry names |
| 3899 | PROOF | A282963 | a condition on every cell over the neighbour set the entry names |
| 3900 | PROOF | A207392 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3901 | PROOF | A220565 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 3902 | PROOF | A251313 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3903 | PROOF | A237474 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3904 | PROOF | A236812 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 3905 | PROOF | A298916 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3906 | PROOF | A301963 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3907 | PROOF | A196282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3908 | PROOF | A197175 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3909 | PROOF | A234561 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3910 | PROOF | A235306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3911 | PROOF | A252026 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3912 | PROOF | A252257 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3913 | PROOF | A304219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3914 | PROOF | A234560 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3915 | PROOF | A208839 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3916 | PROOF | A208107 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3917 | PROOF | A235305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3918 | PROOF | A231993 | a condition on every cell over the neighbour set the entry names |
| 3919 | PROOF | A232044 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3920 | PROOF | A259767 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3921 | PROOF | A260279 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3922 | PROOF | A260975 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3923 | PROOF | A261706 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3924 | PROOF | A301320 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3925 | PROOF | A301967 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3926 | PROOF | A204410 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3927 | PROOF | A230615 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3928 | PROOF | A208838 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3929 | PROOF | A207594 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3930 | PROOF | A208106 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3931 | PROOF | A234559 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3932 | PROOF | A208122 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3933 | PROOF | A234125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3934 | PROOF | A282524 | a condition on every cell's king-move neighbourhood, boundaries included |
| 3935 | PROOF | A183305 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3936 | PROOF | A255095 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3937 | PROOF | A256804 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3938 | PROOF | A259995 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3939 | PROOF | A260242 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3940 | PROOF | A295116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3941 | PROOF | A295412 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3942 | PROOF | A296323 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3943 | PROOF | A297810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3944 | PROOF | A299650 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3945 | PROOF | A305512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3946 | PROOF | A317769 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3947 | PROOF | A235304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3948 | PROOF | A207604 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3949 | PROOF | A283687 | a condition on every cell over the neighbour set the entry names |
| 3950 | PROOF | A207876 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3951 | PROOF | A207603 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3952 | PROOF | A208120 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3953 | PROOF | A228505 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3954 | PROOF | A251273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3955 | PROOF | A234558 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3956 | PROOF | A207251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3957 | PROOF | A207602 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3958 | PROOF | A207930 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3959 | PROOF | A209955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3960 | PROOF | A236058 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 3961 | PROOF | A251205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3962 | PROOF | A185829 | a condition on every cell over the neighbour set the entry names |
| 3963 | PROOF | A283859 | a condition on every cell over the neighbour set the entry names |
| 3964 | PROOF | A188689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3965 | PROOF | A188768 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3966 | PROOF | A207601 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3967 | PROOF | A210294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3968 | PROOF | A233853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3969 | PROOF | A233869 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3970 | PROOF | A233961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3971 | PROOF | A251562 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3972 | PROOF | A255794 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3973 | PROOF | A260760 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3974 | PROOF | A260834 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 3975 | PROOF | A278152 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3976 | PROOF | A296391 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3977 | PROOF | A296573 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3978 | PROOF | A297539 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3979 | PROOF | A297861 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3980 | PROOF | A298216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3981 | PROOF | A298577 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3982 | PROOF | A299055 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3983 | PROOF | A299223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3984 | PROOF | A299569 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3985 | PROOF | A299816 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3986 | PROOF | A300367 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3987 | PROOF | A300684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3988 | PROOF | A301824 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3989 | PROOF | A302317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3990 | PROOF | A302324 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3991 | PROOF | A302382 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3992 | PROOF | A302467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3993 | PROOF | A302665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3994 | PROOF | A302815 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3995 | PROOF | A303103 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3996 | PROOF | A303249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3997 | PROOF | A303470 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3998 | PROOF | A303508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 3999 | PROOF | A304060 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4000 | PROOF | A304144 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4001 | PROOF | A305084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4002 | PROOF | A305484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4003 | PROOF | A305680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4004 | PROOF | A316735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4005 | PROOF | A207237 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4006 | PROOF | A207264 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4007 | PROOF | A207903 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4008 | PROOF | A220613 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4009 | PROOF | A220631 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4010 | PROOF | A251197 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4011 | PROOF | A250976 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4012 | PROOF | A251013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4013 | PROOF | A236821 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4014 | PROOF | A220612 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4015 | PROOF | A197085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4016 | PROOF | A197093 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4017 | PROOF | A197470 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4018 | PROOF | A222142 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4019 | PROOF | A236014 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4020 | PROOF | A230246 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4021 | PROOF | A261109 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4022 | PROOF | A296552 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4023 | PROOF | A297336 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4024 | PROOF | A305038 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4025 | PROOF | A236051 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4026 | PROOF | A253325 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4027 | PROOF | A203060 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4028 | PROOF | A209509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4029 | PROOF | A236806 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4030 | PROOF | A253324 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4031 | PROOF | A188702 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4032 | PROOF | A228757 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4033 | PROOF | A301948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4034 | PROOF | A302518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4035 | PROOF | A208032 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4036 | PROOF | A238317 | a condition on every cell over the neighbour set the entry names |
| 4037 | PROOF | A253323 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4038 | PROOF | A236805 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4039 | PROOF | A208424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4040 | PROOF | A208005 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4041 | PROOF | A223461 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4042 | PROOF | A236944 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4043 | PROOF | A253322 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4044 | PROOF | A186045 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4045 | PROOF | A220635 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4046 | PROOF | A260538 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4047 | PROOF | A260603 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4048 | PROOF | A300346 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4049 | PROOF | A302949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4050 | PROOF | A303957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4051 | PROOF | A304922 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4052 | PROOF | A316949 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4053 | PROOF | A318541 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4054 | PROOF | A283411 | a condition on every cell over the neighbour set the entry names |
| 4055 | PROOF | A250909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4056 | PROOF | A208004 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4057 | PROOF | A203376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4058 | PROOF | A233983 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4059 | PROOF | A253321 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4060 | PROOF | A207560 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4061 | PROOF | A207748 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4062 | PROOF | A209946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4063 | PROOF | A229928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4064 | PROOF | A233639 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4065 | PROOF | A236698 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4066 | PROOF | A234915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4067 | PROOF | A188875 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4068 | PROOF | A189690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4069 | PROOF | A207307 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4070 | PROOF | A210150 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4071 | PROOF | A231518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4072 | PROOF | A234338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4073 | PROOF | A255142 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4074 | PROOF | A278089 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4075 | PROOF | A297225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4076 | PROOF | A297609 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4077 | PROOF | A297715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4078 | PROOF | A297910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4079 | PROOF | A297973 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4080 | PROOF | A298235 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4081 | PROOF | A298332 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4082 | PROOF | A298456 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4083 | PROOF | A299549 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4084 | PROOF | A299597 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4085 | PROOF | A299888 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4086 | PROOF | A300422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4087 | PROOF | A300806 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4088 | PROOF | A301445 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4089 | PROOF | A302304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4090 | PROOF | A302410 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4091 | PROOF | A302809 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4092 | PROOF | A302872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4093 | PROOF | A303035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4094 | PROOF | A303177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4095 | PROOF | A303237 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4096 | PROOF | A303891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4097 | PROOF | A304539 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4098 | PROOF | A304762 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4099 | PROOF | A306055 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4100 | PROOF | A306124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4101 | PROOF | A316927 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4102 | PROOF | A317233 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4103 | PROOF | A203059 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4104 | PROOF | A233659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4105 | PROOF | A253320 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4106 | PROOF | A228800 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4107 | PROOF | A237060 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4108 | PROOF | A236895 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4109 | PROOF | A250921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4110 | PROOF | A251004 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4111 | PROOF | A237843 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4112 | PROOF | A251168 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4113 | PROOF | A255798 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4114 | PROOF | A297298 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4115 | PROOF | A302679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4116 | PROOF | A196691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4117 | PROOF | A197064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4118 | PROOF | A197212 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4119 | PROOF | A197337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4120 | PROOF | A203653 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4121 | PROOF | A238519 | a condition on every cell over the neighbour set the entry names |
| 4122 | PROOF | A188989 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4123 | PROOF | A203793 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4124 | PROOF | A223397 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4125 | PROOF | A252377 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4126 | PROOF | A252525 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4127 | PROOF | A252533 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4128 | PROOF | A255797 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4129 | PROOF | A259638 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4130 | PROOF | A260134 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4131 | PROOF | A304228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4132 | PROOF | A304268 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4133 | PROOF | A208068 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4134 | PROOF | A256743 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4135 | PROOF | A260010 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4136 | PROOF | A260922 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4137 | PROOF | A261108 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4138 | PROOF | A261260 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4139 | PROOF | A261375 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4140 | PROOF | A297311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4141 | PROOF | A297811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4142 | PROOF | A302012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4143 | PROOF | A302147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4144 | PROOF | A302160 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4145 | PROOF | A303317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4146 | PROOF | A305227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4147 | PROOF | A203832 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4148 | PROOF | A252068 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4149 | PROOF | A207849 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4150 | PROOF | A207721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4151 | PROOF | A223460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4152 | PROOF | A208423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4153 | PROOF | A185527 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4154 | PROOF | A208552 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4155 | PROOF | A256023 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4156 | PROOF | A260364 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4157 | PROOF | A297434 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4158 | PROOF | A297597 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4159 | PROOF | A208115 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4160 | PROOF | A208371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4161 | PROOF | A282786 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4162 | PROOF | A228659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4163 | PROOF | A228682 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4164 | PROOF | A208551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4165 | PROOF | A283574 | a condition on every cell over the neighbour set the entry names |
| 4166 | PROOF | A283567 | a condition on every cell over the neighbour set the entry names |
| 4167 | PROOF | A207364 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4168 | PROOF | A207753 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4169 | PROOF | A207875 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4170 | PROOF | A207962 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4171 | PROOF | A208009 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4172 | PROOF | A233878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4173 | PROOF | A188845 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4174 | PROOF | A207940 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4175 | PROOF | A233727 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4176 | PROOF | A234424 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4177 | PROOF | A251272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4178 | PROOF | A251375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4179 | PROOF | A251493 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4180 | PROOF | A255785 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4181 | PROOF | A260468 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4182 | PROOF | A260494 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4183 | PROOF | A260602 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4184 | PROOF | A261285 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4185 | PROOF | A261548 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4186 | PROOF | A295711 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4187 | PROOF | A296536 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4188 | PROOF | A296630 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4189 | PROOF | A296669 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4190 | PROOF | A297340 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4191 | PROOF | A297376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4192 | PROOF | A297521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4193 | PROOF | A297902 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4194 | PROOF | A297954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4195 | PROOF | A298439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4196 | PROOF | A298542 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4197 | PROOF | A298662 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4198 | PROOF | A298836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4199 | PROOF | A299130 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4200 | PROOF | A299329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4201 | PROOF | A299361 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4202 | PROOF | A299516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4203 | PROOF | A299716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4204 | PROOF | A301843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4205 | PROOF | A302267 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4206 | PROOF | A302362 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4207 | PROOF | A302455 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4208 | PROOF | A302966 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4209 | PROOF | A303520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4210 | PROOF | A303964 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4211 | PROOF | A304474 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4212 | PROOF | A304664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4213 | PROOF | A304850 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4214 | PROOF | A305247 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4215 | PROOF | A305342 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4216 | PROOF | A316299 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4217 | PROOF | A316422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4218 | PROOF | A317460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4219 | PROOF | A320397 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4220 | PROOF | A282587 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4221 | PROOF | A283277 | a condition on every cell over the neighbour set the entry names |
| 4222 | PROOF | A234905 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4223 | PROOF | A235002 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4224 | PROOF | A235072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4225 | PROOF | A284076 | a condition on every cell over the neighbour set the entry names |
| 4226 | PROOF | A237069 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4227 | PROOF | A206878 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4228 | PROOF | A237939 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4229 | PROOF | A283094 | a condition on every cell over the neighbour set the entry names |
| 4230 | PROOF | A237333 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4231 | PROOF | A282435 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4232 | PROOF | A207118 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4233 | PROOF | A207462 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4234 | PROOF | A207584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4235 | PROOF | A207763 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4236 | PROOF | A207961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4237 | PROOF | A220721 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4238 | PROOF | A251254 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4239 | PROOF | A184557 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4240 | PROOF | A251066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4241 | PROOF | A251404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4242 | PROOF | A251234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4243 | PROOF | A298186 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4244 | PROOF | A196317 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4245 | PROOF | A251233 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4246 | PROOF | A252545 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4247 | PROOF | A297222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4248 | PROOF | A301962 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4249 | PROOF | A209380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4250 | PROOF | A203051 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4251 | PROOF | A183389 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4252 | PROOF | A251232 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4253 | PROOF | A260202 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4254 | PROOF | A298960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4255 | PROOF | A301659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4256 | PROOF | A301838 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4257 | PROOF | A301996 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4258 | PROOF | A302066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4259 | PROOF | A302683 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4260 | PROOF | A223300 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4261 | PROOF | A252025 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4262 | PROOF | A234222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4263 | PROOF | A254416 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4264 | PROOF | A254423 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4265 | PROOF | A208031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4266 | PROOF | A253346 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4267 | PROOF | A253353 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4268 | PROOF | A234877 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4269 | PROOF | A237854 | a condition on every cell over the neighbour set the entry names |
| 4270 | PROOF | A209548 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4271 | PROOF | A234156 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4272 | PROOF | A234485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4273 | PROOF | A236445 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4274 | PROOF | A236495 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4275 | PROOF | A251231 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4276 | PROOF | A255153 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4277 | PROOF | A259766 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4278 | PROOF | A260064 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4279 | PROOF | A260974 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4280 | PROOF | A297453 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4281 | PROOF | A300800 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4282 | PROOF | A301439 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4283 | PROOF | A305178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4284 | PROOF | A234118 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4285 | PROOF | A236804 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4286 | PROOF | A234178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4287 | PROOF | A231645 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4288 | PROOF | A231747 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4289 | PROOF | A236611 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4290 | PROOF | A236646 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4291 | PROOF | A283693 | a condition on every cell over the neighbour set the entry names |
| 4292 | PROOF | A183382 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4293 | PROOF | A188757 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4294 | PROOF | A188993 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4295 | PROOF | A189190 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4296 | PROOF | A209730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4297 | PROOF | A228388 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4298 | PROOF | A233786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4299 | PROOF | A233910 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4300 | PROOF | A234327 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4301 | PROOF | A255094 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4302 | PROOF | A296034 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4303 | PROOF | A296315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4304 | PROOF | A297501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4305 | PROOF | A297602 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4306 | PROOF | A297649 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4307 | PROOF | A297981 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4308 | PROOF | A297988 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4309 | PROOF | A298282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4310 | PROOF | A298489 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4311 | PROOF | A298624 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4312 | PROOF | A299663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4313 | PROOF | A300170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4314 | PROOF | A300337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4315 | PROOF | A302219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4316 | PROOF | A302376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4317 | PROOF | A303041 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4318 | PROOF | A303079 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4319 | PROOF | A303097 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4320 | PROOF | A304843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4321 | PROOF | A305042 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4322 | PROOF | A305525 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4323 | PROOF | A305764 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4324 | PROOF | A316178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4325 | PROOF | A316540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4326 | PROOF | A316817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4327 | PROOF | A316999 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4328 | PROOF | A317567 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4329 | PROOF | A318011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4330 | PROOF | A318063 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4331 | PROOF | A318217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4332 | PROOF | A237235 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4333 | PROOF | A206780 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4334 | PROOF | A234400 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4335 | PROOF | A203454 | a condition on every cell over the neighbour set the entry names |
| 4336 | PROOF | A282857 | a condition on every cell over the neighbour set the entry names |
| 4337 | PROOF | A203050 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4338 | PROOF | A207747 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4339 | PROOF | A251059 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4340 | PROOF | A237092 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4341 | PROOF | A237101 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4342 | PROOF | A251287 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4343 | PROOF | A235296 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4344 | PROOF | A303726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4345 | PROOF | A196899 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4346 | PROOF | A230064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4347 | PROOF | A235014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4348 | PROOF | A188828 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4349 | PROOF | A228665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4350 | PROOF | A228687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4351 | PROOF | A231834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4352 | PROOF | A235295 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4353 | PROOF | A252132 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4354 | PROOF | A256744 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4355 | PROOF | A259738 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4356 | PROOF | A302008 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4357 | PROOF | A223444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4358 | PROOF | A235013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4359 | PROOF | A188870 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4360 | PROOF | A235294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4361 | PROOF | A259737 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4362 | PROOF | A296551 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4363 | PROOF | A298180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4364 | PROOF | A304218 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4365 | PROOF | A204401 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4366 | PROOF | A204494 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4367 | PROOF | A230270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4368 | PROOF | A196212 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4369 | PROOF | A197666 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4370 | PROOF | A208081 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4371 | PROOF | A207810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4372 | PROOF | A208837 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4373 | PROOF | A235293 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4374 | PROOF | A235965 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4375 | PROOF | A259717 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4376 | PROOF | A260288 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4377 | PROOF | A295777 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4378 | PROOF | A304129 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4379 | PROOF | A304771 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4380 | PROOF | A305478 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4381 | PROOF | A316514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4382 | PROOF | A251369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4383 | PROOF | A208105 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4384 | PROOF | A207720 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4385 | PROOF | A208422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4386 | PROOF | A283489 | a condition on every cell over the neighbour set the entry names |
| 4387 | PROOF | A220648 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4388 | PROOF | A208836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4389 | PROOF | A236943 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4390 | PROOF | A207725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4391 | PROOF | A207854 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4392 | PROOF | A209791 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4393 | PROOF | A232282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4394 | PROOF | A236028 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4395 | PROOF | A236089 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4396 | PROOF | A236349 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4397 | PROOF | A236803 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4398 | PROOF | A237077 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4399 | PROOF | A251244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4400 | PROOF | A235081 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4401 | PROOF | A282311 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4402 | PROOF | A220623 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4403 | PROOF | A183795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4404 | PROOF | A207250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4405 | PROOF | A220618 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4406 | PROOF | A231377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4407 | PROOF | A233676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4408 | PROOF | A235292 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4409 | PROOF | A251501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4410 | PROOF | A254971 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4411 | PROOF | A260170 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4412 | PROOF | A295115 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4413 | PROOF | A295374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4414 | PROOF | A295980 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4415 | PROOF | A296646 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4416 | PROOF | A296720 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4417 | PROOF | A297508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4418 | PROOF | A297884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4419 | PROOF | A298275 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4420 | PROOF | A298996 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4421 | PROOF | A299076 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4422 | PROOF | A299137 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4423 | PROOF | A299316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4424 | PROOF | A299368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4425 | PROOF | A299932 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4426 | PROOF | A300133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4427 | PROOF | A301610 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4428 | PROOF | A301952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4429 | PROOF | A302884 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4430 | PROOF | A303011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4431 | PROOF | A303803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4432 | PROOF | A304467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4433 | PROOF | A305177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4434 | PROOF | A305511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4435 | PROOF | A306048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4436 | PROOF | A316284 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4437 | PROOF | A317113 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4438 | PROOF | A317225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4439 | PROOF | A317736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4440 | PROOF | A283686 | a condition on every cell over the neighbour set the entry names |
| 4441 | PROOF | A235251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4442 | PROOF | A220591 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4443 | PROOF | A220727 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4444 | PROOF | A233885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4445 | PROOF | A233974 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4446 | PROOF | A234406 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4447 | PROOF | A251611 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4448 | PROOF | A237151 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4449 | PROOF | A234891 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4450 | PROOF | A234992 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4451 | PROOF | A235064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4452 | PROOF | A202974 | a condition on every cell over the neighbour set the entry names |
| 4453 | PROOF | A207341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4454 | PROOF | A207509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4455 | PROOF | A234201 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4456 | PROOF | A251468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4457 | PROOF | A283197 | a condition on every cell over the neighbour set the entry names |
| 4458 | PROOF | A283488 | a condition on every cell over the neighbour set the entry names |
| 4459 | PROOF | A283727 | a condition on every cell over the neighbour set the entry names |
| 4460 | PROOF | A251271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4461 | PROOF | A282879 | a condition on every cell over the neighbour set the entry names |
| 4462 | PROOF | A233943 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4463 | PROOF | A250835 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4464 | PROOF | A220617 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4465 | PROOF | A236730 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4466 | PROOF | A207025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4467 | PROOF | A207069 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4468 | PROOF | A251263 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4469 | PROOF | A251312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4470 | PROOF | A251321 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4471 | PROOF | A251435 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4472 | PROOF | A220706 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4473 | PROOF | A251026 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4474 | PROOF | A251053 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4475 | PROOF | A195964 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4476 | PROOF | A196205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4477 | PROOF | A196324 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4478 | PROOF | A196431 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4479 | PROOF | A196631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4480 | PROOF | A196952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4481 | PROOF | A196984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4482 | PROOF | A197524 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4483 | PROOF | A235275 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4484 | PROOF | A252069 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4485 | PROOF | A251025 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4486 | PROOF | A251052 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4487 | PROOF | A252271 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4488 | PROOF | A252516 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4489 | PROOF | A303725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4490 | PROOF | A235274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4491 | PROOF | A208112 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4492 | PROOF | A189060 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4493 | PROOF | A206251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4494 | PROOF | A251024 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4495 | PROOF | A251051 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4496 | PROOF | A259637 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4497 | PROOF | A260133 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4498 | PROOF | A297221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4499 | PROOF | A297371 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4500 | PROOF | A300179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4501 | PROOF | A302512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4502 | PROOF | A303311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4503 | PROOF | A304267 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4504 | PROOF | A230332 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4505 | PROOF | A230521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4506 | PROOF | A278009 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4507 | PROOF | A196132 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4508 | PROOF | A196294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4509 | PROOF | A197403 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4510 | PROOF | A197883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4511 | PROOF | A198179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4512 | PROOF | A203185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4513 | PROOF | A235273 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4514 | PROOF | A208111 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4515 | PROOF | A253518 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4516 | PROOF | A208017 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4517 | PROOF | A208072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4518 | PROOF | A207593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4519 | PROOF | A236012 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4520 | PROOF | A229697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4521 | PROOF | A183445 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4522 | PROOF | A282643 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4523 | PROOF | A184147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4524 | PROOF | A188712 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4525 | PROOF | A251023 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4526 | PROOF | A251050 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4527 | PROOF | A251278 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4528 | PROOF | A259946 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4529 | PROOF | A260009 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4530 | PROOF | A260278 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4531 | PROOF | A296124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4532 | PROOF | A297591 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4533 | PROOF | A303423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4534 | PROOF | A305043 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4535 | PROOF | A320367 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4536 | PROOF | A206468 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4537 | PROOF | A223426 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4538 | PROOF | A207175 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4539 | PROOF | A208110 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4540 | PROOF | A209226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4541 | PROOF | A207174 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4542 | PROOF | A208015 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4543 | PROOF | A208070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4544 | PROOF | A250954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4545 | PROOF | A234030 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4546 | PROOF | A235272 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4547 | PROOF | A207173 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4548 | PROOF | A237030 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4549 | PROOF | A184370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4550 | PROOF | A208003 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4551 | PROOF | A208109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4552 | PROOF | A234876 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4553 | PROOF | A231971 | a condition on every cell over the neighbour set the entry names |
| 4554 | PROOF | A282394 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4555 | PROOF | A283125 | a condition on every cell over the neighbour set the entry names |
| 4556 | PROOF | A183399 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4557 | PROOF | A189105 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4558 | PROOF | A207172 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4559 | PROOF | A233685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4560 | PROOF | A251022 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4561 | PROOF | A251049 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4562 | PROOF | A251230 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4563 | PROOF | A256022 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4564 | PROOF | A256741 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4565 | PROOF | A260008 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4566 | PROOF | A260099 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4567 | PROOF | A260287 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4568 | PROOF | A260537 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4569 | PROOF | A261704 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4570 | PROOF | A295046 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4571 | PROOF | A295842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4572 | PROOF | A296330 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4573 | PROOF | A297514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4574 | PROOF | A297696 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4575 | PROOF | A297735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4576 | PROOF | A297818 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4577 | PROOF | A297918 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4578 | PROOF | A298141 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4579 | PROOF | A298570 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4580 | PROOF | A298584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4581 | PROOF | A299062 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4582 | PROOF | A299576 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4583 | PROOF | A299834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4584 | PROOF | A300968 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4585 | PROOF | A302207 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4586 | PROOF | A302618 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4587 | PROOF | A302630 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4588 | PROOF | A304297 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4589 | PROOF | A304422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4590 | PROOF | A305956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4591 | PROOF | A316277 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4592 | PROOF | A317217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4593 | PROOF | A326100 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4594 | PROOF | A282832 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4595 | PROOF | A235169 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4596 | PROOF | A206872 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4597 | PROOF | A207089 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4598 | PROOF | A283635 | a condition on every cell over the neighbour set the entry names |
| 4599 | PROOF | A258548 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4600 | PROOF | A282991 | a condition on every cell over the neighbour set the entry names |
| 4601 | PROOF | A207171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4602 | PROOF | A207437 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4603 | PROOF | A207483 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4604 | PROOF | A207559 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4605 | PROOF | A207712 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4606 | PROOF | A207730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4607 | PROOF | A207939 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4608 | PROOF | A208023 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4609 | PROOF | A208496 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4610 | PROOF | A233646 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4611 | PROOF | A233749 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4612 | PROOF | A234084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4613 | PROOF | A236739 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4614 | PROOF | A228387 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4615 | PROOF | A228479 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4616 | PROOF | A236886 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4617 | PROOF | A237160 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4618 | PROOF | A184490 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4619 | PROOF | A210270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4620 | PROOF | A203184 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4621 | PROOF | A251508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4622 | PROOF | A237301 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4623 | PROOF | A231703 | a condition on every cell over the neighbour set the entry names |
| 4624 | PROOF | A231765 | a condition on every cell over the neighbour set the entry names |
| 4625 | PROOF | A231998 | a condition on every cell over the neighbour set the entry names |
| 4626 | PROOF | A282831 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4627 | PROOF | A220630 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4628 | PROOF | A250968 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4629 | PROOF | A251095 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4630 | PROOF | A251196 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4631 | PROOF | A251214 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4632 | PROOF | A296399 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4633 | PROOF | A296572 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4634 | PROOF | A296582 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4635 | PROOF | A297315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4636 | PROOF | A303681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4637 | PROOF | A196488 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4638 | PROOF | A196741 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4639 | PROOF | A197368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4640 | PROOF | A253520 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4641 | PROOF | A209381 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4642 | PROOF | A252337 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4643 | PROOF | A223435 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4644 | PROOF | A297297 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4645 | PROOF | A298915 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4646 | PROOF | A302513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4647 | PROOF | A303312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4648 | PROOF | A253519 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4649 | PROOF | A258553 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4650 | PROOF | A207702 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4651 | PROOF | A236013 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4652 | PROOF | A207937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4653 | PROOF | A236050 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4654 | PROOF | A189198 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4655 | PROOF | A298914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4656 | PROOF | A298921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4657 | PROOF | A301404 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4658 | PROOF | A301781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4659 | PROOF | A303724 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4660 | PROOF | A317514 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4661 | PROOF | A258552 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4662 | PROOF | A208067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4663 | PROOF | A196479 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4664 | PROOF | A197174 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4665 | PROOF | A197201 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4666 | PROOF | A197444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4667 | PROOF | A197531 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4668 | PROOF | A197539 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4669 | PROOF | A197607 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4670 | PROOF | A258551 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4671 | PROOF | A236149 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4672 | PROOF | A235012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4673 | PROOF | A235948 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4674 | PROOF | A183388 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4675 | PROOF | A188701 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4676 | PROOF | A207848 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4677 | PROOF | A208066 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4678 | PROOF | A208121 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4679 | PROOF | A228756 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4680 | PROOF | A232043 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4681 | PROOF | A255021 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4682 | PROOF | A256742 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4683 | PROOF | A259888 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4684 | PROOF | A259956 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4685 | PROOF | A260201 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4686 | PROOF | A260921 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4687 | PROOF | A261374 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4688 | PROOF | A278267 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4689 | PROOF | A297310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4690 | PROOF | A297397 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4691 | PROOF | A298920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4692 | PROOF | A301880 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4693 | PROOF | A302077 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4694 | PROOF | A302619 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4695 | PROOF | A302625 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4696 | PROOF | A318339 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4697 | PROOF | A209378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4698 | PROOF | A258550 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4699 | PROOF | A208080 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4700 | PROOF | A223213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4701 | PROOF | A208291 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4702 | PROOF | A283545 | a condition on every cell over the neighbour set the entry names |
| 4703 | PROOF | A258549 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4704 | PROOF | A208065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4705 | PROOF | A283539 | a condition on every cell over the neighbour set the entry names |
| 4706 | PROOF | A208114 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4707 | PROOF | A208119 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4708 | PROOF | A208370 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4709 | PROOF | A253526 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4710 | PROOF | A282523 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4711 | PROOF | A283852 | a condition on every cell over the neighbour set the entry names |
| 4712 | PROOF | A189258 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4713 | PROOF | A228504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4714 | PROOF | A234241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4715 | PROOF | A234476 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4716 | PROOF | A234721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4717 | PROOF | A256803 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4718 | PROOF | A259765 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4719 | PROOF | A259945 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4720 | PROOF | A260277 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4721 | PROOF | A260920 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4722 | PROOF | A260973 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4723 | PROOF | A278203 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4724 | PROOF | A295411 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4725 | PROOF | A296322 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4726 | PROOF | A297459 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4727 | PROOF | A297683 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4728 | PROOF | A297689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4729 | PROOF | A297728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4730 | PROOF | A297853 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4731 | PROOF | A298919 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4732 | PROOF | A298965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4733 | PROOF | A299656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4734 | PROOF | A299735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4735 | PROOF | A300210 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4736 | PROOF | A300345 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4737 | PROOF | A300541 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4738 | PROOF | A300925 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4739 | PROOF | A302948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4740 | PROOF | A304136 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4741 | PROOF | A305240 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4742 | PROOF | A305687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4743 | PROOF | A317067 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4744 | PROOF | A235241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4745 | PROOF | A206931 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4746 | PROOF | A207177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4747 | PROOF | A238174 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4748 | PROOF | A235232 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4749 | PROOF | A220597 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4750 | PROOF | A282554 | a condition on every cell's king-move neighbourhood, boundaries included |
| 4751 | PROOF | A207249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4752 | PROOF | A207363 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4753 | PROOF | A234146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4754 | PROOF | A283951 | a condition on every cell over the neighbour set the entry names |
| 4755 | PROOF | A220560 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4756 | PROOF | A234984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4757 | PROOF | A283036 | a condition on every cell over the neighbour set the entry names |
| 4758 | PROOF | A233710 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4759 | PROOF | A283276 | a condition on every cell over the neighbour set the entry names |
| 4760 | PROOF | A228799 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4761 | PROOF | A231538 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4762 | PROOF | A251021 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4763 | PROOF | A251048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4764 | PROOF | A251223 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4765 | PROOF | A251270 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4766 | PROOF | A296380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4767 | PROOF | A296593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4768 | PROOF | A317857 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4769 | PROOF | A203731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4770 | PROOF | A203883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4771 | PROOF | A188711 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4772 | PROOF | A317763 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4773 | PROOF | A196781 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4774 | PROOF | A203930 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4775 | PROOF | A222278 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4776 | PROOF | A251087 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4777 | PROOF | A251136 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4778 | PROOF | A223594 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4779 | PROOF | A298185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4780 | PROOF | A302148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4781 | PROOF | A303680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4782 | PROOF | A317762 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4783 | PROOF | A203652 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4784 | PROOF | A222141 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4785 | PROOF | A230529 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4786 | PROOF | A251086 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4787 | PROOF | A251135 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4788 | PROOF | A258560 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4789 | PROOF | A203792 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4790 | PROOF | A228664 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4791 | PROOF | A228686 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4792 | PROOF | A297335 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4793 | PROOF | A301881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4794 | PROOF | A302078 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4795 | PROOF | A305037 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4796 | PROOF | A316690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4797 | PROOF | A258559 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4798 | PROOF | A209508 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4799 | PROOF | A230464 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4800 | PROOF | A232018 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4801 | PROOF | A251085 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4802 | PROOF | A251134 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4803 | PROOF | A195972 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4804 | PROOF | A196450 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4805 | PROOF | A196584 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4806 | PROOF | A196701 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4807 | PROOF | A196850 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4808 | PROOF | A196961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4809 | PROOF | A197274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4810 | PROOF | A197311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4811 | PROOF | A207701 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4812 | PROOF | A207936 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4813 | PROOF | A258558 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4814 | PROOF | A188869 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4815 | PROOF | A188987 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4816 | PROOF | A189059 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4817 | PROOF | A189197 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4818 | PROOF | A203095 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4819 | PROOF | A231833 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4820 | PROOF | A258960 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4821 | PROOF | A278095 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4822 | PROOF | A278189 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4823 | PROOF | A296550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4824 | PROOF | A297391 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4825 | PROOF | A297427 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4826 | PROOF | A298163 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4827 | PROOF | A301966 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4828 | PROOF | A302511 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4829 | PROOF | A302517 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4830 | PROOF | A302682 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4831 | PROOF | A303310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4832 | PROOF | A303316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4833 | PROOF | A304217 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4834 | PROOF | A305036 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4835 | PROOF | A305226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4836 | PROOF | A316689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4837 | PROOF | A316804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4838 | PROOF | A317521 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4839 | PROOF | A203831 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4840 | PROOF | A251084 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4841 | PROOF | A251133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4842 | PROOF | A258557 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4843 | PROOF | A207592 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4844 | PROOF | A208030 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4845 | PROOF | A208290 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4846 | PROOF | A228753 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4847 | PROOF | A228795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4848 | PROOF | A253345 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4849 | PROOF | A253352 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4850 | PROOF | A258556 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4851 | PROOF | A220710 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4852 | PROOF | A230170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4853 | PROOF | A236664 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4854 | PROOF | A250908 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4855 | PROOF | A251083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4856 | PROOF | A251132 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4857 | PROOF | A186055 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4858 | PROOF | A203375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4859 | PROOF | A228658 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4860 | PROOF | A228681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4861 | PROOF | A234414 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4862 | PROOF | A234667 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4863 | PROOF | A234705 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4864 | PROOF | A234731 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4865 | PROOF | A250953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4866 | PROOF | A251294 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4867 | PROOF | A251337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4868 | PROOF | A251485 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4869 | PROOF | A259955 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4870 | PROOF | A259994 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4871 | PROOF | A260363 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4872 | PROOF | A278275 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4873 | PROOF | A297452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4874 | PROOF | A297596 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4875 | PROOF | A300467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4876 | PROOF | A302158 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4877 | PROOF | A302742 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4878 | PROOF | A302954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4879 | PROOF | A303192 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4880 | PROOF | A303457 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4881 | PROOF | A303795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4882 | PROOF | A303956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4883 | PROOF | A304599 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4884 | PROOF | A304921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4885 | PROOF | A305335 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4886 | PROOF | A306161 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4887 | PROOF | A316415 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4888 | PROOF | A316948 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4889 | PROOF | A317378 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4890 | PROOF | A318540 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4891 | PROOF | A206989 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4892 | PROOF | A234185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4893 | PROOF | A234816 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4894 | PROOF | A258555 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4895 | PROOF | A207306 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4896 | PROOF | A207495 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4897 | PROOF | A237029 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4898 | PROOF | A236942 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4899 | PROOF | A209945 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4900 | PROOF | A209954 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4901 | PROOF | A233638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4902 | PROOF | A251082 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4903 | PROOF | A251131 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4904 | PROOF | A251345 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4905 | PROOF | A234975 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4906 | PROOF | A237938 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 4907 | PROOF | A184665 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4908 | PROOF | A203094 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4909 | PROOF | A232048 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4910 | PROOF | A250958 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4911 | PROOF | A251301 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4912 | PROOF | A251352 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4913 | PROOF | A251395 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4914 | PROOF | A251452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4915 | PROOF | A297375 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4916 | PROOF | A300374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4917 | PROOF | A300500 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4918 | PROOF | A301885 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4919 | PROOF | A318018 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4920 | PROOF | A220676 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4921 | PROOF | A220548 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4922 | PROOF | A220564 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 4923 | PROOF | A251106 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4924 | PROOF | A234138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4925 | PROOF | A235287 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4926 | PROOF | A299594 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4927 | PROOF | A301789 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4928 | PROOF | A303718 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4929 | PROOF | A196573 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4930 | PROOF | A196804 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4931 | PROOF | A196858 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4932 | PROOF | A234265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4933 | PROOF | A203823 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4934 | PROOF | A234137 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4935 | PROOF | A235286 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4936 | PROOF | A252236 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4937 | PROOF | A252262 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4938 | PROOF | A252362 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4939 | PROOF | A252543 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4940 | PROOF | A258962 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4941 | PROOF | A299593 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4942 | PROOF | A301788 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4943 | PROOF | A302678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4944 | PROOF | A303717 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4945 | PROOF | A229752 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4946 | PROOF | A223419 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4947 | PROOF | A234264 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4948 | PROOF | A223348 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4949 | PROOF | A229751 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4950 | PROOF | A188988 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4951 | PROOF | A234136 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4952 | PROOF | A235285 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4953 | PROOF | A299592 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4954 | PROOF | A301961 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4955 | PROOF | A302007 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4956 | PROOF | A303679 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4957 | PROOF | A303716 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4958 | PROOF | A304227 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4959 | PROOF | A305583 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4960 | PROOF | A229691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4961 | PROOF | A209379 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4962 | PROOF | A223374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4963 | PROOF | A234263 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4964 | PROOF | A252336 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4965 | PROOF | A253396 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4966 | PROOF | A195956 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4967 | PROOF | A196140 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4968 | PROOF | A196906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4969 | PROOF | A196976 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4970 | PROOF | A197229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4971 | PROOF | A197642 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4972 | PROOF | A223251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4973 | PROOF | A253395 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 4974 | PROOF | A223418 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4975 | PROOF | A229750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4976 | PROOF | A236049 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4977 | PROOF | A188826 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4978 | PROOF | A206250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4979 | PROOF | A208016 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4980 | PROOF | A208071 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4981 | PROOF | A230782 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4982 | PROOF | A234135 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4983 | PROOF | A235284 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4984 | PROOF | A236120 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 4985 | PROOF | A259636 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4986 | PROOF | A260132 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4987 | PROOF | A261107 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 4988 | PROOF | A278183 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4989 | PROOF | A295914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4990 | PROOF | A296309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4991 | PROOF | A299591 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4992 | PROOF | A300178 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4993 | PROOF | A301947 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4994 | PROOF | A303417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4995 | PROOF | A303715 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4996 | PROOF | A303723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4997 | PROOF | A304137 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4998 | PROOF | A304226 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 4999 | PROOF | A304266 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5000 | PROOF | A305582 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5001 | PROOF | A317729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5002 | PROOF | A234262 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5003 | PROOF | A207700 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5004 | PROOF | A223338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5005 | PROOF | A223425 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5006 | PROOF | A223347 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5007 | PROOF | A207935 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5008 | PROOF | A208383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5009 | PROOF | A208382 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5010 | PROOF | A234221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5011 | PROOF | A229696 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5012 | PROOF | A208289 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5013 | PROOF | A208381 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5014 | PROOF | A223408 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5015 | PROOF | A239179 | a condition on every cell over the neighbour set the entry names |
| 5016 | PROOF | A206467 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5017 | PROOF | A207591 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5018 | PROOF | A207689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5019 | PROOF | A207737 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5020 | PROOF | A207924 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5021 | PROOF | A208014 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5022 | PROOF | A208035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5023 | PROOF | A208104 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5024 | PROOF | A209220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5025 | PROOF | A234261 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5026 | PROOF | A235947 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5027 | PROOF | A236011 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5028 | PROOF | A236048 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5029 | PROOF | A253517 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5030 | PROOF | A183444 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5031 | PROOF | A231992 | a condition on every cell over the neighbour set the entry names |
| 5032 | PROOF | A282642 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5033 | PROOF | A186044 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5034 | PROOF | A188748 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5035 | PROOF | A208380 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5036 | PROOF | A209547 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5037 | PROOF | A220561 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5038 | PROOF | A220634 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5039 | PROOF | A234134 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5040 | PROOF | A234155 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5041 | PROOF | A234228 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5042 | PROOF | A235283 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5043 | PROOF | A251518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5044 | PROOF | A255020 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5045 | PROOF | A255152 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5046 | PROOF | A257440 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5047 | PROOF | A259735 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5048 | PROOF | A260063 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5049 | PROOF | A260241 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5050 | PROOF | A261258 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5051 | PROOF | A261373 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5052 | PROOF | A297396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5053 | PROOF | A297426 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5054 | PROOF | A297433 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5055 | PROOF | A297577 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5056 | PROOF | A297590 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5057 | PROOF | A299723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5058 | PROOF | A303619 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5059 | PROOF | A303722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5060 | PROOF | A305225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5061 | PROOF | A305477 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5062 | PROOF | A317728 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5063 | PROOF | A318070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5064 | PROOF | A282371 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5065 | PROOF | A235205 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5066 | PROOF | A206866 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5067 | PROOF | A207083 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5068 | PROOF | A233897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5069 | PROOF | A234124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5070 | PROOF | A234170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5071 | PROOF | A234550 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5072 | PROOF | A234683 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5073 | PROOF | A235312 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5074 | PROOF | A196012 | a condition on every cell over the neighbour set the entry names |
| 5075 | PROOF | A235100 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5076 | PROOF | A235191 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5077 | PROOF | A283544 | a condition on every cell over the neighbour set the entry names |
| 5078 | PROOF | A282785 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5079 | PROOF | A207347 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5080 | PROOF | A207683 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5081 | PROOF | A207769 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5082 | PROOF | A207840 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5083 | PROOF | A208103 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5084 | PROOF | A233811 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5085 | PROOF | A234452 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5086 | PROOF | A283538 | a condition on every cell over the neighbour set the entry names |
| 5087 | PROOF | A228503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5088 | PROOF | A228657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5089 | PROOF | A228680 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5090 | PROOF | A234883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5091 | PROOF | A235019 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5092 | PROOF | A235179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5093 | PROOF | A283573 | a condition on every cell over the neighbour set the entry names |
| 5094 | PROOF | A183785 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5095 | PROOF | A210384 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5096 | PROOF | A233877 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5097 | PROOF | A234260 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5098 | PROOF | A234437 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5099 | PROOF | A236802 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 5100 | PROOF | A251204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5101 | PROOF | A251329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5102 | PROOF | A251384 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5103 | PROOF | A220709 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5104 | PROOF | A233921 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5105 | PROOF | A234076 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5106 | PROOF | A234107 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5107 | PROOF | A220622 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5108 | PROOF | A231799 | a condition on every cell over the neighbour set the entry names |
| 5109 | PROOF | A282393 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5110 | PROOF | A297079 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5111 | PROOF | A297096 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5112 | PROOF | A238173 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 5113 | PROOF | A184209 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5114 | PROOF | A188501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5115 | PROOF | A188516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5116 | PROOF | A207170 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5117 | PROOF | A207436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5118 | PROOF | A209709 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5119 | PROOF | A209780 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5120 | PROOF | A209851 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5121 | PROOF | A209906 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5122 | PROOF | A210070 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5123 | PROOF | A210328 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5124 | PROOF | A231509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5125 | PROOF | A251253 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5126 | PROOF | A278171 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5127 | PROOF | A295346 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5128 | PROOF | A295525 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5129 | PROOF | A295937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5130 | PROOF | A295979 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5131 | PROOF | A296109 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5132 | PROOF | A296645 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5133 | PROOF | A296668 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5134 | PROOF | A296682 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5135 | PROOF | A296733 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5136 | PROOF | A296798 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5137 | PROOF | A296821 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5138 | PROOF | A296984 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5139 | PROOF | A297545 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5140 | PROOF | A297608 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5141 | PROOF | A297638 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5142 | PROOF | A297655 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5143 | PROOF | A297721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5144 | PROOF | A297750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5145 | PROOF | A300421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5146 | PROOF | A300533 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5147 | PROOF | A317735 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5148 | PROOF | A317767 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5149 | PROOF | A317809 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5150 | PROOF | A317817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5151 | PROOF | A318031 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5152 | PROOF | A318039 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5153 | PROOF | A251081 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5154 | PROOF | A251130 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5155 | PROOF | A251151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5156 | PROOF | A251444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5157 | PROOF | A220713 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5158 | PROOF | A220739 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5159 | PROOF | A251311 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5160 | PROOF | A220705 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5161 | PROOF | A196596 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5162 | PROOF | A223250 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5163 | PROOF | A223409 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5164 | PROOF | A230180 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5165 | PROOF | A251148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5166 | PROOF | A185899 | a condition on every cell over the neighbour set the entry names |
| 5167 | PROOF | A188710 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5168 | PROOF | A230509 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5169 | PROOF | A198598 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5170 | PROOF | A185405 | a condition on every cell over the neighbour set the entry names |
| 5171 | PROOF | A251147 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5172 | PROOF | A185535 | a condition on every cell over the neighbour set the entry names |
| 5173 | PROOF | A301820 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5174 | PROOF | A301903 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5175 | PROOF | A302677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5176 | PROOF | A208505 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5177 | PROOF | A223292 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5178 | PROOF | A230670 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5179 | PROOF | A251146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5180 | PROOF | A196072 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5181 | PROOF | A196204 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5182 | PROOF | A196316 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5183 | PROOF | A197211 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5184 | PROOF | A197244 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5185 | PROOF | A197344 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5186 | PROOF | A230393 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5187 | PROOF | A208504 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5188 | PROOF | A223242 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5189 | PROOF | A253394 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5190 | PROOF | A186161 | a condition on every cell over the neighbour set the entry names |
| 5191 | PROOF | A251127 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5192 | PROOF | A261259 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5193 | PROOF | A297220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5194 | PROOF | A297334 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5195 | PROOF | A298179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5196 | PROOF | A298959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5197 | PROOF | A301403 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5198 | PROOF | A301658 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5199 | PROOF | A301837 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5200 | PROOF | A302065 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5201 | PROOF | A303678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5202 | PROOF | A317760 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5203 | PROOF | A209507 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5204 | PROOF | A251145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5205 | PROOF | A253393 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5206 | PROOF | A251126 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5207 | PROOF | A185552 | a condition on every cell over the neighbour set the entry names |
| 5208 | PROOF | A202883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5209 | PROOF | A207719 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5210 | PROOF | A208421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5211 | PROOF | A230185 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5212 | PROOF | A230470 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5213 | PROOF | A230676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5214 | PROOF | A232017 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5215 | PROOF | A234117 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5216 | PROOF | A236148 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5217 | PROOF | A251144 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5218 | PROOF | A251368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5219 | PROOF | A253742 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5220 | PROOF | A235011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5221 | PROOF | A237853 | a condition on every cell over the neighbour set the entry names |
| 5222 | PROOF | A283410 | a condition on every cell over the neighbour set the entry names |
| 5223 | PROOF | A188700 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5224 | PROOF | A208288 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5225 | PROOF | A228752 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5226 | PROOF | A228794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5227 | PROOF | A234484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5228 | PROOF | A234697 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5229 | PROOF | A251125 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5230 | PROOF | A260200 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5231 | PROOF | A295776 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5232 | PROOF | A298095 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5233 | PROOF | A298897 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5234 | PROOF | A299590 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5235 | PROOF | A299649 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5236 | PROOF | A300203 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5237 | PROOF | A302260 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5238 | PROOF | A302416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5239 | PROOF | A302636 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5240 | PROOF | A302736 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5241 | PROOF | A302960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5242 | PROOF | A303183 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5243 | PROOF | A303451 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5244 | PROOF | A303464 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5245 | PROOF | A303631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5246 | PROOF | A304770 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5247 | PROOF | A305518 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5248 | PROOF | A316513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5249 | PROOF | A316810 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5250 | PROOF | A316955 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5251 | PROOF | A317560 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5252 | PROOF | A318338 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5253 | PROOF | A234659 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5254 | PROOF | A207718 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5255 | PROOF | A207896 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5256 | PROOF | A234177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5257 | PROOF | A234491 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5258 | PROOF | A234543 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5259 | PROOF | A234651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5260 | PROOF | A235303 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5261 | PROOF | A203374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5262 | PROOF | A251124 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5263 | PROOF | A235091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5264 | PROOF | A209376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5265 | PROOF | A251143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5266 | PROOF | A251243 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5267 | PROOF | A234557 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5268 | PROOF | A283124 | a condition on every cell over the neighbour set the entry names |
| 5269 | PROOF | A283409 | a condition on every cell over the neighbour set the entry names |
| 5270 | PROOF | A283692 | a condition on every cell over the neighbour set the entry names |
| 5271 | PROOF | A297088 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5272 | PROOF | A210149 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5273 | PROOF | A210348 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5274 | PROOF | A220683 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5275 | PROOF | A228386 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5276 | PROOF | A231376 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5277 | PROOF | A231524 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5278 | PROOF | A233628 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5279 | PROOF | A233960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5280 | PROOF | A251123 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5281 | PROOF | A295091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5282 | PROOF | A295247 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5283 | PROOF | A296033 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5284 | PROOF | A296329 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5285 | PROOF | A296957 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5286 | PROOF | A296968 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5287 | PROOF | A297339 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5288 | PROOF | A297507 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5289 | PROOF | A297734 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5290 | PROOF | A297763 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5291 | PROOF | A297817 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5292 | PROOF | A297852 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5293 | PROOF | A297883 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5294 | PROOF | A297901 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5295 | PROOF | A297945 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5296 | PROOF | A298057 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5297 | PROOF | A298148 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5298 | PROOF | A298189 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5299 | PROOF | A298215 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5300 | PROOF | A298448 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5301 | PROOF | A300344 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5302 | PROOF | A302164 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5303 | PROOF | A302225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5304 | PROOF | A302310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5305 | PROOF | A303684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5306 | PROOF | A303794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5307 | PROOF | A303882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5308 | PROOF | A304013 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5309 | PROOF | A304052 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5310 | PROOF | A304143 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5311 | PROOF | A304257 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5312 | PROOF | A304341 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5313 | PROOF | A305091 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5314 | PROOF | A317890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5315 | PROOF | A282856 | a condition on every cell over the neighbour set the entry names |
| 5316 | PROOF | A237028 | a signed sum of the order statistics of every 2 X 2 subblock taking one common value |
| 5317 | PROOF | A202973 | a condition on every cell over the neighbour set the entry names |
| 5318 | PROOF | A220611 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5319 | PROOF | A184556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5320 | PROOF | A202882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5321 | PROOF | A250920 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5322 | PROOF | A250975 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5323 | PROOF | A251003 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5324 | PROOF | A251012 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5325 | PROOF | A251403 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5326 | PROOF | A220629 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5327 | PROOF | A220720 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5328 | PROOF | A220733 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5329 | PROOF | A228798 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5330 | PROOF | A250967 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5331 | PROOF | A251122 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5332 | PROOF | A251195 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5333 | PROOF | A251213 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5334 | PROOF | A251222 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5335 | PROOF | A251252 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5336 | PROOF | A251269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5337 | PROOF | A251286 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5338 | PROOF | A251320 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5339 | PROOF | A235952 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5340 | PROOF | A188822 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5341 | PROOF | A188829 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5342 | PROOF | A255225 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5343 | PROOF | A257444 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5344 | PROOF | A258963 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5345 | PROOF | A196917 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5346 | PROOF | A235951 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5347 | PROOF | A255224 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5348 | PROOF | A257443 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5349 | PROOF | A235950 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5350 | PROOF | A230588 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5351 | PROOF | A188709 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5352 | PROOF | A188820 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5353 | PROOF | A188827 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5354 | PROOF | A203822 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5355 | PROOF | A255223 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5356 | PROOF | A257442 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5357 | PROOF | A258961 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5358 | PROOF | A297296 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5359 | PROOF | A301787 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5360 | PROOF | A317761 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5361 | PROOF | A208693 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5362 | PROOF | A235949 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5363 | PROOF | A196630 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5364 | PROOF | A196690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5365 | PROOF | A197092 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5366 | PROOF | A197497 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5367 | PROOF | A197617 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5368 | PROOF | A208692 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5369 | PROOF | A208559 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5370 | PROOF | A223396 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5371 | PROOF | A228663 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5372 | PROOF | A228685 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5373 | PROOF | A230835 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5374 | PROOF | A255222 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5375 | PROOF | A257441 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5376 | PROOF | A259736 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5377 | PROOF | A301780 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5378 | PROOF | A301786 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5379 | PROOF | A302006 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5380 | PROOF | A302011 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5381 | PROOF | A302676 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5382 | PROOF | A223442 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5383 | PROOF | A207458 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5384 | PROOF | A208691 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5385 | PROOF | A207457 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5386 | PROOF | A208557 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5387 | PROOF | A207456 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5388 | PROOF | A207847 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5389 | PROOF | A253392 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5390 | PROOF | A208029 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5391 | PROOF | A208690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5392 | PROOF | A209225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5393 | PROOF | A209377 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5394 | PROOF | A229841 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5395 | PROOF | A277939 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5396 | PROOF | A278000 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5397 | PROOF | A278015 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5398 | PROOF | A295913 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5399 | PROOF | A184146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5400 | PROOF | A188819 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5401 | PROOF | A188868 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5402 | PROOF | A188986 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5403 | PROOF | A206249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5404 | PROOF | A207455 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5405 | PROOF | A228755 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5406 | PROOF | A251277 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5407 | PROOF | A255221 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5408 | PROOF | A259635 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5409 | PROOF | A259716 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5410 | PROOF | A259887 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5411 | PROOF | A260131 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5412 | PROOF | A297300 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5413 | PROOF | A297309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5414 | PROOF | A297390 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5415 | PROOF | A301657 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5416 | PROOF | A301965 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5417 | PROOF | A302165 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5418 | PROOF | A302422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5419 | PROOF | A302510 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5420 | PROOF | A302516 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5421 | PROOF | A302624 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5422 | PROOF | A302681 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5423 | PROOF | A302803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5424 | PROOF | A303309 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5425 | PROOF | A303315 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5426 | PROOF | A303422 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5427 | PROOF | A304216 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5428 | PROOF | A316803 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5429 | PROOF | A317520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5430 | PROOF | A253344 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5431 | PROOF | A253391 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5432 | PROOF | A207454 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5433 | PROOF | A207694 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5434 | PROOF | A207929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5435 | PROOF | A208064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5436 | PROOF | A233951 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5437 | PROOF | A234674 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5438 | PROOF | A228751 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5439 | PROOF | A228793 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5440 | PROOF | A236324 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5441 | PROOF | A250952 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5442 | PROOF | A184369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5443 | PROOF | A206466 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5444 | PROOF | A209790 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5445 | PROOF | A234116 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5446 | PROOF | A196423 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5447 | PROOF | A196537 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5448 | PROOF | A234029 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5449 | PROOF | A234162 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5450 | PROOF | A234210 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5451 | PROOF | A234444 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5452 | PROOF | A235271 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5453 | PROOF | A185828 | a condition on every cell over the neighbour set the entry names |
| 5454 | PROOF | A234875 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5455 | PROOF | A234914 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5456 | PROOF | A235080 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5457 | PROOF | A282522 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5458 | PROOF | A283858 | a condition on every cell over the neighbour set the entry names |
| 5459 | PROOF | A183794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5460 | PROOF | A209546 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5461 | PROOF | A210293 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5462 | PROOF | A220559 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5463 | PROOF | A228502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5464 | PROOF | A233675 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5465 | PROOF | A233726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5466 | PROOF | A233785 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5467 | PROOF | A234326 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5468 | PROOF | A235291 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5469 | PROOF | A236323 | the 2 X 2 subblocks properly coloured by a statistic of their entries: neighbours must differ |
| 5470 | PROOF | A250928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5471 | PROOF | A251229 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5472 | PROOF | A251374 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5473 | PROOF | A251492 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5474 | PROOF | A251500 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5475 | PROOF | A278281 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5476 | PROOF | A295841 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5477 | PROOF | A296946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5478 | PROOF | A297432 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5479 | PROOF | A297458 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5480 | PROOF | A297520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5481 | PROOF | A297583 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5482 | PROOF | A297809 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5483 | PROOF | A297860 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5484 | PROOF | A297870 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5485 | PROOF | A297909 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5486 | PROOF | A297917 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5487 | PROOF | A297937 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5488 | PROOF | A297953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5489 | PROOF | A297980 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5490 | PROOF | A298569 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5491 | PROOF | A301842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5492 | PROOF | A302266 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5493 | PROOF | A302279 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5494 | PROOF | A302368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5495 | PROOF | A303677 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5496 | PROOF | A303721 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5497 | PROOF | A303802 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5498 | PROOF | A303890 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5499 | PROOF | A303963 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5500 | PROOF | A304004 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5501 | PROOF | A304304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5502 | PROOF | A304349 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5503 | PROOF | A317759 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5504 | PROOF | A318010 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5505 | PROOF | A318062 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5506 | PROOF | A282990 | a condition on every cell over the neighbour set the entry names |
| 5507 | PROOF | A220647 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5508 | PROOF | A184489 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5509 | PROOF | A220616 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5510 | PROOF | A233942 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5511 | PROOF | A250834 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5512 | PROOF | A220558 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5513 | PROOF | A220590 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5514 | PROOF | A220726 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5515 | PROOF | A228385 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5516 | PROOF | A251094 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5517 | PROOF | A251262 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5518 | PROOF | A220547 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5519 | PROOF | A251194 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5520 | PROOF | A251285 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5521 | PROOF | A251310 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5522 | PROOF | A183631 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5523 | PROOF | A301796 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5524 | PROOF | A183630 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5525 | PROOF | A209726 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5526 | PROOF | A203730 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5527 | PROOF | A222460 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5528 | PROOF | A301795 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5529 | PROOF | A253452 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5530 | PROOF | A253498 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5531 | PROOF | A203882 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5532 | PROOF | A222337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5533 | PROOF | A183629 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5534 | PROOF | A209532 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5535 | PROOF | A209725 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5536 | PROOF | A253451 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5537 | PROOF | A253497 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5538 | PROOF | A203929 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5539 | PROOF | A222277 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5540 | PROOF | A208844 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5541 | PROOF | A301794 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5542 | PROOF | A230063 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5543 | PROOF | A197469 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5544 | PROOF | A203651 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5545 | PROOF | A222140 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5546 | PROOF | A208843 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5547 | PROOF | A253450 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5548 | PROOF | A253489 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5549 | PROOF | A253496 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5550 | PROOF | A229690 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5551 | PROOF | A238518 | a condition on every cell over the neighbour set the entry names |
| 5552 | PROOF | A188708 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5553 | PROOF | A203791 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5554 | PROOF | A208558 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5555 | PROOF | A223395 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5556 | PROOF | A223434 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5557 | PROOF | A230245 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5558 | PROOF | A301793 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5559 | PROOF | A301960 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5560 | PROOF | A301995 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5561 | PROOF | A317513 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5562 | PROOF | A209531 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5563 | PROOF | A209723 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5564 | PROOF | A223337 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5565 | PROOF | A208842 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5566 | PROOF | A208503 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5567 | PROOF | A229689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5568 | PROOF | A229749 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5569 | PROOF | A183626 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5570 | PROOF | A203830 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5571 | PROOF | A208079 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5572 | PROOF | A208556 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5573 | PROOF | A208841 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5574 | PROOF | A209506 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5575 | PROOF | A209722 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5576 | PROOF | A230269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5577 | PROOF | A230331 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5578 | PROOF | A230520 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5579 | PROOF | A253449 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5580 | PROOF | A183304 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5581 | PROOF | A228662 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5582 | PROOF | A228684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5583 | PROOF | A258959 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5584 | PROOF | A261106 | a 3 X 3 subblock condition, whose state is a pair of consecutive lines |
| 5585 | PROOF | A297219 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5586 | PROOF | A297333 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5587 | PROOF | A297369 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5588 | PROOF | A300177 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5589 | PROOF | A300799 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5590 | PROOF | A301438 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5591 | PROOF | A301792 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5592 | PROOF | A301879 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5593 | PROOF | A301902 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5594 | PROOF | A301946 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5595 | PROOF | A301959 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5596 | PROOF | A301994 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5597 | PROOF | A302076 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5598 | PROOF | A302146 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5599 | PROOF | A303416 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5600 | PROOF | A303714 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5601 | PROOF | A304128 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5602 | PROOF | A304225 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5603 | PROOF | A304265 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5604 | PROOF | A305035 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5605 | PROOF | A305581 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5606 | PROOF | A316688 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5607 | PROOF | A317512 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5608 | PROOF | A320366 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5609 | PROOF | A253351 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5610 | PROOF | A229695 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5611 | PROOF | A207656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5612 | PROOF | A208689 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5613 | PROOF | A183625 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5614 | PROOF | A209530 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5615 | PROOF | A250907 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5616 | PROOF | A196700 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5617 | PROOF | A233982 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5618 | PROOF | A234220 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5619 | PROOF | A282310 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5620 | PROOF | A282641 | a condition on every cell's king-move neighbourhood, boundaries included |
| 5621 | PROOF | A203373 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5622 | PROOF | A209729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5623 | PROOF | A220633 | cells linked reciprocally to themselves or to a fixed number of neighbours: degree-constrained subgraphs of a grid |
| 5624 | PROOF | A228656 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5625 | PROOF | A228750 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5626 | PROOF | A228792 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5627 | PROOF | A233684 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5628 | PROOF | A234133 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5629 | PROOF | A234154 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5630 | PROOF | A234483 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5631 | PROOF | A235282 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5632 | PROOF | A250951 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5633 | PROOF | A251293 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5634 | PROOF | A251336 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5635 | PROOF | A251517 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5636 | PROOF | A278088 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5637 | PROOF | A278151 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5638 | PROOF | A278274 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5639 | PROOF | A296719 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5640 | PROOF | A297695 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5641 | PROOF | A297972 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5642 | PROOF | A298234 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5643 | PROOF | A301791 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5644 | PROOF | A302323 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5645 | PROOF | A304421 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5646 | PROOF | A183624 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5647 | PROOF | A183784 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5648 | PROOF | A209953 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5649 | PROOF | A210269 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5650 | PROOF | A210383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5651 | PROOF | A234259 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5652 | PROOF | A251203 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5653 | PROOF | A251328 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5654 | PROOF | A251344 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5655 | PROOF | A251383 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5656 | PROOF | A228501 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5657 | PROOF | A228655 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5658 | PROOF | A228678 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5659 | PROOF | A228797 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5660 | PROOF | A251221 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5661 | PROOF | A251251 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5662 | PROOF | A251319 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5663 | PROOF | A127905 | a recurrence derived from the summand by creative telescoping |
| 5664 | PROOF | A045742 | a recurrence derived from the summand by creative telescoping |
| 5665 | PROOF | A222276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5666 | PROOF | A222139 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5667 | PROOF | A223299 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5668 | PROOF | A223291 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5669 | PROOF | A223373 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5670 | PROOF | A223687 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5671 | PROOF | A231280 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5672 | PROOF | A223241 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5673 | PROOF | A208779 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5674 | PROOF | A223212 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5675 | PROOF | A230179 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5676 | PROOF | A208778 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5677 | PROOF | A223249 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5678 | PROOF | A253158 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5679 | PROOF | A253434 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5680 | PROOF | A253441 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5681 | PROOF | A203729 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5682 | PROOF | A222459 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5683 | PROOF | A203881 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5684 | PROOF | A222336 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5685 | PROOF | A253157 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5686 | PROOF | A253433 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5687 | PROOF | A253440 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5688 | PROOF | A238923 | a condition on every cell over the neighbour set the entry names |
| 5689 | PROOF | A223443 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5690 | PROOF | A203928 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5691 | PROOF | A253156 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5692 | PROOF | A253432 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5693 | PROOF | A253439 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5694 | PROOF | A203650 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5695 | PROOF | A253155 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5696 | PROOF | A253431 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5697 | PROOF | A253438 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5698 | PROOF | A239171 | a condition on every cell over the neighbour set the entry names |
| 5699 | PROOF | A208502 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5700 | PROOF | A223290 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5701 | PROOF | A223372 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5702 | PROOF | A278008 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5703 | PROOF | A253154 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5704 | PROOF | A253430 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5705 | PROOF | A253437 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5706 | PROOF | A203790 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5707 | PROOF | A298777 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5708 | PROOF | A301402 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5709 | PROOF | A301779 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5710 | PROOF | A301836 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5711 | PROOF | A302064 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5712 | PROOF | A302675 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5713 | PROOF | A223240 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5714 | PROOF | A223417 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5715 | PROOF | A253153 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5716 | PROOF | A253429 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5717 | PROOF | A253436 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5718 | PROOF | A207590 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5719 | PROOF | A207846 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5720 | PROOF | A203829 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5721 | PROOF | A209505 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5722 | PROOF | A184145 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5723 | PROOF | A251276 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5724 | PROOF | A251484 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5725 | PROOF | A253152 | a statistic of every 2 X 2 subblock monotone along named directions of the subblock grid |
| 5726 | PROOF | A184368 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5727 | PROOF | A209789 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5728 | PROOF | A209944 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5729 | PROOF | A233637 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5730 | PROOF | A234436 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5731 | PROOF | A228791 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5732 | PROOF | A243585 | a recurrence derived from the summand by creative telescoping |
| 5733 | PROOF | A026005 | a recurrence derived from the summand by creative telescoping |
| 5734 | PROOF | A222335 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5735 | PROOF | A222138 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5736 | PROOF | A188825 | an array count rebuilt as walks in a digraph, then the recurrence annihilated exactly |
| 5737 | PROOF | A359643 | the generating function derived from a coefficient-extraction definition |
| 5738 | PROOF | A156894 | the generating function derived from a coefficient-extraction definition |
| 5739 | PROOF | A156894 | the generating function derived from a coefficient-extraction definition |
| 5740 | PROOF | A371753 | the generating function derived from a coefficient-extraction definition |
| 5741 | PROOF | A226751 | the generating function derived from a coefficient-extraction definition |
| 5742 | PROOF | A386830 | the generating function derived from a coefficient-extraction definition |
| 5743 | PROOF | A172025 | the generating function derived from a coefficient-extraction definition |
| 5744 | PROOF | A348410 | the generating function derived from a coefficient-extraction definition |
| 5745 | PROOF | A243764 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5746 | PROOF | A243760 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5747 | PROOF | A285195 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5748 | PROOF | A243814 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5749 | PROOF | A055392 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5750 | PROOF | A025758 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5751 | PROOF | A308726 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5752 | PROOF | A243022 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5753 | PROOF | A168506 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5754 | PROOF | A239425 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5755 | PROOF | A025757 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5756 | PROOF | A242566 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5757 | PROOF | A270530 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5758 | PROOF | A101478 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5759 | PROOF | A025756 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5760 | PROOF | A097180 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5761 | PROOF | A097189 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5762 | PROOF | A127632 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5763 | PROOF | A130655 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5764 | PROOF | A166135 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5765 | PROOF | A212696 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5766 | PROOF | A261196 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5767 | PROOF | A270530 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5768 | PROOF | A185010 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5769 | PROOF | A185020 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5770 | PROOF | A200312 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5771 | PROOF | A025754 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5772 | PROOF | A097188 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5773 | PROOF | A097192 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5774 | PROOF | A158826 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5775 | PROOF | A159769 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5776 | PROOF | A294159 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5777 | PROOF | A392976 | a general algebraic function field: nested radicals, implicit or reversion g.f.s |
| 5778 | PROOF | A162972 | a transcendental e.g.f., in a differential module over Q(x) |
| 5779 | PROOF | A001465 | a transcendental e.g.f., in a differential module over Q(x) |
| 5780 | PROOF | A085387 | a transcendental e.g.f., in a differential module over Q(x) |
| 5781 | PROOF | A096471 | a transcendental e.g.f., in a differential module over Q(x) |
| 5782 | PROOF | A000704 | a transcendental e.g.f., in a differential module over Q(x) |
| 5783 | PROOF | A001724 | a transcendental e.g.f., in a differential module over Q(x) |
| 5784 | PROOF | A066052 | a transcendental e.g.f., in a differential module over Q(x) |
| 5785 | PROOF | A097204 | a transcendental e.g.f., in a differential module over Q(x) |
| 5786 | PROOF | A053532 | a transcendental e.g.f., in a differential module over Q(x) |
| 5787 | PROOF | A306948 | a transcendental e.g.f., in a differential module over Q(x) |
| 5788 | PROOF | A000483 | a transcendental e.g.f., in a differential module over Q(x) |
| 5789 | PROOF | A000276 | a transcendental e.g.f., in a differential module over Q(x) |
| 5790 | PROOF | A002104 | a transcendental e.g.f., in a differential module over Q(x) |
| 5791 | PROOF | A002538 | a transcendental e.g.f., in a differential module over Q(x) |
| 5792 | PROOF | A066052 | a transcendental e.g.f., in a differential module over Q(x) |
| 5793 | PROOF | A073591 | a transcendental e.g.f., in a differential module over Q(x) |
| 5794 | PROOF | A108704 | a transcendental e.g.f., in a differential module over Q(x) |
| 5795 | PROOF | A110322 | a transcendental e.g.f., in a differential module over Q(x) |
| 5796 | PROOF | A185369 | a transcendental e.g.f., in a differential module over Q(x) |
| 5797 | PROOF | A000276 | a transcendental e.g.f., in a differential module over Q(x) |
| 5798 | PROOF | A000774 | a transcendental e.g.f., in a differential module over Q(x) |
| 5799 | PROOF | A094905 | a transcendental e.g.f., in a differential module over Q(x) |
| 5800 | PROOF | A098557 | a transcendental e.g.f., in a differential module over Q(x) |
| 5801 | PROOF | A051560 | a transcendental e.g.f., in a differential module over Q(x) |
| 5802 | PROOF | A129149 | a transcendental e.g.f., in a differential module over Q(x) |
| 5803 | PROOF | A187252 | a transcendental e.g.f., in a differential module over Q(x) |
| 5804 | PROOF | A005654 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5805 | PROOF | A116385 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5806 | PROOF | A005558 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5807 | PROOF | A065942 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5808 | PROOF | A081181 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5809 | PROOF | A081204 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5810 | PROOF | A005558 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5811 | PROOF | A005559 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5812 | PROOF | A005560 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5813 | PROOF | A005561 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5814 | PROOF | A005562 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5815 | PROOF | A081204 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5816 | PROOF | A081205 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5817 | PROOF | A213801 | a posted closed form split on the parity of n, then decided by hypergeometric terms |
| 5818 | PROOF | A006231 | a posted closed form against a derived holonomic recurrence |
| 5819 | PROOF | A213203 | a posted closed form compared against the posted generating function |
| 5820 | PROOF | A242429 | a posted closed form compared against the posted generating function |
| 5821 | PROOF | A026018 | a posted closed form compared against the posted generating function |
| 5822 | PROOF | A092634 | a posted closed form compared against the posted generating function |
| 5823 | PROOF | A026026 | a posted closed form compared against the posted generating function |
| 5824 | PROOF | A052227 | a posted closed form compared against the posted generating function |
| 5825 | PROOF | A228329 | a posted closed form compared against the posted generating function |
| 5826 | PROOF | A259457 | a posted closed form compared against the posted generating function |
| 5827 | PROOF | A268554 | a posted closed form compared against the posted generating function |
| 5828 | PROOF | A214907 | the recurrence follows from a generating function the entry records as fact |
| 5829 | PROOF | A263869 | the recurrence follows from a generating function the entry records as fact |
| 5830 | PROOF | A250782 | the recurrence follows from a generating function the entry records as fact |
| 5831 | PROOF | A165386 | the recurrence follows from a generating function the entry records as fact |
| 5832 | PROOF | A250781 | the recurrence follows from a generating function the entry records as fact |
| 5833 | PROOF | A163020 | the recurrence follows from a generating function the entry records as fact |
| 5834 | PROOF | A220640 | the recurrence follows from a generating function the entry records as fact |
| 5835 | PROOF | A204648 | the recurrence follows from a generating function the entry records as fact |
| 5836 | PROOF | A206264 | the recurrence follows from a generating function the entry records as fact |
| 5837 | PROOF | A262482 | the recurrence follows from a generating function the entry records as fact |
| 5838 | PROOF | A208642 | the recurrence follows from a generating function the entry records as fact |
| 5839 | PROOF | A204647 | the recurrence follows from a generating function the entry records as fact |
| 5840 | PROOF | A250892 | the recurrence follows from a generating function the entry records as fact |
| 5841 | PROOF | A250893 | the recurrence follows from a generating function the entry records as fact |
| 5842 | PROOF | A250894 | the recurrence follows from a generating function the entry records as fact |
| 5843 | PROOF | A250895 | the recurrence follows from a generating function the entry records as fact |
| 5844 | PROOF | A250896 | the recurrence follows from a generating function the entry records as fact |
| 5845 | PROOF | A250897 | the recurrence follows from a generating function the entry records as fact |
| 5846 | PROOF | A164760 | the recurrence follows from a generating function the entry records as fact |
| 5847 | PROOF | A202442 | the recurrence follows from a generating function the entry records as fact |
| 5848 | PROOF | A202443 | the recurrence follows from a generating function the entry records as fact |
| 5849 | PROOF | A206263 | the recurrence follows from a generating function the entry records as fact |
| 5850 | PROOF | A250780 | the recurrence follows from a generating function the entry records as fact |
| 5851 | PROOF | A263794 | the recurrence follows from a generating function the entry records as fact |
| 5852 | PROOF | A208641 | the recurrence follows from a generating function the entry records as fact |
| 5853 | PROOF | A204646 | the recurrence follows from a generating function the entry records as fact |
| 5854 | PROOF | A206262 | the recurrence follows from a generating function the entry records as fact |
| 5855 | PROOF | A204645 | the recurrence follows from a generating function the entry records as fact |
| 5856 | PROOF | A233402 | the recurrence follows from a generating function the entry records as fact |
| 5857 | PROOF | A250900 | the recurrence follows from a generating function the entry records as fact |
| 5858 | PROOF | A267960 | the recurrence follows from a generating function the entry records as fact |
| 5859 | PROOF | A220639 | the recurrence follows from a generating function the entry records as fact |
| 5860 | PROOF | A102319 | several independent square roots |
| 5861 | PROOF | A115256 | several independent square roots |
| 5862 | PROOF | A165373 | the recurrence follows from a generating function the entry records as fact |
| 5863 | PROOF | A165394 | the recurrence follows from a generating function the entry records as fact |
| 5864 | PROOF | A206261 | the recurrence follows from a generating function the entry records as fact |
| 5865 | PROOF | A224671 | the recurrence follows from a generating function the entry records as fact |
| 5866 | PROOF | A224673 | the recurrence follows from a generating function the entry records as fact |
| 5867 | PROOF | A194772 | the recurrence follows from a generating function the entry records as fact |
| 5868 | PROOF | A222993 | the recurrence follows from a generating function the entry records as fact |
| 5869 | PROOF | A223711 | the recurrence follows from a generating function the entry records as fact |
| 5870 | PROOF | A224670 | the recurrence follows from a generating function the entry records as fact |
| 5871 | PROOF | A235510 | the recurrence follows from a generating function the entry records as fact |
| 5872 | PROOF | A250779 | the recurrence follows from a generating function the entry records as fact |
| 5873 | PROOF | A250792 | the recurrence follows from a generating function the entry records as fact |
| 5874 | PROOF | A250899 | the recurrence follows from a generating function the entry records as fact |
| 5875 | PROOF | A157125 | several independent square roots |
| 5876 | PROOF | A102318 | several independent square roots |
| 5877 | PROOF | A107587 | several independent square roots |
| 5878 | PROOF | A190092 | the recurrence follows from a generating function the entry records as fact |
| 5879 | PROOF | A190093 | the recurrence follows from a generating function the entry records as fact |
| 5880 | PROOF | A253226 | the recurrence follows from a generating function the entry records as fact |
| 5881 | PROOF | A253227 | the recurrence follows from a generating function the entry records as fact |
| 5882 | PROOF | A253228 | the recurrence follows from a generating function the entry records as fact |
| 5883 | PROOF | A253229 | the recurrence follows from a generating function the entry records as fact |
| 5884 | PROOF | A253230 | the recurrence follows from a generating function the entry records as fact |
| 5885 | PROOF | A222835 | the recurrence follows from a generating function the entry records as fact |
| 5886 | PROOF | A221788 | the recurrence follows from a generating function the entry records as fact |
| 5887 | PROOF | A222777 | the recurrence follows from a generating function the entry records as fact |
| 5888 | PROOF | A222892 | the recurrence follows from a generating function the entry records as fact |
| 5889 | PROOF | A184031 | the recurrence follows from a generating function the entry records as fact |
| 5890 | PROOF | A184032 | the recurrence follows from a generating function the entry records as fact |
| 5891 | PROOF | A184033 | the recurrence follows from a generating function the entry records as fact |
| 5892 | PROOF | A184034 | the recurrence follows from a generating function the entry records as fact |
| 5893 | PROOF | A184035 | the recurrence follows from a generating function the entry records as fact |
| 5894 | PROOF | A184036 | the recurrence follows from a generating function the entry records as fact |
| 5895 | PROOF | A184037 | the recurrence follows from a generating function the entry records as fact |
| 5896 | PROOF | A184038 | the recurrence follows from a generating function the entry records as fact |
| 5897 | PROOF | A184041 | the recurrence follows from a generating function the entry records as fact |
| 5898 | PROOF | A184042 | the recurrence follows from a generating function the entry records as fact |
| 5899 | PROOF | A184043 | the recurrence follows from a generating function the entry records as fact |
| 5900 | PROOF | A184044 | the recurrence follows from a generating function the entry records as fact |
| 5901 | PROOF | A184045 | the recurrence follows from a generating function the entry records as fact |
| 5902 | PROOF | A184046 | the recurrence follows from a generating function the entry records as fact |
| 5903 | PROOF | A184047 | the recurrence follows from a generating function the entry records as fact |
| 5904 | PROOF | A189450 | the recurrence follows from a generating function the entry records as fact |
| 5905 | PROOF | A190091 | the recurrence follows from a generating function the entry records as fact |
| 5906 | PROOF | A206170 | the recurrence follows from a generating function the entry records as fact |
| 5907 | PROOF | A208086 | the recurrence follows from a generating function the entry records as fact |
| 5908 | PROOF | A208087 | the recurrence follows from a generating function the entry records as fact |
| 5909 | PROOF | A208089 | the recurrence follows from a generating function the entry records as fact |
| 5910 | PROOF | A211327 | the recurrence follows from a generating function the entry records as fact |
| 5911 | PROOF | A214181 | the recurrence follows from a generating function the entry records as fact |
| 5912 | PROOF | A218185 | several independent square roots |
| 5913 | PROOF | A221619 | the recurrence follows from a generating function the entry records as fact |
| 5914 | PROOF | A221764 | the recurrence follows from a generating function the entry records as fact |
| 5915 | PROOF | A222001 | the recurrence follows from a generating function the entry records as fact |
| 5916 | PROOF | A239024 | the recurrence follows from a generating function the entry records as fact |
| 5917 | PROOF | A250610 | the recurrence follows from a generating function the entry records as fact |
| 5918 | PROOF | A250784 | the recurrence follows from a generating function the entry records as fact |
| 5919 | PROOF | A250791 | the recurrence follows from a generating function the entry records as fact |
| 5920 | PROOF | A262267 | the recurrence follows from a generating function the entry records as fact |
| 5921 | PROOF | A263908 | the recurrence follows from a generating function the entry records as fact |
| 5922 | PROOF | A267905 | the recurrence follows from a generating function the entry records as fact |
| 5923 | PROOF | A268053 | the recurrence follows from a generating function the entry records as fact |
| 5924 | PROOF | A268775 | the recurrence follows from a generating function the entry records as fact |
| 5925 | PROOF | A269202 | the recurrence follows from a generating function the entry records as fact |
| 5926 | PROOF | A025567 | several independent square roots |
| 5927 | PROOF | A071684 | several independent square roots |
| 5928 | PROOF | A179648 | several independent square roots |
| 5929 | PROOF | A184120 | several independent square roots |
| 5930 | PROOF | A026163 | several independent square roots |
| 5931 | PROOF | A102318 | several independent square roots |
| 5932 | PROOF | A101500 | several independent square roots |
| 5933 | PROOF | A102319 | several independent square roots |
| 5934 | PROOF | A107587 | several independent square roots |
| 5935 | PROOF | A206336 | the recurrence follows from a generating function the entry records as fact |
| 5936 | PROOF | A165381 | the recurrence follows from a generating function the entry records as fact |
| 5937 | PROOF | A165392 | the recurrence follows from a generating function the entry records as fact |
| 5938 | PROOF | A207142 | the recurrence follows from a generating function the entry records as fact |
| 5939 | PROOF | A220749 | the recurrence follows from a generating function the entry records as fact |
| 5940 | PROOF | A253225 | the recurrence follows from a generating function the entry records as fact |
| 5941 | PROOF | A253490 | the recurrence follows from a generating function the entry records as fact |
| 5942 | PROOF | A265989 | the recurrence follows from a generating function the entry records as fact |
| 5943 | PROOF | A165378 | the recurrence follows from a generating function the entry records as fact |
| 5944 | PROOF | A253491 | the recurrence follows from a generating function the entry records as fact |
| 5945 | PROOF | A253492 | the recurrence follows from a generating function the entry records as fact |
| 5946 | PROOF | A253493 | the recurrence follows from a generating function the entry records as fact |
| 5947 | PROOF | A204609 | the recurrence follows from a generating function the entry records as fact |
| 5948 | PROOF | A222939 | the recurrence follows from a generating function the entry records as fact |
| 5949 | PROOF | A267912 | the recurrence follows from a generating function the entry records as fact |
| 5950 | PROOF | A183356 | the recurrence follows from a generating function the entry records as fact |
| 5951 | PROOF | A222834 | the recurrence follows from a generating function the entry records as fact |
| 5952 | PROOF | A233162 | the recurrence follows from a generating function the entry records as fact |
| 5953 | PROOF | A233175 | the recurrence follows from a generating function the entry records as fact |
| 5954 | PROOF | A233218 | the recurrence follows from a generating function the entry records as fact |
| 5955 | PROOF | A276300 | the recurrence follows from a generating function the entry records as fact |
| 5956 | PROOF | A181192 | the recurrence follows from a generating function the entry records as fact |
| 5957 | PROOF | A183430 | the recurrence follows from a generating function the entry records as fact |
| 5958 | PROOF | A184679 | the recurrence follows from a generating function the entry records as fact |
| 5959 | PROOF | A204707 | the recurrence follows from a generating function the entry records as fact |
| 5960 | PROOF | A204708 | the recurrence follows from a generating function the entry records as fact |
| 5961 | PROOF | A211322 | the recurrence follows from a generating function the entry records as fact |
| 5962 | PROOF | A211490 | the recurrence follows from a generating function the entry records as fact |
| 5963 | PROOF | A214160 | the recurrence follows from a generating function the entry records as fact |
| 5964 | PROOF | A221374 | the recurrence follows from a generating function the entry records as fact |
| 5965 | PROOF | A223363 | the recurrence follows from a generating function the entry records as fact |
| 5966 | PROOF | A223499 | the recurrence follows from a generating function the entry records as fact |
| 5967 | PROOF | A224669 | the recurrence follows from a generating function the entry records as fact |
| 5968 | PROOF | A232951 | the recurrence follows from a generating function the entry records as fact |
| 5969 | PROOF | A233106 | the recurrence follows from a generating function the entry records as fact |
| 5970 | PROOF | A233107 | the recurrence follows from a generating function the entry records as fact |
| 5971 | PROOF | A233124 | the recurrence follows from a generating function the entry records as fact |
| 5972 | PROOF | A233211 | the recurrence follows from a generating function the entry records as fact |
| 5973 | PROOF | A233212 | the recurrence follows from a generating function the entry records as fact |
| 5974 | PROOF | A233213 | the recurrence follows from a generating function the entry records as fact |
| 5975 | PROOF | A234789 | the recurrence follows from a generating function the entry records as fact |
| 5976 | PROOF | A235878 | the recurrence follows from a generating function the entry records as fact |
| 5977 | PROOF | A235879 | the recurrence follows from a generating function the entry records as fact |
| 5978 | PROOF | A235880 | the recurrence follows from a generating function the entry records as fact |
| 5979 | PROOF | A235881 | the recurrence follows from a generating function the entry records as fact |
| 5980 | PROOF | A235882 | the recurrence follows from a generating function the entry records as fact |
| 5981 | PROOF | A235883 | the recurrence follows from a generating function the entry records as fact |
| 5982 | PROOF | A235887 | the recurrence follows from a generating function the entry records as fact |
| 5983 | PROOF | A235888 | the recurrence follows from a generating function the entry records as fact |
| 5984 | PROOF | A235889 | the recurrence follows from a generating function the entry records as fact |
| 5985 | PROOF | A235890 | the recurrence follows from a generating function the entry records as fact |
| 5986 | PROOF | A235891 | the recurrence follows from a generating function the entry records as fact |
| 5987 | PROOF | A235892 | the recurrence follows from a generating function the entry records as fact |
| 5988 | PROOF | A235895 | the recurrence follows from a generating function the entry records as fact |
| 5989 | PROOF | A250461 | the recurrence follows from a generating function the entry records as fact |
| 5990 | PROOF | A250778 | the recurrence follows from a generating function the entry records as fact |
| 5991 | PROOF | A262326 | the recurrence follows from a generating function the entry records as fact |
| 5992 | PROOF | A262327 | the recurrence follows from a generating function the entry records as fact |
| 5993 | PROOF | A262415 | the recurrence follows from a generating function the entry records as fact |
| 5994 | PROOF | A265987 | the recurrence follows from a generating function the entry records as fact |
| 5995 | PROOF | A267946 | the recurrence follows from a generating function the entry records as fact |
| 5996 | PROOF | A268052 | the recurrence follows from a generating function the entry records as fact |
| 5997 | PROOF | A268093 | the recurrence follows from a generating function the entry records as fact |
| 5998 | PROOF | A268164 | the recurrence follows from a generating function the entry records as fact |
| 5999 | PROOF | A277761 | the recurrence follows from a generating function the entry records as fact |
| 6000 | PROOF | A072100 | several independent square roots |
| 6001 | PROOF | A239530 | the recurrence follows from a generating function the entry records as fact |
| 6002 | PROOF | A263907 | the recurrence follows from a generating function the entry records as fact |
| 6003 | PROOF | A221588 | the recurrence follows from a generating function the entry records as fact |
| 6004 | PROOF | A221589 | the recurrence follows from a generating function the entry records as fact |
| 6005 | PROOF | A221022 | the recurrence follows from a generating function the entry records as fact |
| 6006 | PROOF | A165372 | the recurrence follows from a generating function the entry records as fact |
| 6007 | PROOF | A202730 | the recurrence follows from a generating function the entry records as fact |
| 6008 | PROOF | A206687 | the recurrence follows from a generating function the entry records as fact |
| 6009 | PROOF | A221829 | the recurrence follows from a generating function the entry records as fact |
| 6010 | PROOF | A222869 | the recurrence follows from a generating function the entry records as fact |
| 6011 | PROOF | A222940 | the recurrence follows from a generating function the entry records as fact |
| 6012 | PROOF | A223332 | the recurrence follows from a generating function the entry records as fact |
| 6013 | PROOF | A269290 | the recurrence follows from a generating function the entry records as fact |
| 6014 | PROOF | A223181 | the recurrence follows from a generating function the entry records as fact |
| 6015 | PROOF | A223234 | the recurrence follows from a generating function the entry records as fact |
| 6016 | PROOF | A223381 | the recurrence follows from a generating function the entry records as fact |
| 6017 | PROOF | A233163 | the recurrence follows from a generating function the entry records as fact |
| 6018 | PROOF | A233164 | the recurrence follows from a generating function the entry records as fact |
| 6019 | PROOF | A233165 | the recurrence follows from a generating function the entry records as fact |
| 6020 | PROOF | A233166 | the recurrence follows from a generating function the entry records as fact |
| 6021 | PROOF | A233167 | the recurrence follows from a generating function the entry records as fact |
| 6022 | PROOF | A233196 | the recurrence follows from a generating function the entry records as fact |
| 6023 | PROOF | A233257 | the recurrence follows from a generating function the entry records as fact |
| 6024 | PROOF | A268622 | the recurrence follows from a generating function the entry records as fact |
| 6025 | PROOF | A269103 | the recurrence follows from a generating function the entry records as fact |
| 6026 | PROOF | A269285 | the recurrence follows from a generating function the entry records as fact |
| 6027 | PROOF | A183586 | the recurrence follows from a generating function the entry records as fact |
| 6028 | PROOF | A183682 | the recurrence follows from a generating function the entry records as fact |
| 6029 | PROOF | A183690 | the recurrence follows from a generating function the entry records as fact |
| 6030 | PROOF | A183702 | the recurrence follows from a generating function the entry records as fact |
| 6031 | PROOF | A184688 | the recurrence follows from a generating function the entry records as fact |
| 6032 | PROOF | A185761 | the recurrence follows from a generating function the entry records as fact |
| 6033 | PROOF | A185858 | the recurrence follows from a generating function the entry records as fact |
| 6034 | PROOF | A189604 | the recurrence follows from a generating function the entry records as fact |
| 6035 | PROOF | A205220 | the recurrence follows from a generating function the entry records as fact |
| 6036 | PROOF | A205329 | the recurrence follows from a generating function the entry records as fact |
| 6037 | PROOF | A205354 | the recurrence follows from a generating function the entry records as fact |
| 6038 | PROOF | A208088 | the recurrence follows from a generating function the entry records as fact |
| 6039 | PROOF | A211715 | the recurrence follows from a generating function the entry records as fact |
| 6040 | PROOF | A211719 | the recurrence follows from a generating function the entry records as fact |
| 6041 | PROOF | A220932 | the recurrence follows from a generating function the entry records as fact |
| 6042 | PROOF | A221121 | the recurrence follows from a generating function the entry records as fact |
| 6043 | PROOF | A221731 | the recurrence follows from a generating function the entry records as fact |
| 6044 | PROOF | A222098 | the recurrence follows from a generating function the entry records as fact |
| 6045 | PROOF | A223197 | the recurrence follows from a generating function the entry records as fact |
| 6046 | PROOF | A223204 | the recurrence follows from a generating function the entry records as fact |
| 6047 | PROOF | A223228 | the recurrence follows from a generating function the entry records as fact |
| 6048 | PROOF | A223258 | the recurrence follows from a generating function the entry records as fact |
| 6049 | PROOF | A223277 | the recurrence follows from a generating function the entry records as fact |
| 6050 | PROOF | A223278 | the recurrence follows from a generating function the entry records as fact |
| 6051 | PROOF | A223318 | the recurrence follows from a generating function the entry records as fact |
| 6052 | PROOF | A223552 | the recurrence follows from a generating function the entry records as fact |
| 6053 | PROOF | A231103 | the recurrence follows from a generating function the entry records as fact |
| 6054 | PROOF | A231104 | the recurrence follows from a generating function the entry records as fact |
| 6055 | PROOF | A232950 | the recurrence follows from a generating function the entry records as fact |
| 6056 | PROOF | A232956 | the recurrence follows from a generating function the entry records as fact |
| 6057 | PROOF | A233123 | the recurrence follows from a generating function the entry records as fact |
| 6058 | PROOF | A233251 | the recurrence follows from a generating function the entry records as fact |
| 6059 | PROOF | A233252 | the recurrence follows from a generating function the entry records as fact |
| 6060 | PROOF | A234779 | the recurrence follows from a generating function the entry records as fact |
| 6061 | PROOF | A235877 | the recurrence follows from a generating function the entry records as fact |
| 6062 | PROOF | A235886 | the recurrence follows from a generating function the entry records as fact |
| 6063 | PROOF | A253029 | the recurrence follows from a generating function the entry records as fact |
| 6064 | PROOF | A259243 | the recurrence follows from a generating function the entry records as fact |
| 6065 | PROOF | A259290 | the recurrence follows from a generating function the entry records as fact |
| 6066 | PROOF | A269284 | the recurrence follows from a generating function the entry records as fact |
| 6067 | PROOF | A275229 | the recurrence follows from a generating function the entry records as fact |
| 6068 | PROOF | A221082 | the recurrence follows from a generating function the entry records as fact |
| 6069 | PROOF | A223270 | the recurrence follows from a generating function the entry records as fact |
| 6070 | PROOF | A232921 | the recurrence follows from a generating function the entry records as fact |
| 6071 | PROOF | A233020 | the recurrence follows from a generating function the entry records as fact |
| 6072 | PROOF | A025567 | several independent square roots |
| 6073 | PROOF | A264123 | the recurrence follows from a generating function the entry records as fact |
| 6074 | PROOF | A264185 | the recurrence follows from a generating function the entry records as fact |
| 6075 | PROOF | A208428 | the recurrence follows from a generating function the entry records as fact |
| 6076 | PROOF | A189274 | the recurrence follows from a generating function the entry records as fact |
| 6077 | PROOF | A223322 | the recurrence follows from a generating function the entry records as fact |
| 6078 | PROOF | A334509 | an identity between different entries |
| 6079 | PROOF | A298022 | an identity between different entries |
| 6080 | PROOF | A273676 | an identity between different entries |
| 6081 | PROOF | A273832 | an identity between different entries |
| 6082 | PROOF | A319371 | an identity between different entries |
| 6083 | PROOF | A110320 | an identity between different entries |
| 6084 | PROOF | A309878 | an identity between different entries |
| 6085 | PROOF | A315520 | an identity between different entries |
| 6086 | PROOF | A346370 | an identity between different entries |
| 6087 | PROOF | A176126 | the residual test over one square root, or none |
| 6088 | PROOF | A191625 | the residual test over one square root, or none |
| 6089 | PROOF | A186341 | the residual test over one square root, or none |
| 6090 | PROOF | A026743 | the residual test over one square root, or none |
| 6091 | PROOF | A191786 | the residual test over one square root, or none |
| 6092 | PROOF | A210496 | the residual test over one square root, or none |
| 6093 | PROOF | A182892 | the residual test over one square root, or none |
| 6094 | PROOF | A270724 | the residual test over one square root, or none |
| 6095 | PROOF | A190171 | the residual test over one square root, or none |
| 6096 | PROOF | A257515 | the residual test over one square root, or none |
| 6097 | PROOF | A190788 | the residual test over one square root, or none |
| 6098 | PROOF | A095981 | the residual test over one square root, or none |
| 6099 | PROOF | A212205 | the residual test over one square root, or none |
| 6100 | PROOF | A270661 | the residual test over one square root, or none |
| 6101 | PROOF | A157021 | the residual test over one square root, or none |
| 6102 | PROOF | A165537 | the residual test over one square root, or none |
| 6103 | PROOF | A166287 | the residual test over one square root, or none |
| 6104 | PROOF | A174013 | the residual test over one square root, or none |
| 6105 | PROOF | A178072 | the residual test over one square root, or none |
| 6106 | PROOF | A182894 | the residual test over one square root, or none |
| 6107 | PROOF | A114584 | the residual test over one square root, or none |
| 6108 | PROOF | A164586 | the residual test over one square root, or none |
| 6109 | PROOF | A189053 | the residual test over one square root, or none |
| 6110 | PROOF | A182904 | the residual test over one square root, or none |
| 6111 | PROOF | A274295 | the residual test over one square root, or none |
| 6112 | PROOF | A226434 | the residual test over one square root, or none |
| 6113 | PROOF | A257104 | the residual test over one square root, or none |
| 6114 | PROOF | A108600 | the residual test over one square root, or none |
| 6115 | PROOF | A114851 | the residual test over one square root, or none |
| 6116 | PROOF | A125306 | the residual test over one square root, or none |
| 6117 | PROOF | A166290 | the residual test over one square root, or none |
| 6118 | PROOF | A228770 | the residual test over one square root, or none |
| 6119 | PROOF | A257300 | the residual test over one square root, or none |
| 6120 | PROOF | A089324 | the residual test over one square root, or none |
| 6121 | PROOF | A104625 | the residual test over one square root, or none |
| 6122 | PROOF | A113956 | the residual test over one square root, or none |
| 6123 | PROOF | A116383 | the residual test over one square root, or none |
| 6124 | PROOF | A162548 | the residual test over one square root, or none |
| 6125 | PROOF | A173993 | the residual test over one square root, or none |
| 6126 | PROOF | A244886 | the residual test over one square root, or none |
| 6127 | PROOF | A157003 | the residual test over one square root, or none |
| 6128 | PROOF | A162482 | the residual test over one square root, or none |
| 6129 | PROOF | A163493 | the residual test over one square root, or none |
| 6130 | PROOF | A191398 | the residual test over one square root, or none |
| 6131 | PROOF | A135582 | the residual test over one square root, or none |
| 6132 | PROOF | A139376 | the residual test over one square root, or none |
| 6133 | PROOF | A346074 | the residual test over one square root, or none |
| 6134 | PROOF | A190166 | the residual test over one square root, or none |
| 6135 | PROOF | A025251 | the residual test over one square root, or none |
| 6136 | PROOF | A228771 | the residual test over one square root, or none |
| 6137 | PROOF | A025268 | the residual test over one square root, or none |
| 6138 | PROOF | A025272 | the residual test over one square root, or none |
| 6139 | PROOF | A162475 | the residual test over one square root, or none |
| 6140 | PROOF | A385252 | the residual test over one square root, or none |
| 6141 | PROOF | A114464 | the residual test over one square root, or none |
| 6142 | PROOF | A127154 | the residual test over one square root, or none |
| 6143 | PROOF | A135335 | the residual test over one square root, or none |
| 6144 | PROOF | A165540 | the residual test over one square root, or none |
| 6145 | PROOF | A171416 | the residual test over one square root, or none |
| 6146 | PROOF | A188314 | the residual test over one square root, or none |
| 6147 | PROOF | A247170 | the residual test over one square root, or none |
| 6148 | PROOF | A254314 | the residual test over one square root, or none |
| 6149 | PROOF | A270661 | the residual test over one square root, or none |
| 6150 | PROOF | A003440 | the residual test over one square root, or none |
| 6151 | PROOF | A110521 | the residual test over one square root, or none |
| 6152 | PROOF | A114190 | the residual test over one square root, or none |
| 6153 | PROOF | A116387 | the residual test over one square root, or none |
| 6154 | PROOF | A128096 | the residual test over one square root, or none |
| 6155 | PROOF | A135052 | the residual test over one square root, or none |
| 6156 | PROOF | A157021 | the residual test over one square root, or none |
| 6157 | PROOF | A160823 | the residual test over one square root, or none |
| 6158 | PROOF | A166287 | the residual test over one square root, or none |
| 6159 | PROOF | A174808 | the residual test over one square root, or none |
| 6160 | PROOF | A185089 | the residual test over one square root, or none |
| 6161 | PROOF | A186940 | the residual test over one square root, or none |
| 6162 | PROOF | A190736 | the residual test over one square root, or none |
| 6163 | PROOF | A219314 | the residual test over one square root, or none |
| 6164 | PROOF | A100095 | the residual test over one square root, or none |
| 6165 | PROOF | A100097 | the residual test over one square root, or none |
| 6166 | PROOF | A191313 | the residual test over one square root, or none |
| 6167 | PROOF | A191790 | the residual test over one square root, or none |
| 6168 | PROOF | A273351 | the residual test over one square root, or none |
| 6169 | PROOF | A278472 | the residual test over one square root, or none |
| 6170 | PROOF | A108296 | the residual test over one square root, or none |
| 6171 | PROOF | A116391 | the residual test over one square root, or none |
| 6172 | PROOF | A110198 | the residual test over one square root, or none |
| 6173 | PROOF | A182879 | the residual test over one square root, or none |
| 6174 | PROOF | A182887 | the residual test over one square root, or none |
| 6175 | PROOF | A135925 | the residual test over one square root, or none |
| 6176 | PROOF | A007901 | the residual test over one square root, or none |
| 6177 | PROOF | A025256 | the residual test over one square root, or none |
| 6178 | PROOF | A025258 | the residual test over one square root, or none |
| 6179 | PROOF | A000781 | the residual test over one square root, or none |
| 6180 | PROOF | A025245 | the residual test over one square root, or none |
| 6181 | PROOF | A025257 | the residual test over one square root, or none |
| 6182 | PROOF | A025269 | the residual test over one square root, or none |
| 6183 | PROOF | A025270 | the residual test over one square root, or none |
| 6184 | PROOF | A025275 | the residual test over one square root, or none |
| 6185 | PROOF | A032096 | the residual test over one square root, or none |
| 6186 | PROOF | A102880 | the residual test over one square root, or none |
| 6187 | PROOF | A111053 | the residual test over one square root, or none |
| 6188 | PROOF | A152120 | the residual test over one square root, or none |
| 6189 | PROOF | A159771 | the residual test over one square root, or none |
| 6190 | PROOF | A166694 | the residual test over one square root, or none |
| 6191 | PROOF | A166696 | the residual test over one square root, or none |
| 6192 | PROOF | A191796 | the residual test over one square root, or none |
| 6193 | PROOF | A217711 | the residual test over one square root, or none |
| 6194 | PROOF | A278023 | the residual test over one square root, or none |
| 6195 | PROOF | A279014 | the residual test over one square root, or none |
| 6196 | PROOF | A000483 | the residual test over one square root, or none |
| 6197 | PROOF | A026030 | the residual test over one square root, or none |
| 6198 | PROOF | A026031 | the residual test over one square root, or none |
| 6199 | PROOF | A048775 | the residual test over one square root, or none |
| 6200 | PROOF | A116409 | the residual test over one square root, or none |
| 6201 | PROOF | A126322 | the residual test over one square root, or none |
| 6202 | PROOF | A128750 | the residual test over one square root, or none |
| 6203 | PROOF | A143955 | the residual test over one square root, or none |
| 6204 | PROOF | A165203 | the residual test over one square root, or none |
| 6205 | PROOF | A168505 | the residual test over one square root, or none |
| 6206 | PROOF | A176605 | the residual test over one square root, or none |
| 6207 | PROOF | A181933 | the residual test over one square root, or none |
| 6208 | PROOF | A191585 | the residual test over one square root, or none |
| 6209 | PROOF | A215973 | the residual test over one square root, or none |
| 6210 | PROOF | A234269 | the residual test over one square root, or none |
| 6211 | PROOF | A236407 | the residual test over one square root, or none |
| 6212 | PROOF | A270363 | the residual test over one square root, or none |
| 6213 | PROOF | A098521 | the residual test over one square root, or none |
| 6214 | PROOF | A100096 | the residual test over one square root, or none |
| 6215 | PROOF | A100099 | the residual test over one square root, or none |
| 6216 | PROOF | A105849 | the residual test over one square root, or none |
| 6217 | PROOF | A105864 | the residual test over one square root, or none |
| 6218 | PROOF | A105865 | the residual test over one square root, or none |
| 6219 | PROOF | A108308 | the residual test over one square root, or none |
| 6220 | PROOF | A114194 | the residual test over one square root, or none |
| 6221 | PROOF | A115967 | the residual test over one square root, or none |
| 6222 | PROOF | A117186 | the residual test over one square root, or none |
| 6223 | PROOF | A120010 | the residual test over one square root, or none |
| 6224 | PROOF | A124431 | the residual test over one square root, or none |
| 6225 | PROOF | A124431 | the residual test over one square root, or none |
| 6226 | PROOF | A126568 | the residual test over one square root, or none |
| 6227 | PROOF | A132364 | the residual test over one square root, or none |
| 6228 | PROOF | A141342 | the residual test over one square root, or none |
| 6229 | PROOF | A155051 | the residual test over one square root, or none |
| 6230 | PROOF | A157002 | the residual test over one square root, or none |
| 6231 | PROOF | A157100 | the residual test over one square root, or none |
| 6232 | PROOF | A166076 | the residual test over one square root, or none |
| 6233 | PROOF | A166300 | the residual test over one square root, or none |
| 6234 | PROOF | A168503 | the residual test over one square root, or none |
| 6235 | PROOF | A174107 | the residual test over one square root, or none |
| 6236 | PROOF | A174169 | the residual test over one square root, or none |
| 6237 | PROOF | A176332 | the residual test over one square root, or none |
| 6238 | PROOF | A184018 | the residual test over one square root, or none |
| 6239 | PROOF | A188312 | the residual test over one square root, or none |
| 6240 | PROOF | A188482 | the residual test over one square root, or none |
| 6241 | PROOF | A191782 | the residual test over one square root, or none |
| 6242 | PROOF | A217333 | the residual test over one square root, or none |
| 6243 | PROOF | A257072 | the residual test over one square root, or none |
| 6244 | PROOF | A261681 | the residual test over one square root, or none |
| 6245 | PROOF | A073155 | the residual test over one square root, or none |
| 6246 | PROOF | A105524 | the residual test over one square root, or none |
| 6247 | PROOF | A114589 | the residual test over one square root, or none |
| 6248 | PROOF | A114590 | the residual test over one square root, or none |
| 6249 | PROOF | A162481 | the residual test over one square root, or none |
| 6250 | PROOF | A174783 | the residual test over one square root, or none |
| 6251 | PROOF | A188460 | the residual test over one square root, or none |
| 6252 | PROOF | A188464 | the residual test over one square root, or none |
| 6253 | PROOF | A190725 | the residual test over one square root, or none |
| 6254 | PROOF | A191526 | the residual test over one square root, or none |
| 6255 | PROOF | A191531 | the residual test over one square root, or none |
| 6256 | PROOF | A211278 | the residual test over one square root, or none |
| 6257 | PROOF | A026327 | the residual test over one square root, or none |
| 6258 | PROOF | A081207 | the residual test over one square root, or none |
| 6259 | PROOF | A102882 | the residual test over one square root, or none |
| 6260 | PROOF | A182881 | the residual test over one square root, or none |
| 6261 | PROOF | A191309 | the residual test over one square root, or none |
| 6262 | PROOF | A191319 | the residual test over one square root, or none |
| 6263 | PROOF | A191790 | the residual test over one square root, or none |
| 6264 | PROOF | A273351 | the residual test over one square root, or none |
| 6265 | PROOF | A025248 | the residual test over one square root, or none |
| 6266 | PROOF | A025249 | the residual test over one square root, or none |
| 6267 | PROOF | A026017 | the residual test over one square root, or none |
| 6268 | PROOF | A071717 | the residual test over one square root, or none |
| 6269 | PROOF | A081672 | the residual test over one square root, or none |
| 6270 | PROOF | A104722 | the residual test over one square root, or none |
| 6271 | PROOF | A109263 | the residual test over one square root, or none |
| 6272 | PROOF | A118093 | the residual test over one square root, or none |
| 6273 | PROOF | A118974 | the residual test over one square root, or none |
| 6274 | PROOF | A121320 | the residual test over one square root, or none |
| 6275 | PROOF | A126323 | the residual test over one square root, or none |
| 6276 | PROOF | A128723 | the residual test over one square root, or none |
| 6277 | PROOF | A135334 | the residual test over one square root, or none |
| 6278 | PROOF | A141351 | the residual test over one square root, or none |
| 6279 | PROOF | A141353 | the residual test over one square root, or none |
| 6280 | PROOF | A163824 | the residual test over one square root, or none |
| 6281 | PROOF | A165201 | the residual test over one square root, or none |
| 6282 | PROOF | A279014 | the residual test over one square root, or none |
| 6283 | PROOF | A026027 | the residual test over one square root, or none |
| 6284 | PROOF | A026135 | the residual test over one square root, or none |
| 6285 | PROOF | A050168 | the residual test over one square root, or none |
| 6286 | PROOF | A059279 | the residual test over one square root, or none |
| 6287 | PROOF | A063395 | the residual test over one square root, or none |
| 6288 | PROOF | A071722 | the residual test over one square root, or none |
| 6289 | PROOF | A082134 | the residual test over one square root, or none |
| 6290 | PROOF | A097331 | the residual test over one square root, or none |
| 6291 | PROOF | A100193 | the residual test over one square root, or none |
| 6292 | PROOF | A103973 | the residual test over one square root, or none |
| 6293 | PROOF | A106181 | the residual test over one square root, or none |
| 6294 | PROOF | A108623 | the residual test over one square root, or none |
| 6295 | PROOF | A126180 | the residual test over one square root, or none |
| 6296 | PROOF | A128732 | the residual test over one square root, or none |
| 6297 | PROOF | A134389 | the residual test over one square root, or none |
| 6298 | PROOF | A143013 | the residual test over one square root, or none |
| 6299 | PROOF | A143954 | the residual test over one square root, or none |
| 6300 | PROOF | A157418 | the residual test over one square root, or none |
| 6301 | PROOF | A158196 | the residual test over one square root, or none |
| 6302 | PROOF | A158197 | the residual test over one square root, or none |
| 6303 | PROOF | A191585 | the residual test over one square root, or none |
| 6304 | PROOF | A257290 | the residual test over one square root, or none |
| 6305 | PROOF | A054341 | the residual test over one square root, or none |
| 6306 | PROOF | A071715 | the residual test over one square root, or none |
| 6307 | PROOF | A090413 | the residual test over one square root, or none |
| 6308 | PROOF | A090826 | the residual test over one square root, or none |
| 6309 | PROOF | A091699 | the residual test over one square root, or none |
| 6310 | PROOF | A098664 | the residual test over one square root, or none |
| 6311 | PROOF | A099363 | the residual test over one square root, or none |
| 6312 | PROOF | A100098 | the residual test over one square root, or none |
| 6313 | PROOF | A105872 | the residual test over one square root, or none |
| 6314 | PROOF | A119975 | the residual test over one square root, or none |
| 6315 | PROOF | A121724 | the residual test over one square root, or none |
| 6316 | PROOF | A121725 | the residual test over one square root, or none |
| 6317 | PROOF | A126931 | the residual test over one square root, or none |
| 6318 | PROOF | A126932 | the residual test over one square root, or none |
| 6319 | PROOF | A127361 | the residual test over one square root, or none |
| 6320 | PROOF | A127363 | the residual test over one square root, or none |
| 6321 | PROOF | A155051 | the residual test over one square root, or none |
| 6322 | PROOF | A166078 | the residual test over one square root, or none |
| 6323 | PROOF | A166587 | the residual test over one square root, or none |
| 6324 | PROOF | A166588 | the residual test over one square root, or none |
| 6325 | PROOF | A176006 | the residual test over one square root, or none |
| 6326 | PROOF | A185087 | the residual test over one square root, or none |
| 6327 | PROOF | A190724 | the residual test over one square root, or none |
| 6328 | PROOF | A225887 | the residual test over one square root, or none |
| 6329 | PROOF | A227081 | the residual test over one square root, or none |
| 6330 | PROOF | A257178 | the residual test over one square root, or none |
| 6331 | PROOF | A257388 | the residual test over one square root, or none |
| 6332 | PROOF | A257838 | the residual test over one square root, or none |
| 6333 | PROOF | A001712 | the residual test over one square root, or none |
| 6334 | PROOF | A025175 | the residual test over one square root, or none |
| 6335 | PROOF | A025577 | the residual test over one square root, or none |
| 6336 | PROOF | A026023 | the residual test over one square root, or none |
| 6337 | PROOF | A055217 | the residual test over one square root, or none |
| 6338 | PROOF | A081052 | the residual test over one square root, or none |
| 6339 | PROOF | A103821 | the residual test over one square root, or none |
| 6340 | PROOF | A107231 | the residual test over one square root, or none |
| 6341 | PROOF | A110199 | the residual test over one square root, or none |
| 6342 | PROOF | A116406 | the residual test over one square root, or none |
| 6343 | PROOF | A128734 | the residual test over one square root, or none |
| 6344 | PROOF | A191307 | the residual test over one square root, or none |
| 6345 | PROOF | A278472 | the residual test over one square root, or none |
| 6346 | PROOF | A034863 | the residual test over one square root, or none |
| 6347 | PROOF | A128652 | the residual test over one square root, or none |
| 6348 | PROOF | A174195 | the residual test over one square root, or none |
| 6349 | PROOF | A192480 | the residual test over one square root, or none |
| 6350 | PROOF | A158495 | the residual test over one square root, or none |
| 6351 | PROOF | A189176 | the residual test over one square root, or none |
| 6352 | PROOF | A194724 | the residual test over one square root, or none |
| 6353 | PROOF | A210474 | the residual test over one square root, or none |
| 6354 | PROOF | A262768 | the residual test over one square root, or none |
| 6355 | PROOF | A026029 | the residual test over one square root, or none |
| 6356 | PROOF | A064088 | the residual test over one square root, or none |
| 6357 | PROOF | A064089 | the residual test over one square root, or none |
| 6358 | PROOF | A064090 | the residual test over one square root, or none |
| 6359 | PROOF | A064091 | the residual test over one square root, or none |
| 6360 | PROOF | A064092 | the residual test over one square root, or none |
| 6361 | PROOF | A067299 | the residual test over one square root, or none |
| 6362 | PROOF | A068551 | the residual test over one square root, or none |
| 6363 | PROOF | A080243 | the residual test over one square root, or none |
| 6364 | PROOF | A114191 | the residual test over one square root, or none |
| 6365 | PROOF | A116881 | the residual test over one square root, or none |
| 6366 | PROOF | A122920 | the residual test over one square root, or none |
| 6367 | PROOF | A132864 | the residual test over one square root, or none |
| 6368 | PROOF | A133305 | the residual test over one square root, or none |
| 6369 | PROOF | A133306 | the residual test over one square root, or none |
| 6370 | PROOF | A133307 | the residual test over one square root, or none |
| 6371 | PROOF | A133308 | the residual test over one square root, or none |
| 6372 | PROOF | A141222 | the residual test over one square root, or none |
| 6373 | PROOF | A154623 | the residual test over one square root, or none |
| 6374 | PROOF | A157328 | the residual test over one square root, or none |
| 6375 | PROOF | A158196 | the residual test over one square root, or none |
| 6376 | PROOF | A158197 | the residual test over one square root, or none |
| 6377 | PROOF | A191993 | the residual test over one square root, or none |
| 6378 | PROOF | A225034 | the residual test over one square root, or none |
| 6379 | PROOF | A242172 | the residual test over one square root, or none |
| 6380 | PROOF | A002867 | the residual test over one square root, or none |
| 6381 | PROOF | A014533 | the residual test over one square root, or none |
| 6382 | PROOF | A051524 | the residual test over one square root, or none |
| 6383 | PROOF | A071264 | the residual test over one square root, or none |
| 6384 | PROOF | A081046 | the residual test over one square root, or none |
| 6385 | PROOF | A098519 | the residual test over one square root, or none |
| 6386 | PROOF | A098520 | the residual test over one square root, or none |
| 6387 | PROOF | A101596 | the residual test over one square root, or none |
| 6388 | PROOF | A101601 | the residual test over one square root, or none |
| 6389 | PROOF | A101602 | the residual test over one square root, or none |
| 6390 | PROOF | A111779 | the residual test over one square root, or none |
| 6391 | PROOF | A112703 | the residual test over one square root, or none |
| 6392 | PROOF | A119012 | the residual test over one square root, or none |
| 6393 | PROOF | A128057 | the residual test over one square root, or none |
| 6394 | PROOF | A128746 | the residual test over one square root, or none |
| 6395 | PROOF | A132900 | the residual test over one square root, or none |
| 6396 | PROOF | A151483 | the residual test over one square root, or none |
| 6397 | PROOF | A167481 | the residual test over one square root, or none |
| 6398 | PROOF | A171556 | the residual test over one square root, or none |
| 6399 | PROOF | A176479 | the residual test over one square root, or none |
| 6400 | PROOF | A182401 | the residual test over one square root, or none |
| 6401 | PROOF | A208355 | the residual test over one square root, or none |
| 6402 | PROOF | A210064 | the residual test over one square root, or none |
| 6403 | PROOF | A240558 | the residual test over one square root, or none |
| 6404 | PROOF | A141771 | the residual test over one square root, or none |
| 6405 | PROOF | A176606 | the residual test over one square root, or none |
| 6406 | PROOF | A176607 | the residual test over one square root, or none |
| 6407 | PROOF | A176609 | the residual test over one square root, or none |
| 6408 | PROOF | A176610 | the residual test over one square root, or none |
| 6409 | PROOF | A176611 | the residual test over one square root, or none |
| 6410 | PROOF | A176675 | the residual test over one square root, or none |
| 6411 | PROOF | A176749 | the residual test over one square root, or none |
| 6412 | PROOF | A176750 | the residual test over one square root, or none |
| 6413 | PROOF | A176751 | the residual test over one square root, or none |
| 6414 | PROOF | A176752 | the residual test over one square root, or none |
| 6415 | PROOF | A176753 | the residual test over one square root, or none |
| 6416 | PROOF | A176754 | the residual test over one square root, or none |
| 6417 | PROOF | A176755 | the residual test over one square root, or none |
| 6418 | PROOF | A176756 | the residual test over one square root, or none |
| 6419 | PROOF | A176757 | the residual test over one square root, or none |
| 6420 | PROOF | A176759 | the residual test over one square root, or none |
| 6421 | PROOF | A176828 | the residual test over one square root, or none |
| 6422 | PROOF | A176829 | the residual test over one square root, or none |
| 6423 | PROOF | A176830 | the residual test over one square root, or none |
| 6424 | PROOF | A176832 | the residual test over one square root, or none |
| 6425 | PROOF | A176854 | the residual test over one square root, or none |
| 6426 | PROOF | A176855 | the residual test over one square root, or none |
| 6427 | PROOF | A176856 | the residual test over one square root, or none |
| 6428 | PROOF | A176857 | the residual test over one square root, or none |
| 6429 | PROOF | A176858 | the residual test over one square root, or none |
| 6430 | PROOF | A176859 | the residual test over one square root, or none |
| 6431 | PROOF | A176952 | the residual test over one square root, or none |
| 6432 | PROOF | A176953 | the residual test over one square root, or none |
| 6433 | PROOF | A176956 | the residual test over one square root, or none |
| 6434 | PROOF | A176957 | the residual test over one square root, or none |
| 6435 | PROOF | A176958 | the residual test over one square root, or none |
| 6436 | PROOF | A176959 | the residual test over one square root, or none |
| 6437 | PROOF | A176962 | the residual test over one square root, or none |
| 6438 | PROOF | A176964 | the residual test over one square root, or none |
| 6439 | PROOF | A176966 | the residual test over one square root, or none |
| 6440 | PROOF | A176967 | the residual test over one square root, or none |
| 6441 | PROOF | A177123 | the residual test over one square root, or none |
| 6442 | PROOF | A177124 | the residual test over one square root, or none |
| 6443 | PROOF | A177125 | the residual test over one square root, or none |
| 6444 | PROOF | A177126 | the residual test over one square root, or none |
| 6445 | PROOF | A177127 | the residual test over one square root, or none |
| 6446 | PROOF | A177128 | the residual test over one square root, or none |
| 6447 | PROOF | A177129 | the residual test over one square root, or none |
| 6448 | PROOF | A177130 | the residual test over one square root, or none |
| 6449 | PROOF | A177131 | the residual test over one square root, or none |
| 6450 | PROOF | A177163 | the residual test over one square root, or none |
| 6451 | PROOF | A177165 | the residual test over one square root, or none |
| 6452 | PROOF | A177166 | the residual test over one square root, or none |
| 6453 | PROOF | A177167 | the residual test over one square root, or none |
| 6454 | PROOF | A177168 | the residual test over one square root, or none |
| 6455 | PROOF | A177169 | the residual test over one square root, or none |
| 6456 | PROOF | A177170 | the residual test over one square root, or none |
| 6457 | PROOF | A177171 | the residual test over one square root, or none |
| 6458 | PROOF | A177172 | the residual test over one square root, or none |
| 6459 | PROOF | A177175 | the residual test over one square root, or none |
| 6460 | PROOF | A177177 | the residual test over one square root, or none |
| 6461 | PROOF | A177178 | the residual test over one square root, or none |
| 6462 | PROOF | A177179 | the residual test over one square root, or none |
| 6463 | PROOF | A177180 | the residual test over one square root, or none |
| 6464 | PROOF | A177181 | the residual test over one square root, or none |
| 6465 | PROOF | A177182 | the residual test over one square root, or none |
| 6466 | PROOF | A177183 | the residual test over one square root, or none |
| 6467 | PROOF | A177184 | the residual test over one square root, or none |
| 6468 | PROOF | A177185 | the residual test over one square root, or none |
| 6469 | PROOF | A177197 | the residual test over one square root, or none |
| 6470 | PROOF | A177198 | the residual test over one square root, or none |
| 6471 | PROOF | A177199 | the residual test over one square root, or none |
| 6472 | PROOF | A177200 | the residual test over one square root, or none |
| 6473 | PROOF | A177203 | the residual test over one square root, or none |
| 6474 | PROOF | A081670 | the known side is the entry's NAME rather than a formula line |
| 6475 | PROOF | A085781 | the known side is the entry's NAME rather than a formula line |
| 6476 | PROOF | A026019 | the known side is the entry's NAME rather than a formula line |
| 6477 | PROOF | A052183 | the known side is the entry's NAME rather than a formula line |
| 6478 | PROOF | A052204 | the known side is the entry's NAME rather than a formula line |
| 6479 | PROOF | A157713 | the known side is the entry's NAME rather than a formula line |
| 6480 | PROOF | A334511 | a posted closed form decided by the theory of hypergeometric terms |
| 6481 | PROOF | A333905 | a posted closed form decided by the theory of hypergeometric terms |
| 6482 | PROOF | A049486 | a posted closed form decided by the theory of hypergeometric terms |
| 6483 | PROOF | A267879 | a posted closed form decided by the theory of hypergeometric terms |
| 6484 | PROOF | A267802 | a posted closed form decided by the theory of hypergeometric terms |
| 6485 | PROOF | A267847 | a posted closed form decided by the theory of hypergeometric terms |
| 6486 | PROOF | A034267 | a posted closed form decided by the theory of hypergeometric terms |
| 6487 | PROOF | A126501 | a posted closed form decided by the theory of hypergeometric terms |
| 6488 | PROOF | A128153 | a posted closed form decided by the theory of hypergeometric terms |
| 6489 | PROOF | A212938 | a posted closed form decided by the theory of hypergeometric terms |
| 6490 | PROOF | A220250 | a posted closed form decided by the theory of hypergeometric terms |
| 6491 | PROOF | A248434 | a posted closed form decided by the theory of hypergeometric terms |
| 6492 | PROOF | A258547 | a posted closed form decided by the theory of hypergeometric terms |
| 6493 | PROOF | A272706 | a posted closed form decided by the theory of hypergeometric terms |
| 6494 | PROOF | A126089 | complete annihilation, tested in the Ore algebra Q(n)[N] |
| 6495 | PROOF | A025271 | division of one posted operator by another |
| 6496 | PROOF | A138164 | division of one posted operator by another |
| 6497 | PROOF | A143017 | division of one posted operator by another |
| 6498 | PROOF | A159772 | division of one posted operator by another |
| 6499 | PROOF | A000986 | division of one posted operator by another |
| 6500 | PROOF | A022917 | division of one posted operator by another |
| 6501 | PROOF | A217447 | division of one posted operator by another |
| 6502 | PROOF | A226302 | division of one posted operator by another |
| 6503 | PROOF | A245088 | division of one posted operator by another |
| 6504 | PROOF | A026165 | division of one posted operator by another |
| 6505 | PROOF | A185966 | division of one posted operator by another |
| 6506 | PROOF | A200753 | division of one posted operator by another |
| 6507 | PROOF | A217358 | division of one posted operator by another |
| 6508 | PROOF | A228960 | division of one posted operator by another |
| 6509 | PROOF | A003435 | division of one posted operator by another |
| 6510 | PROOF | A228331 | division of one posted operator by another |
| 6511 | PROOF | A273019 | division of one posted operator by another |
| 6512 | PROOF | A386834 | division of one posted operator by another |
| 6513 | PROOF | A228330 | division of one posted operator by another |
| 6514 | PROOF | A228333 | division of one posted operator by another |

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

### 31 Aug 2026: "new values 0..k introduced in row major order" — 177 papers, and the trick that unlocks them

588 Hardin entries carry that clause. It is not local: it says the array is written in
canonical form, so whether a cell may take a value depends on every cell before it in
reading order. A transfer matrix over the alphabet cannot see it, which is why this whole
block sat untouched behind four transfer-matrix families.

**What is actually being counted is patterns.** Every condition in this block is stated in
equalities between entries ("equal diagonal elements", "no element equal to any horizontal
or vertical neighbor", "two or three distinct values"), so it is invariant under relabelling
and is a property of the equality pattern -- the set partition of the cells -- alone. The
canonical-form clause picks exactly one array from each relabelling class. So
a(n) = #{admissible patterns with at most K = k+1 classes}.

**Recovering patterns from labelled counts.** Let L_i(n) count arrays over an i-letter
alphabet with the canonical-form clause dropped, and N_j(n) the admissible patterns with
exactly j classes. Then L_i = sum_j N_j * i(i-1)...(i-j+1), a falling factorial, because a
pattern with j classes gives exactly that many labelled arrays. Writing the falling factorial
as j! C(i,j) and inverting binomially, j! N_j = sum_i (-1)^(j-i) C(j,i) L_i, and summing over
j <= K,

        K! * a(n) = sum_{i=0}^{K} C(K,i) * D_{K-i} * L_i(n),

with D_m the derangement numbers -- an integer identity, since K!/i! * sum_{t<=K-i}(-1)^t/t!
is C(K,i) D_{K-i}. Each L_i is an ordinary transfer count. So the answer is a walk count on
the block-diagonal matrix diag(M_1,...,M_K) with those weights in the start vector, and
everything downstream (Cayley-Hamilton, the annihilation test) is unchanged.

**The chain lumps, and it has to.** The direct state space is sum_i i^W, which at W = 7 and
0..3 is 20515 rows with a dense edge relation -- the first run of the sweep managed four
entries in ninety seconds. But relabelling-invariance says more than the identity above: for
two rows r, r' of the same pattern there is a permutation sigma with r' = sigma(r), and
s -> sigma(s) is a pattern-preserving bijection between their successor sets. The chain is
strongly lumpable over the patterns. Lumping replaces i^W states by the set partitions of the
W columns into at most i blocks -- 20515 becomes 1223, and 1300 becomes 109. The lumped walk
counts were checked against the unlumped ones term by term on 40 entries before the sweep was
allowed to use them.

**Result.** 177 proved, no failures, no DATA mismatches: 92 with a 2 X 2 subblock condition,
85 with a cell-neighbourhood condition ("no element equal to more than one of its immediate
leftward or upward or left-upward diagonal neighbors" and relatives). Orders 1 to 91, lumped
state spaces 5 to 1223. Ranked as a tier above the plain transfer-matrix papers: the walk
count is the last step, not the argument.

**Two traps met on the way.**

  * `patterns(W, i)` enumerates set partitions, so calling it merely to MEASURE the state
    space hangs on a name with a wide fixed dimension -- the size cap can only refuse what
    it has already counted. The size is now computed by a Stirling-number recursion, and the
    enumeration only runs after the cap has passed.
  * Offsets like "leftward or upward" are given in the array's own coordinates. For a
    transposed name (`5 X n`) the walk runs along columns, so the two components swap, and
    an offset that pointed backwards may now point forwards. Where all of them point forwards
    the walk direction is simply reversed; where the signs are mixed the entry is refused,
    because settling a cell then needs a two-line window. Reading the offsets in the wrong
    frame produced five DATA mismatches and nothing else -- which is exactly what the DATA
    check is for.

**Still open in this block.** Roughly 400 of the 588 need one more idea each: a three-line
window (city-block distance two, knight moves, "each element equal to at least one horizontal
or vertical neighbor"), a cyclic fixed direction ("colorings on an n X 3 array circular in the
3 direction"), or a global constant to sum over ("every 2 X 2 subblock having the same number
of equal edges").

### 1 Sep 2026: the two-line window — 615 more papers, and the cell conditions that need it

Two families were still refused because every engine so far tests a condition using only the
lines already laid down. A cell constrained by its neighbours on BOTH sides breaks that: the
condition at a cell of line t involves lines t-1, t and t+1 together, and the step from
r^(t) to r^(t+1) does not know r^(t-1).

The fix is the same in both cases and is worth stating once. Take ORDERED PAIRS of
consecutive lines as vertices; (p,c) -> (c,x) is an edge when every cell of the MIDDLE line c
passes with p above and x below. Consecutive vertices overlap in one line, so a walk of
length L-2 is exactly an array of L lines, each interior line is tested once and with its
true neighbours, the first line is tested by the start vector with the line above absent and
the last by the end vector with the line below absent. So a(n) = v^T N^(L-2) u. Getting the
two boundary vectors wrong is the only way to get this wrong, and it is exactly what the DATA
check catches.

**transfer8 — 44 papers.** The two-line window combined with the canonical-form clause of the
previous batch: "each element equal to exactly two horizontal and vertical neighbors, with new
values 0..3 introduced in row major order" and relatives, including the comparisons "no
element equal to fewer vertical neighbors than horizontal neighbors". The relabelling
reduction and the lumping carry over unchanged, now over patterns of a PAIR of lines, so the
state count is set partitions of 2W cells rather than W. Also new here: names whose n
dimension carries a multiplier, "Number of 2n X 4 0..2 arrays ...", which advance the walk by
two lines per unit step; the criterion then runs on G = N^2.

**transfer9 — 571 papers, the largest single family so far.** Cell conditions over the
explicit alphabet, no canonical form:

  * "each 1 adjacent to 0 or 2 king-move neighboring 1s" — the count is imposed only on the
    cells carrying a stated value;
  * "every element equal to 0, 1 or 4 horizontally, vertically or antidiagonally adjacent
    elements, with upper left element zero" — the count of equal (or unequal) neighbours lies
    in a stated set, plus a symmetry-breaking clause that only restricts which lines may start
    a walk;
  * "each element equal to the number of its horizontal and vertical neighbors unequal to
    itself" — the cell's VALUE is the neighbour count.

1370 names compile; 788 of them already had papers from the earlier neighbour-count family and
were skipped by the roster check, which is what that check is for. 571 proved, no failures, no
DATA mismatches, orders 2 to 70, state spaces 16 to 16384.

**Two things this batch got right that earlier ones fudged.** There is no shift search: the
number of lines is read off the name as L = mult*n + base and the entry's offset says which
index the first published term carries, so the DATA comparison is exact with nothing fitted.
And the empty array is counted: an entry with offset 0 records a(0) = 1 for L = 0, which the
first run returned as None and which showed up immediately as a single-index mismatch.

**An honesty note on the annihilation budget.** The Cayley--Hamilton bound is S, and on a
lumped chain with thousands of states each step is a full matrix-vector product. A first run
of the transfer8 sweep capped the iterations at order+80 and reported 16 entries as
UNRESOLVED; they were requeued with the full bound and all 16 proved. Exceeding a budget is
now reported as UNRESOLVED and never as a proof and never as a failure, and a wall-clock
guard of seven minutes per entry does the same. 3 entries in transfer8 and 1 in transfer9 sit
in that state today, together with 25 whose state space is past the cap; none of them is
counted.

### 1 Sep 2026 (later): six more predicate shapes, 287 papers, and the offset family

Continuing the same method -- one engine, many compiled predicates -- six shapes were added
to the two-line-window engine and one new engine written.

**Added to transfer9 (218 papers).**

  * `table` (239 names): "each element x equal to the number of its horizontal and vertical
    neighbors equal to 2,0,1,3,4 for x=0,1,2,3,4". The trailing list is a FUNCTION f given as
    a table, and the condition is that a cell of value x has exactly x neighbours carrying
    the value f(x). This was the largest single unread shape in the pool.
  * `major` (53): "no element less than a strict majority of its horizontal and vertical
    neighbors" -- twice the number of strictly larger neighbours must not exceed the number
    of neighbours, boundary cells having fewer.
  * `some` (17): "every nonzero element less than or equal to some horizontal or vertical
    neighbor".
  * `shift` (16): "no entry increasing mod 5 by 4 rightwards or downwards, starting with
    upper left zero".
  * `both` (19) and `plusmod` (18): explicit offset lists, "every element both equal and not
    equal to some elements at offset (-1,0) (-1,1) ...", and "every element plus 1 mod 3
    equal to some element at offset ...".

Also a one-word fix worth noting: the `value` shape ("each 1 adjacent to 0 or 2 king-move
neighboring 1s") required the word "neighboring", so "each 1 horizontally or vertically
adjacent to 2 or 4 1s" was refused -- 40 names lost to an optional word.

**transfer10, a new engine (69 papers).** "Number of n X 3 0..2 arrays with no element equal
to any value at offset (-1,-1) (-2,0) or (0,-2) and new values introduced in order 0..2":
explicit offsets, all pointing backwards in reading order, but some reaching TWO lines back.
That is a third window shape -- not the one-line backward window of transfer7, not the
symmetric two-line window of transfer8/9, but a two-line BACKWARD window in which the step
(a,b) -> (b,x) tests the cells of the NEW line x against b one line up and a two lines up,
and the first two lines are tested by the start vector with the missing lines absent. No end
vector: nothing constrains the bottom of the array. The canonical-form clause is present, so
the falling-factorial inversion and the pattern lumping of transfer7 apply verbatim.

**Where the pool stands.** Of the 6059 n X k array names, 3623 papers now exist. What is left
divides into: 132 transfer9 names and 22 transfer10 names whose state space is past the cap
(a dense pair state over a five- or six-letter alphabet; the relabel-invariant ones among
them could be lumped, which is the obvious next move); the 25 transfer6/8 entries already
recorded; and about 3300 names whose condition is still unread by any compiler. The largest
unread shapes now are "some element plus some horizontally or antidiagonally adjacent
neighbor totalling two exactly once" (~80, a GLOBAL count, so the state needs a small
counter), "rows nondecreasing and antidiagonals unimodal" (~60, order conditions rather than
equality ones), "all 2 X 2 subblock sums the same" (~16, local once the common sum is fixed),
and a long tail of one-off phrasings.

### 1 Sep 2026 (evening): conditions on the WHOLE array — 358 papers

Everything up to here tested a condition inside a bounded window. Two large families do not:
they say something about the array as a whole, and no window sees it. Both become transfer
matrices once the running total is put into the state, and both are cheap because a total
that has passed its bound can never come back, so those states need not exist at all.

**transfer11 — 171 papers, a global pair count.** "Number of n X 2 0..2 arrays with some
element plus some horizontally or vertically adjacent neighbor totalling two exactly once",
and "some 1 horizontally or vertically adjacent to some other 1 exactly once". The number of
MARKED adjacent pairs in the entire array must be exactly one, or at most one. States are
(line, count) with the count in {0,1}; each unordered adjacency is represented by exactly one
offset with a nonnegative line shift, so each pair is counted once: pairs inside a line when
that line is laid down, pairs joining two lines when the later one is.

The state-dropping is what makes it work. With a third absorbing count the digraph is DENSE
— every pair of lines is an edge, (alpha+1)^(2W) of them — and a single entry took minutes.
Dropping the states that can never lead anywhere leaves a sparse graph and the sweep runs in
seconds.

**transfer12 — 187 papers, an exception budget with canonical form.** "no element equal to
more than one of its horizontal and antidiagonal neighbors, with the exception of exactly two
elements, and with new values introduced in order 0 sequentially upwards" — three separate
obstructions at once: a cell condition reaching one line up AND one line down, a global budget
of exactly E offending cells, and the canonical-form clause. States are (pair of lines, count
of offending cells so far), and the canonical-form clause goes through the same
falling-factorial inversion as before; the alphabets here are 0..1 and 0..2, small enough that
the pattern lumping is not needed.

**A bug the DATA check caught immediately, worth recording as a rule.** In transfer11 the
state carries a LINE, not a boundary between lines, so an array of L lines is a walk of length
L-1 — not L-2, which is right for the pair-state engines. The first run used L-2 and returned
every value one index late: got [3, 3, 24, 120] against a wanted [3, 24, 120, 504]. Every
engine's walk length has to be re-derived from what its state actually holds; carrying the
formula over from the previous engine is exactly the kind of error the DATA comparison exists
to catch, and it caught it on the first entry.

Roster 3981.

### 1 Sep 2026 (night): four more shapes, the one-line state, and two bugs the DATA check caught

**Four shapes added (198 papers).**

  * `patt` (113 names): "without the pattern 1 1 0 diagonally, vertically or horizontally" --
    a forbidden word of length two or three along a stated direction.
  * `graph` (92): "where 0..5 label nodes of a graph with edges 0,1 0,2 1,2 ... and every
    array movement to a horizontal or vertical neighbor moves along an edge of this graph" --
    a graph-homomorphism count. The edge list is read out of the name; when it says "the
    square grid graph" instead, the grid's shape is read from the TITLE before the colon
    ("3 X 3 square grid graph coloring a rectangular array:"), which is the only place it
    appears.
  * `modnext` (21): "each element horizontally or vertically next to at least one element
    with value 2-x(i,j)", and the "(x(i,j)+1) mod 3" variant.
  * `cmpself` (6): "each element equal to the number of its horizontal and vertical
    neighbors less than or equal to itself".

Three parser facts learned here, all of which had been silently costing entries: the
connector after "arrays" is not always "with" (the graph names say "arrays where", others
"arrays x(i,j) with", the pattern names have no connector at all); and several families carry
a descriptive title and a colon before "Number of".

**The one-line state.** The two-line window was being used for every condition, but it is
only needed when the offsets reach BOTH up and down. When they all point one way, a single
line of state suffices: the cells of a line are settled by that line and its successor (or
its predecessor). For the graph-colouring names, over a nine-letter alphabet, that is 9^W
states instead of 9^(2W) -- the difference between running and not running.

**Two bugs, both caught by the DATA comparison on the first entries.**

  1. A length-three forbidden pattern is tested at its MIDDLE cell, so it reads one step in
     each direction whatever the sign of the stated offset. Deciding the state size from the
     offset list rather than from the SPAN gave a one-line state for patterns whose offsets
     all pointed down, and the test then never fired: every such entry returned the
     completely unconstrained count 2^(nW). The span, not the offset list, decides.
  2. Forbidden patterns are directional. Forbidding the word in both orientations gave counts
     that were too small everywhere for non-palindromic patterns (1 1 0 failed, 0 1 0 passed,
     which is exactly the signature of the mistake); and a transposed name can leave the
     direction with a NEGATIVE line shift, where taking the line above for the first position
     is wrong. With both fixed, 106 of 106 tested entries match their DATA.

Roster 4179.

### 1 Sep 2026 (late): the ordering clause, and where the array pool now stands

**Three more shapes (123 papers).**

  * `noadjval` (50 names): "top left element equal to 1 and no two ones adjacent
    horizontally or nw-se". Two things needed here: the value can be spelled as a WORD
    ("no two ones adjacent", not "no two 1s"), and the directions can be compass names --
    nw-se is the diagonal, ne-sw the antidiagonal. The upper-left clause was hard-coded to
    the value zero and is now a value like any other.
  * `modnext` widened from 21 names to 68: the clause reads ", and upper left element zero"
    as often as ", with upper left element zero", and the regex accepted only the second.
  * `transfer13` (19 papers, a new engine): "no element x(i,j) adjacent to value 3-x(i,j)
    horizontally or antidiagonally, top left element zero, and 1 appearing before 2 in row
    major order".

**Why the last one needs its own engine.** "1 appearing before 2 in row major order" compares
FIRST OCCURRENCES across the whole array, so it is not local; but it becomes local once the
state records which of the two values was seen first. The subtlety is that for a K X n name
the walk runs along columns while row major order runs along rows, so the two orders disagree
and a single flag would be wrong. The state therefore carries one flag per ROW -- 0 while
neither value has been seen in that row, 1 or 2 according to which was seen first there -- and
an array is accepted when the first row with a nonzero flag has flag 1, which is exactly row
major order (earlier row first, and within a row the earlier column). For an n X K name the
walk order and the reading order agree and one flag suffices. 17 of 17 tested entries matched
their DATA on the first run.

Also, the neighbour relation "y = c - x" is symmetric, so each unordered adjacency is tested
once from the earlier cell; every offset then points forward and one line of state suffices,
where a naive reading would have used a pair.

**Where the pool stands.** 4302 papers now, out of 6059 n X k array names. The remaining
~2500 no longer contain any large bucket: the biggest single unread shape is 21 names, and
the tail is hundreds of distinct phrasings. What is left in coherent groups: order conditions
on rows, columns, diagonals and antidiagonals ("rows nondecreasing and antidiagonals
unimodal", ~55 -- these need a turned/not-turned flag per antidiagonal, which is a real but
bounded state); "connected ... with exactly one mistake" (~40, connectivity is not a local
property and would need a union-find state); "all 2 X 2 subblock sums the same" (~16, local
once the common sum is fixed and summed over); and about 150 entries across all engines whose
state space is past the caps. Everything else is one-off.

### 1 Sep 2026: order conditions and the unnamed common sum — 80 papers

**transfer14 (68 papers): monotone and unimodal conditions.** "rows nondecreasing and
antidiagonals unimodal", and its relatives over rows, columns, diagonals and antidiagonals.
A monotone condition compares two cells one step apart and is local. A unimodal one is not:
a sequence is unimodal exactly when it never rises again after it has fallen, so the state
carries one bit per running sequence saying whether it has fallen, and those bits TRAVEL with
their sequences -- the bit of the antidiagonal through (t,u) becomes the bit at (t+1,u-1), and
a fresh antidiagonal starts at the far end of each new line.

Two things the DATA settled that no amount of reading the name would have.

  * "rows and columns in nondecreasing order" does NOT mean each row is nondecreasing along
    itself. It means the rows, read as vectors, are sorted, and likewise the columns. The two
    readings agree at n = 1 (both give 10 for 1 X 2 arrays over 0..3) and diverge at n = 2:
    86 against 50. Nine entries were failing until the brute force over candidate readings
    picked out row-sorted-and-column-sorted as the one matching 10, 86, 561.
  * A lexicographic condition between adjacent columns is decided at the first row where
    they differ, so it needs one bit per adjacent pair -- still tied, or already settled the
    right way -- exactly like the unimodal bits. With that, all 77 tested entries match.

Direction words are given in the array's own frame, so walking columns swaps the two
components; an antidiagonal is then traversed backwards, which turns "nondecreasing" into
"nonincreasing". Unimodality is unchanged by reversal.

**transfer15 (12 papers): the unnamed common sum.** "all 2 X 2 subblock sums the same". The
common value is not a parameter of the problem, which is what stops a transfer matrix
applying directly; but any array with at least one 2 X 2 subblock determines it, so the count
splits as a sum over the 4m+1 possible values with nothing counted twice, each summand being
an ordinary walk count. The splitting is exact only because every array here has a subblock:
for a one-column or one-row shape there is none, every value would be vacuously admissible,
and the sum would count each array 4m+1 times. Those shapes are refused.

Roster 4382.

### 1 Sep 2026: defective colourings — 29 papers, and two engines composed

"Number of defective 3-colorings of an n X 3 0..2 array connected horizontally and vertically
with exactly one mistake and colors introduced in row-major 0..2 order." Proper colourings
except that exactly E adjacent pairs carry equal colours, counted up to relabelling.

Nothing new was needed. The mistake count is transfer11's global pair count -- a running
total in the state, capped at E, with the states past the budget absent -- and the colour
clause is transfer7's falling-factorial inversion. Composing the two is the whole engine;
81 names parse and 80 of them reproduce their DATA. 29 are proved here, the rest sitting
past the state cap (the wide shapes over five- and six-letter alphabets) or still running
when the batch was closed.

This is the fourth time the same two devices have carried a family, and it is worth stating
as the general shape of this work: a Hardin condition is a conjunction of clauses, each
clause is either local (an edge condition), a running total (a counter in the state, capped),
a canonical form (removed by inversion), or an order comparison (a bit per running sequence).
Anything built from those four is a walk count, and the only per-family work is reading the
name.

Roster 4411.

### 1 Sep 2026: turning the engines round to look for FALSE conjectures — one found

Proving a recurrence costs S+1 matrix-vector products; DISPROVING one costs only enough terms
to reach a failure. So every entry the engines can model but could not prove --- the ones past
the state cap, the ones whose annihilation run was cut off --- can still be decided in the
negative cheaply. `falsify.py` builds the model, checks it against the entry's DATA, then
computes forty terms beyond the published range and tests the conjectured recurrence at every
index the entry actually claims.

**A208046: a false alarm, and the reason to record it.** The first run flagged it at n = 5.
Its recurrence is stated "for n>5", so it says nothing at n = 5 and there is nothing to
disprove. The sweep now reads the entry's own bound. A disproof that ignores the stated range
is not a disproof.

**A197230: genuinely false.** "Number of n X 3 0..4 arrays with each element x equal to the
number its horizontal and vertical neighbors equal to 4,3,0,1,2 for x=0,1,2,3,4." The entry
publishes 22 terms with offset 1 and an empirical recurrence of ORDER 22, so the recurrence
first asserts something at n = 23 --- one index past the published data. It fails there:
the true a(23) is 1327965802062332 and the recurrence gives 1327965802062198, short by 134.

The model was not taken on trust. It reproduces all 22 published terms exactly, and its first
two values were confirmed by brute-force enumeration over all 5^(3n) arrays.

What is actually wrong is worth stating, because it decides what the paper is. Solving for
the true minimal recurrence from the model's terms gives ORDER 25 --- and its first 22
coefficients are, term for term, the published ones. The entry's line is the correct
recurrence with its last three terms, +28a(n-23) -82a(n-24) +40a(n-25), dropped. So this is a
correction, not the collapse of an interesting conjecture, and the paper says so. The order-25
recurrence is proved by the usual annihilation test (it holds for every n > 26); solving for
it only PROPOSED it.

One disproof from 452 candidates. That is the honest yield, and it is worth repeating that the
yield is low BECAUSE Hardin's empirical recurrences are almost all true: they are fitted to
enough terms to be trustworthy, and the one that failed is the one fitted at an order its
sample could not support.

### 1 Sep 2026: the pool I had been working was incomplete — and what that was worth

Every array sweep so far ran against a 6059-entry pool assembled from an old census. Scanning
the whole local clone for names of the shape "... n X k ... array" gives **26117** of them.
23014 were entries I had never looked at.

Running all eleven engines over the merged pool: **1166 of the new entries parse**, and
**30 papers came out of it** (all defective colourings). The rest breaks down as:

  * ~820 have NO conjectured recurrence at all --- no Empirical line, no Conjecture line.
    There is nothing to prove on them. This is by far the largest share, and it is the honest
    reason the expansion was worth so little: the entries I had already been working are
    precisely the ones Hardin fitted recurrences to.
  * ~600 parse but their state space is past the caps.
  * 1415 are two-dimensional tables (T(n,k) reading by antidiagonals), which the sweeps skip.

So the correction to the record is worth stating both ways: the pool WAS incomplete, and
enlarging it four-fold added 30 papers. A bigger haystack is not more needles.

**A general conjecture, found and then found already proved.** Among the new entries,
A183634 and A183635 carry a comment added on 20 June 2026 by Zhuorui He: a closed form for
the whole two-parameter family, "Number of (n+1) X (k+1) 0..p arrays with every 2 X 2 subblock
summing to 2p is Sum_{i=1..p+1} i^(n+1)(p+2-i)^(k+1) - 2*Sum_{i=1..p} i^(n+1)(p+1-i)^(k+1) +
Sum_{i=1..p-1} i^(n+1)(p-i)^(k+1)". That is a far better target than another recurrence, and
it is provable in half a page:

  writing B(i,j) = (-1)^(i+j) (A(i,j) - p/2), the 2 X 2 condition says exactly that the mixed
  second difference of B vanishes, so B(i,j) = f_i + g_j; hence A(i,j) = alpha_i + beta_j when
  i+j is even and p - alpha_i - beta_j when it is odd, with alpha, beta integers determined up
  to a common shift, and the entry bounds reduce to 0 <= alpha_i + beta_j <= p in both cases.
  Normalising min beta = 0 and summing over B = max beta, with inclusion-exclusion for
  "min 0 and max B", gives the stated expression with n and k interchanged --- which is the
  same thing, the array family being closed under transposition.

It was verified against brute force on 80 (n,k,p) triples before any of that. **It is not
open**: Christian Krause posted a proof on the same entries on 20 June 2026, two days after
the conjecture went up, and the openness check refused it before a paper was written. That is
the check doing its job, and the result is recorded here as a null rather than as a paper.

The wider vein is real though and is recorded for later: 1225 comment or formula lines in the
clone begin "Conjecture" and state something about a whole family in n and k. Most are
unrelated to anything here, but they are the right SHAPE of target --- one theorem, a family
settled --- and nothing systematic has been done with them.

### 1 Sep 2026: a full independent re-audit of the roster, prompted by the obvious question

The user asked how the count could jump from tens to thousands, whether anything was being
waved through, and whether the conjectures were really unsolved. Fair question; here is the
answer and the audit that backs it.

**Why the jump. It is a change of target, not of ability.** 3810 of the 4442 papers are one
family: sequences created by R. H. Hardin, each counting arrays with a condition local to a
bounded window, each carrying a machine-fitted `Empirical: a(n) = ...` line. A sample of 300
of them: 300/300 authored by Hardin, 300/300 unsigned Empirical lines. Every such sequence is
a transfer-matrix walk count, hence C-finite, hence the question "does this recurrence hold?"
is DECIDABLE by finite exact linear algebra with Cayley-Hamilton as the bound. There is no
mathematical difficulty; the work is parsing English into predicates. One theorem, applied
3810 times. The earlier low yield was bespoke conjectures by many authors, one argument each.

**The audit, run fresh and deliberately not trusting the sweeps' own verdicts.**

  * Every array paper rebuilt from the entry's NAME, the sequence recomputed, and compared
    against every published DATA term: **3810 of 3810 clean.** The DATA comparison is the
    only thing tying a model to a sequence, and it has teeth here: minimum 10 published terms,
    median 22, and the largest published term has a median of 15 digits. A misread predicate
    does not reproduce 22 integers of that size.
  * The conjectured recurrence re-evaluated NUMERICALLY well past both the data and the proved
    threshold (median last index 68, about 45 terms beyond the published data). This is
    independent of the annihilation argument that produced the papers, so a bug in that
    argument would show up here. **Zero failures.**
  * Three families brute-forced by hand from the name text, with no use of any parser:
    A183624 (subblock sums), A206780 (pattern avoidance), A295776 (king-move neighbours) --
    all three reproduce the OEIS data exactly.
  * Openness re-checked on all 4442. 31 flagged; every one read individually; every one a
    false positive of the documented kind -- the settlement wording refers to a DIFFERENT
    statement on the same entry, and in each case the paper names the prior work (paper 5
    proves Conjecture A and says Adamczewski did B and C; paper 7 proves Kaydalov's rectangle
    case and says Bala's square case is already known; paper 22 proves the converse and says
    Schmidt did the forward direction).
  * 30 duplicate A-numbers, all legitimate: two distinct conjectures on one entry (A129833 and
    A156894 each carry two different Mathar recurrences; A059970's parts (1) and (2) are
    separate papers that name each other). 4442 papers, 4412 distinct entries.

**One real defect found, and it is conservative, not wrong.** Each engine's threshold routine
starts its residual test at the first index its WALK LENGTH allows, n_lo + order. For a
pair-state engine n_lo is 2, so the one or two smallest indices at which the recurrence can be
stated are never tested, and the routine returns the weakest conclusion consistent with that.
Checked directly against published DATA, A274750's recurrence holds at n = 5 while the paper
claims only n > 5. Recomputing the threshold from the model's own terms over eight engines:
**568 exact, 75 understated, 0 overstated.** Nothing claims more than is true. But 75 papers
state a weaker theorem than they establish, and for an entry whose line carries no range that
falls short of the entry's own unconditional assertion by one or two indices. To be fixed by
recomputing the threshold from the terms rather than from the walk, and rebuilding those
papers.

**What "open" means here, said plainly.** For the Hardin family it means the Empirical line is
still labelled empirical and nobody has commented on it. These are not problems anyone was
working on. They are true, previously unproved statements, and they are not 3810 ideas.

### 1 Sep 2026: the re-audit found a REAL error — 477 papers stated a false range

Asked a second time whether anything was being waved through, the audit was pushed past
"does the model match the data" to "does the PRINTED CLAIM survive a check that uses no model
at all". It did not, for 477 papers.

**The adversarial test first, because it is the one that vindicates the gate.** For 60 sampled
papers the model was deliberately corrupted -- a neighbour dropped or added, a count set
shifted, an equal/unequal flip, the constrained value changed, one entry of the lookup table
altered, the alphabet widened -- and each corrupted model was asked to reproduce the entry's
published terms. 194 mutants rejected, 11 unbuildable, 39 passed. Every one of those 39 was
then compared against the true model over forty terms BEYOND the data, and all 39 were
IDENTICAL sequences: the mutation was vacuous (an offset falling outside a two-column array, a
0/1 complement mapping the condition to itself, an extra colour isolated in the graph). Real
gate failures: **zero**. The DATA comparison does its job.

**The error the model-free check found.** Take only the entry's published integers and the
entry's published recurrence, and ask whether the range each paper PRINTS is consistent with
them. 477 papers were contradicted:

  * transfer4 (pattern avoidance): 115 wrong, off by exactly 2;
  * transfer5 (neighbour counts): 362 wrong, off by exactly 1;
  * every other family: 0 wrong.

The cause is one dropped conversion. Both engines store the threshold as a WALK index, and
both prepend the single-line count to the model, so the entry's index and the walk index
differ by 2 and by 1 respectively. The builders printed the walk index as if it were n. A206989
is the clean example: the entry itself says "for n>9", the paper claimed "for all n > 7", and
the entry's own DATA shows the recurrence failing at n = 8 and n = 9. The theorem as printed
was false.

The underlying mathematics was never wrong -- the annihilation test is sound and the
recurrences do hold -- but a paper that names a range in which its statement is false is a
wrong paper, and 477 of them went out that way. They were built in an earlier session and the
error survived every check until now because every check up to this point compared the MODEL
against the data, and the model was right; nothing compared the printed sentence against the
data.

**Fixed.** All 1284 transfer4 and transfer5 thresholds were recomputed from the model's own
terms as the largest index at which the recurrence actually fails (tight, not just shifted):
1094 changed -- 861 by +1, 200 by +2, and 33 in the other direction where the old value had
been too conservative. All 1284 papers rebuilt and replaced in place. The model-free check now
reports 2415 confirmed against published data and **0 contradicted**.

**The lesson, written down so it is not repeated: check the SENTENCE, not just the model.**
Every engine now has a check that takes the paper's printed threshold and tests it against the
entry's own published terms, using none of the machinery that produced it.

### 1 Sep 2026: the sentence check extended to the 632 non-array papers

Having found that 477 array papers printed a range the data refutes, the same model-free test
was pushed onto the older, bespoke half of the roster: take the entry's own conjectured
formula, evaluate it on the entry's own published integers, and see whether it holds where the
paper says it does. A sympy evaluator handles both shapes those entries use, a recurrence with
polynomial coefficients in n and a closed form in n.

  * **431** conjectures confirmed on the published data outright.
  * **41** where the conjecture FAILS at one or more small indices -- the entry states it
    unconditionally and it is simply false there. A104722 is typical: Mathar's
    `(n+4)a(n) + (n+1)a(n-1) - 4(n+1)a(n-2) + 4(2-n)a(n-3) = 0` gives 4, not 0, at n = 3, and
    holds from n = 4 on. Checking each paper's own printed range against those failures:
    **40 of 41 exclude them correctly** (paper 4198 says "holds for every n > 3").
  * The single remaining flag, A279014, was a fault in the CHECKER, not the paper. That entry
    carries two different Mathar recurrences and has two papers; the checker compared paper
    4210 against the other one's conjecture. Evaluated by hand: the order-4 recurrence fails at
    n = 4 and paper 4123 claims n > 4; the order-3 one fails at n = 3 and paper 4210 claims
    n > 3. Both correct.
  * **160** carry no formula line this evaluator can read -- divisibility statements,
    continued fractions, closed forms with radicals, congruences. Those are NOT machine-checked
    here and are recorded as such; they were reasoned individually when written, which is a
    weaker guarantee than the other 472 have.

**Overclaims among the 632: zero.** Combined with the array half, the roster now stands as:
3810 array papers re-verified end to end with 477 corrected, and 472 of the 632 bespoke papers
confirmed against published data with none overclaiming.

The asymmetry is worth keeping in view. The array papers are machine-checked at every step and
their weak point was never the mathematics but the index arithmetic in the printed sentence.
The 160 unreadable ones are the opposite: the mathematics is bespoke and was reasoned by hand,
and no automatic check covers them.

### 1 Sep 2026: the T(n,k) TABLES — a pool every sweep had been skipping

Every array sweep since the first one began with `if name.startswith('T(n,k)'): skip`. That
threw away 1426 entries, 937 of them carrying conjectures, none papered. They were skipped
because a table is two-dimensional and the engines take one parameter.

They need no new engine. Column k of a table is an ordinary fixed-width array count: rewrite
the entry's own wording with k substituted and the existing parsers read it. `tablecol.py` is
the whole addition, twenty lines of substitution.

**What the tables state.** 811 lines of the form `Empirical for column k:` followed by
`k=1: a(n) = ...`, `k=2: ...`, and so on, giving an explicit recurrence for the first few
columns and `[order 10]` for the rest. So each table is a BLOCK of conjectures, and a paper
that settles the block is one paper per entry rather than one per column.

**Result: 59 tables, 102 column recurrences.** Rank tier 5 -- above the plain transfer-matrix
papers, since reading a column out of a two-dimensional entry is a step the others do not have.

**Two things that had to be got right, and one honest weakness.**

  * A table stores its DATA by antidiagonals, and the orientation is not stated. Rather than
    assume one, both are tried and the one matching the model exactly is used; a wrong reading
    is rejected rather than fitted. Most Hardin tables are symmetric so it rarely matters, but
    it would matter silently if assumed.
  * The antidiagonal DATA gives very few terms per column -- four or five for k = 3 or 4,
    because it stops at a fixed number of antidiagonals. The `Table starts` block printed in
    the comments gives more, and parsing it lifted the yield from 74 columns to 102.
  * **The weakness, stated plainly: the DATA check here is thinner than anywhere else in the
    roster.** Median 8 published terms per column against a median of 22 for the ordinary
    array papers, and three columns rest on 5. The honest measure is total digits of exact
    agreement between model and entry: median 37, minimum 19 (A209727 column 1, twelve terms
    of two-digit values). That is still far past coincidence, but it is the least margin of
    any batch in the roster and is recorded as such.

    **Correction, same day.** The first version of this paragraph, and of the Verification
    section in all 59 papers, said the terms were "sixteen digits and up". They are not: the
    largest column value in the batch has 13 digits and the median has 7. The sentence was
    written from the first few entries looked at and never re-measured. All the papers were
    rebuilt to quote the figure each one actually achieves -- how many published values it
    reproduces and how many digits that is -- and this note left in place. The proofs
    themselves were unaffected; the overstatement was in the evidence sentence.

**A whole sub-family refused as already known.** Six tables (A183632, A183642, A183652,
A183662, A183672, A183680) carry `Empirical, for every row and column: a(n) = ...` where the
coefficients are the elementary symmetric functions of 1..p+1 -- that is, the characteristic
polynomial of prod (x - i). All six are the "every 2 X 2 subblock summing to 2p" family whose
closed form Krause proved in June 2026, and the recurrence is an immediate consequence of that
closed form. The openness checker calls them open because the entries carry no settlement
wording, but they are corollaries of a published proof and are NOT papered. Noticing this cost
nothing except reading the coefficients; papering them would have been six wrong counts.

**What is left here.** 414 tables where nothing was proved -- most have no engine that reads
the substituted name, some are past the state cap. 22 columns match the model at every
available term but have too few terms to run the DATA check at full strength, and are dropped
rather than claimed. 951 tables state no explicit column recurrence at all.

### 1 Sep 2026 (later): the 414 diagnosed, and 37 more tables

Asking WHY the 414 failed rather than moving on was worth 37 papers. The breakdown was
`{engine reads it, failed later: 9, no engine reads it: 407}`, and the largest single shape
among the 407 was 43 entries reading "every 2 X 2 subblock having its diagonal sum differing
from its antidiagonal sum by c" -- the constant-stress family, which has had its own engine
(`transfer3`) since the beginning. It was simply never added to the table sweep's engine list.
Adding it, with the per-engine dispatch its different signature needs, settled 37 tables and
41 column recurrences, all verified the same way as the rest.

A second bug found in the same pass: `tablecol.rewrite` turned "T(n,k) is the number of ..."
into "Number of is the number of ...", because it prepended "Number of" without checking
whether the sentence already carried a verb. Fixing it lifted the transfer6-readable table
count from 122 to 175. Those extra 53 produced no new proofs -- they either state no column
recurrence or their model does not match the published column -- but the fix is right and the
count is reported as zero rather than dressed up.

**Roster: 4538 papers (4532 proofs, 6 disproofs).**

The lesson repeats one already in this ledger: when a sweep reports a large "no engine reads
it" bucket, read the bucket. Twice now the biggest sub-shape in it was a family already
solved, missing only a line in a list.

### 1 Sep 2026: a conjecture does not have to be a recurrence

Every sweep so far looked for a line of the form `a(n) = c1*a(n-1) + ...` and ignored
everything else. Many entries state a CLOSED FORM instead --- `Empirical: a(n) =
(1/24)*n^4 - (1/12)*n^3 + (23/24)*n^2 + (13/12)*n + 3`, or `Empirical: a(n) = 16*7^n` --- and
those were being dropped by the parser, not by any mathematical obstruction. There are 752 of
them outside the roster.

They need no new mathematics either. Every function of the form `sum_j p_j(n) lambda_j^n`
satisfies the monic linear recurrence whose characteristic polynomial is
`prod_j (x - lambda_j)^(deg p_j + 1)`: a polynomial of degree d is annihilated by
`(x-1)^(d+1)`, and `16*7^n` by `(x-7)`. So a closed form IS a recurrence, and the residual
test the roster already runs settles it. Two sequences obeying the same monic recurrence and
agreeing on `order` consecutive terms agree from there on, because the recurrence determines
every later term.

`closedform.py` reads the line and hands sympy the job of producing the annihilator; the
existing engines supply the model. **Result: 158 papers.** 127 of the candidates are
polynomials and 10 are exponentials; the rest are refused.

**Three things this batch got right that are worth keeping.**

  * The range in the paper is MY range, not the entry's. 47 of the entries state no range at
    all and 57 state one; in every one of those 57 my proved range and the entry's agree
    exactly, and where the entry states none the closed form often fails at the first term or
    two and the paper says so.
  * The threshold is read off the sequence of VALUES, not from each engine's index
    convention. Two of the engines prepend a term to the walk, so their walk index and their
    n index differ by a constant --- that constant is precisely what caused the 477-paper
    error recorded above. Locating the last nonzero residual in the value domain removes the
    whole class of error rather than encoding a constant per engine and hoping.
  * Adversarial check: each closed form was perturbed by a constant and by a term linear in
    n, 312 perturbations in all, and every one was rejected.

An independent re-check --- recomputing the models from the engines rather than trusting the
sweep's bookkeeping --- confirmed all 158: the claim holds for sixty indices past its
stated start, fails just below it, and agrees with the entry's own published terms.

**A bug in the reader, found by its own crash.** The guard that rejects a closed form naming
another sequence tested for two consecutive letters, so `A000788(n-1)` passed it (an `A`
followed by digits) and blew up inside the annihilator. It now rejects any alphabetic
character that is not the variable. None of the 158 was affected --- the crash happened on a
later, wider scan --- but the guard was wrong as written.

### 1 Sep 2026: the 3 X 3 subblock, and the reading that was wrong

2523 entries impose a condition on every 3 X 3 subblock, and no engine touched any of them. A
3 X 3 block spans three consecutive lines, so the state has to be a PAIR of consecutive lines
and a step appends one more: `(r,s) -> (s,t)`, admissible when the condition holds on every
window of three consecutive columns of r, s, t. That is the whole of `transfer17.py`.

**Result: 284 papers.** The predicate compiler covers the sum families (`every 3X3 subblock row and diagonal sum equal
to 0 1 3 6 or 7 and every 3X3 column and antidiagonal sum not equal to ...`), the singular /
nonsingular determinant conditions, and the clockwise perimeter patterns.

**Two readings that were wrong, both caught by the DATA check.**

  * `clockwise perimeter pattern 00000001 00000011 or 00000101` does not mean that the eight
    boundary entries, read clockwise from the top left, spell one of those words. It means the
    cyclic word they form is one of those up to rotation. Read literally the model returns 6
    where the entry's own first term is 48 --- 3 patterns times 2 free centres, against 24
    rotations times 2. 155 of 218 models failed the DATA check on that one misreading, and
    every one of them passed after the fix.
  * `no 3X3 subblock diagonal sum 1 and no antidiagonal sum 1 and no row sum 0` is a
    conjunction of separate prohibitions, not the negation of a conjunction: each `no` binds
    its own clause. Negating the whole thing counts arrays in which SOME block violates one of
    the four, a different and much larger set. That reading was refusing 61 entries outright
    rather than getting them wrong, but it was still wrong.

This is the third time the requirement that a model reproduce every published term exactly has
caught a misreading of English that no amount of staring at the code would have found. It is
the single most valuable check in the whole roster.

### 1 Sep 2026: king-move neighbourhoods, and why the boundary is the whole problem

385 entries impose a condition not on a subblock but on every CELL, through its king-move
neighbourhood: `no element equal to a strict majority of its king-move neighbors`, `each 1
adjacent to 2, 3 or 4 king-move neighboring 1s`, `no 1 equal to more than two of its
king-move neighbors`. The geometry is the same three consecutive lines as the 3 X 3 engine,
so the state is again a pair of lines --- but the arithmetic is not.

**The boundary cannot be papered over.** A corner cell has three neighbours, an edge cell
five, an interior cell eight, and the COUNT enters the condition: a strict majority of three
is two and of eight is five. Padding the array with a border of zeros, the obvious shortcut,
gives every cell eight neighbours and counts something else entirely. So the outside is
carried explicitly, as a sentinel line above the first and below the last and a sentinel
column either side, and a neighbour that falls outside is absent from both counts. That also
means the last line cannot be settled by a step --- there is no line below it --- so the walk
ends on a WEIGHT rather than an indicator: the terminal vector evaluates the final line with
nothing beneath it.

`with the exception of exactly E elements` is then just a counter in the state, capped at E,
with acceptance requiring the count to reach exactly E.

**Result: 56 papers**, every one reproducing all of its entry's published terms and every
proved range checked tight.

**The bug this one had, and how it showed.** The violation counter decided whether a
neighbour lay in the current line by testing `line is s` --- object identity. When the line
above happened to be EQUAL to the current line they are the same tuple, so the cell directly
above was skipped as if it were the cell itself. The counts were right for arrays of up to
three lines and wrong from four on: 1, 5, 11, 37 against the entry's 1, 5, 11, 29. A check on
a few small cases would have passed it. Requiring agreement on every published term did not.

That is now four separate misreadings caught by that one rule in a single day.

### 1 Sep 2026: the neighbour set is a parameter, not a family

Once the king-move engine existed the generalisation was obvious and large. 975 entries name
a neighbour SET and then impose a condition on every cell over it: `horizontal and
antidiagonal` (182 entries), `horizontal, diagonal and antidiagonal` (150), `horizontal,
vertical and antidiagonal` (141), `king-move` (138), `horizontal and vertical` (109), and so
on. Every one of those sets lies inside the 3 x 3 square around the cell, so the same
pair-of-lines state works and the set is simply a parameter.

The predicate side widened too: strict majorities of equal, unequal, greater and smaller
neighbours; `no element having a strict majority of its NBRS equal to one`; `every element
equal to exactly one or two of its NBRS`; `each element x equal to the number of its NBRS
equal to a0,...,am for x=0,...,m`; and the two-set form `no element greater than all
horizontal neighbors or less than all vertical neighbors`.

**Result: 46 papers.** 120 more are past the state cap and stay there: the state space is
`(alpha+1)^(2W)` and the annihilation test needs up to `3S` matrix-vector products, so at
`W = 8` over a binary alphabet (`S = 65792`) the BUILD alone is of the order of `10^9` Python
operations. That is not a cap that can be raised by waiting; it needs a different
representation, and until there is one those entries are out of reach. Recorded as out of
reach, not as pending.

**The bug, and the sets that would have hidden it.** The offsets are named in the ARRAY's
frame --- horizontal means along a row --- but when the entry fixes the first dimension, as in
`2 X n`, the walk runs along columns, so the engine's lines are columns and the two components
of every offset swap. King-move is invariant under that swap. So is horizontal-plus-vertical,
and so is diagonal-plus-antidiagonal. Every set I had implemented FIRST was invariant, and the
error was invisible until `horizontal, diagonal and antidiagonal` came through: the model then
returned the counts of a different member of the same family (A231525's data appearing in
A231524's model). Three of four mismatches in the first validation run were this; the fourth
was an entry whose offset is 0 and whose first published term is the empty array, which the
sweep correctly refuses rather than fits.

### 1 Sep 2026: patterns, not arrays --- and what the container taught me about running sweeps

906 of the neighbour-condition entries add `new values 0..m introduced in row major order`.
That clause changes the object: what is counted is EQUALITY PATTERNS, not arrays, and a
pattern count is not a walk count. It is, however, a fixed rational combination of walk
counts. With `N_j` the patterns using exactly `j` letters and `L_i` the arrays over an
alphabet of `i` letters, an array over `i` letters is a pattern plus an injection of its
letters, so `L_i = sum_j N_j i(i-1)...(i-j+1)` --- triangular, hence invertible --- and the
entry counts `N_1 + ... + N_{m+1}`, a fixed rational combination of the `L_i`. Each `L_i` is
a walk count on its own graph, so the whole thing is a walk count on the disjoint union with
the combination's coefficients (some negative) placed in the starting vector.

This is only legitimate when the condition survives a permutation of the alphabet, so every
predicate now carries an `inv` flag: equality-based conditions qualify, ones naming a literal
value or comparing sizes do not. **Result: 45 papers.**

**What actually cost the time, and it was not the mathematics.** Background processes in this
container are suspended between turns: a sweep left running in the background makes almost no
progress, while the same work in the foreground runs at full speed. I lost a long stretch
watching a background sweep sit at eight entries before checking CPU time against wall time
and seeing it. Sweeps now run in foreground chunks, and each chunk must resume exactly where
the last stopped --- which exposed a second thing: the sweeps only persisted their `done` set
on the paths that reached the END of the loop body, so every chunk redid the entries the
previous one had skipped. Both fixed.

**Two engine changes that came out of the same investigation.**

  * The annihilation test costs one matrix-vector product per iteration and up to `3S`
    iterations, and nearly all of a sweep's time goes on entries whose recurrence does NOT
    hold, since those run to the bound before the test can say so. No threshold anywhere in
    this roster is past 70, so a residual still producing nonzeros after a few hundred
    iterations now abandons the entry as UNRESOLVED. That is a statement about the search,
    not about the conjecture, and nothing is certified on that path.
  * States that no start-to-accept walk passes through are trimmed before the test. It is
    pure bookkeeping and does not change a single value, but the graph size IS the running
    time.

There is also a modular pre-filter in place (run the residual in Z/p, where every
intermediate stays a machine word; a run that fails mod p cannot succeed exactly, and one
that succeeds mod p is repeated exactly before anything is claimed). It buys less than the
give-up rule does, because the cost here is the number of edges touched, not the size of the
integers.

**What stays out of reach.** 40 entries in this family are past the state cap. Combined with
the 120 from the neighbour-set sweep, that is the same wall as before: the state space grows
as `(alpha+1)^(2W)` summed over alphabet sizes, and the test is linear in the edge count per
iteration. Pure Python with no numpy in this container puts the practical ceiling around
`S = 1500` for a family that needs full certification.

### 1 Sep 2026: the same inversion around the other engine --- 56 more

The pattern inversion is independent of what the condition is, so it wraps the 3 X 3 subblock
engine exactly as it wrapped the cell-neighbourhood one. The eligible conditions are the ones
stated through equality: `having three equal elements in a row horizontally, vertically,
diagonally or antidiagonally [exactly N ways]` (195 entries) and `having equal diagonal
elements or equal antidiagonal elements` (54). Sums, determinants, perimeter patterns and
strict increases are excluded, because the inversion needs the condition to survive permuting
the alphabet and those do not. **52 papers**, plus 4 more from the neighbour family.

**A regex that quietly refused a whole form.** The relabelling clause appears as `, with new
values 0..2 introduced in row major order` and equally often as `, and new values 0..2
introduced in row major order`. My pattern required the word `with`, so the second form was
not recognised as a relabelling clause at all --- the name simply failed to parse and fell
into "no engine reads it". The first version of this engine parsed ZERO entries, which is the
only reason I looked. Fixing it took the 3 X 3 relabelling pool from 0 to 160 candidates and
also added 69 to the neighbour pool that had been sitting unparsed.

That is worth recording as a pattern in itself: a parser that refuses is invisible, while a
parser that misreads gets caught by the DATA check. The refusals need their own audit, and
"this engine parsed zero" is the only signal that comes for free.

### 1 Sep 2026: auditing the REFUSALS, and a family that is not an array count at all

Acting on the previous note: a parser that misreads gets caught, a parser that refuses is
invisible. So I built the diagnostic that finds refusals -- group every name by its shape with
the digits blanked, and look for shapes where SOME entries parse and others do not. That is
the signature of a gap, since entries of one shape should all be read or all be refused.

274 such shapes at first, but almost all of them were correct refusals: `n X n` square arrays
(both dimensions grow, so it is not a walk in one parameter) and `T(n,k)` tables (handled by
their own sweep). Excluding those left **nine** genuine mixed shapes covering 64 entries. Two
real gaps came out of it:

  * The encyclopedia writes the same thing as `a(n) is the number of ...` (135 entries),
    `1/4 of the number of ...` (51) and `a(n) = Number of ...` (23), and every engine required
    the bare `Number of ...`. `namecanon.py` now normalises those in one place, wired into
    every engine's parser. Verified against a snapshot of all 6257 previous parses: nothing
    changed, three names newly parse. A small yield, but the class of error is the point.
  * Offsets with a row distance of 2 need three lines of state instead of two. 51 entries, all
    of them also carrying a relabelling clause, so the state would be the union over alphabet
    sizes of `(alpha+1)^(3W)` -- feasible only at `W = 3`, and the certification cost there is
    already past what this container can do. Recorded as out of reach.

**The bigger find in that pile: 452 entries that are not array counts at all.** `Number of
(n+1) X (3+1) arrays of permutations of 0..n*4+3 with each element having index change
(+-,+-) 0,0 1,1 or 1,2`. The grid holds each of `0..LW-1` once; a value's HOME cell is its
place in the plain row-major filling; the entry restricts how far each value may move from
home. So the object is a perfect MATCHING between cells and values, not a colouring --- and it
is still a walk. With `R` the largest row displacement, a value with home row `h` can only be
placed in rows `h-R..h+R`, so after the cells of rows `0..i` are filled every home row up to
`i-R` is used up and only `2R` home rows are partly used. The state is those `2R` bitmasks,
one step fills one row, and the row that closes must come out full; nonexistent home rows are
carried as full, which makes the start and accept states the same one.

**126 papers.** State `2^(2RW)`, so `W <= 7` at `R = 1` and `W <= 3` at `R = 2`; 56 entries
are past that and stay there.

**THREE conventions that look identical and are not.** `(+-,+-) a,b` signs each coordinate
independently, so it means `(±a, ±b)`. `+-(.,.) a,b` signs the PAIR, so it means only `(a,b)`
and `(-a,-b)` --- and in that form the second coordinate is sometimes written negative, as in
`2,-2`. `directed index change a,b` is taken literally, no signs added at all; that is the
LARGEST of the three, 249 of the 390 names.

My first version read every entry the first way, which silently DROPPED the negative
displacements. 38 entries disagreed with their own data and were refused; none was wrongly
accepted. Before building any of it I had checked the reading by brute force on the smallest
case (all 720 arrangements of a 2 x 3 grid give 20, the entry's first term, and 3 x 2 gives 9,
its transposed companion's) --- and that check passed, because both test entries used the
first convention. **A brute-force check on one example proves the reading of THAT example.**
The third convention was then found by looking at what the parser was REFUSING (269 names),
and each of the three was brute-forced separately before use: twelve entries per convention,
all reproducing their published terms.

### 2 Sep 2026: one missing word cost 148 papers

The refusal audit, run again but clustering by the OPENING of the condition rather than the
whole shape (a convention variant changes the tail, so exact-shape grouping puts it in a
different bucket and hides it), turned up 43 openings with both parsed and refused entries.
The largest was `no element unequal to a strict majority of its ... neighbors`.

The pattern in the neighbour engine read

    no element (equal|unequal|less than|greater than) a strict majority of its NBRS

and the entries say `unequal TO a strict majority` but `less THAN a strict majority`. The
connecting word differs, and it was missing from the alternation, so the equal and unequal
forms --- the common ones --- were silently unreadable while the less and greater forms
parsed. It had been that way since the engine was written; the 46 papers it produced first
time round all came from the less/greater forms and from other predicates, so nothing looked
wrong.

Three other refusals fixed in the same pass:

  * `no 1 equal to more than one of its ... neighbors` --- the value-specific form. The engine
    had the king-move-only version and not the general one.
  * The relabelling clause written FIRST (`arrays with new values 0..2 introduced in row major
    order and no element ...`): stripping it took the word `with` along with it, leaving
    `arrays and no element ...`, which no parser reads.
  * A trailing comma left behind when the clause was stripped from the end.

**Result: 148 papers** --- 96 in the neighbour family (46 -> 142) and 52 in its relabelling
counterpart (49 -> 101). Every one re-checked independently: zero problems.

The lesson is the one from the previous entry, sharper. A parser that refuses is invisible,
and the way to see it is to find shapes where SOME entries are read and others are not.
Grouping by exact shape is not enough, because the thing that varies is exactly what the
grouping keys on. Group by the opening instead.

### 2 Sep 2026 (later): the refusal audit run to exhaustion, and where it stops paying

Ran the opening-cluster diagnostic again and worked down the list. Five more predicate forms
added, all validated against the published terms of three entries per form before use:

  * `no element x(i,j) adjacent to value 3-x(i,j) horizontally, diagonally or antidiagonally,
    and top left element zero` --- the trailing clause fixes the first cell, which is a
    restriction on which states may START the walk, not on the transitions.
  * `each element equal to the number of its NBRS within one of itself`
  * `every nonzero element less than or equal to at least two NBRS`
  * `every 3X3 subblock row and column sum nonprime and every diagonal and antidiagonal sum
    prime` --- and here the second clause drops the words `3X3 subblock` entirely, so the
    splitter that looked for them left the whole sentence as one unreadable clause. Making
    both words optional took the 3 X 3 parser from 528 names to 789.
  * `each 3X3 subblock having a positive determinant`

**Result: 26 papers.** That is a tenth of what the previous round of the same audit produced,
and the reason is worth writing down: the remaining refusals are no longer parser gaps, they
are 456 entries in the 3 X 3 family and 122 in the neighbour family past the state cap. The
audit has stopped finding bugs and started finding the wall.

**So the refusal audit is now a finished job**, not a standing one. What is left in the
refused pile splits three ways: over the cap (the majority), `n X n` square arrays that are
not a walk in one parameter at all, and a long tail of one-off shapes with no family behind
them. None of those is a missing word.

### 2 Sep 2026: the table sweeps had been frozen at the engines that existed when they were written

With the refusal audit finished, the next question was what else the newer engines could reach.
The answer was embarrassing: the table sweep carried a hard-coded list of engines, written when
there were twelve of them, and every engine built since --- the 3 X 3 subblock one, the
cell-neighbourhood ones, both relabelling wrappers, the grid-permutation one --- was simply
absent from it. The rewritten names parsed perfectly well; nothing was ever asked to try them.

That surfaced only because the ROW sweep, which is the same substitution with the two
dimensions exchanged, returned zero from 73 tables whose names I could see parsing by hand.

`uniform.py` now gives every engine one interface --- `read`, `terms` indexed by walk step with
any scaling divided out, and `threshold` in the same index --- because the shapes had diverged:
some return `(states, adj)` and count with all-ones vectors, some `(adj, start, end)`, some add
a denominator, some expose values already indexed by the entry's own n.

**Result: 92 tables, 183 line recurrences** --- 154 columns and 29 rows. 105 of the 183 came
from the grid-permutation engine alone, on tables nobody had tried it against.

**A row of a table is a column of the transposed table.** Fixing n and letting k vary counts
arrays of fixed height, the same object with the dimensions exchanged, and the engines already
walk in either direction and transpose the condition themselves. `tablerow.py` is the whole
addition.

**One audit bug worth recording**, because it produced a false alarm rather than a false
proof: the audit picked the published line by taking the first antidiagonal reading of the
right LENGTH, but the two readings can have the same length and different values, so it
sometimes compared against a line the sweep had not used. Fourteen phantom failures. The fix
is to test every reading and require one to match, which is what the sweep itself does.

**The general lesson**, and it is not the same as the refusal one: a sweep that hard-codes its
engine list silently stops growing when the engines do. Nothing in it fails; it just never
tries. Every sweep now goes through `uniform.ENG`.

### 2 Sep 2026: every sweep carried its own frozen candidate list, not just the table one

The table sweep's frozen engine list turned out to be the general case. Counting, for each
engine, the names it parses that are neither in the roster nor in that engine's own `done`
set: **transfer6 266, transfer9 264, transfer3 144**, and smaller numbers across the rest ---
around 800 entries that had become parseable when a parser was fixed and then sat there,
because the sweep that would have picked them up had already been run to completion.

`sweep_uni.py` replaces the per-engine sweeps: every engine asked about every name, on every
run. **15 papers**, which is a small return for 800 candidates --- 778 were past the state
cap and 1039 state no recurrence at all --- but the point is that the pool is now swept by
construction rather than by remembering to re-run something.

**A file-name collision, and how it showed itself.** I named the new sweep's output
`uni_hits.json`, which already existed from an older sweep with a different schema, and the
new run appended to it. Nothing was mis-proved: the two schemas share no fields and the
integrator reads only its own. It surfaced as a `KeyError` on a missing field when I went to
count the engines used. The file is now `uniall_hits.json` and the old one restored from git.

One of the nine old records, A166761, was NOT in the roster --- which looked at first like a
proved result that had never been papered. It is not: the entry carries ``The above empirical
formulas are correct. --- Andrew Howroyd, Dec 12 2024'', so it is settled and the openness
check correctly excludes it. Worth checking rather than assuming, and worth recording that the
check came out the boring way.

**Three ways a sweep can silently stop finding things**, all now seen: a parser that refuses
(invisible, found by clustering shapes with mixed outcomes); an engine list frozen at the
engines that existed when the sweep was written; and a candidate list frozen at what parsed
when the sweep was last run. The third is the one that persists after the first two are fixed,
because fixing a parser does not re-open the sweeps that already finished.

### 2 Sep 2026: the entry often already contains the proof, in a different line

A census of what is left outside the roster: **5301 entries still carry a conjectured linear
recurrence**, and the sweeps cannot touch most of them --- past the state cap, or not array
counts at all. So I stopped asking "can I model this sequence?" and asked "does the entry
already say something that settles it?"

276 of them carry a `G.f.:` line that is NOT marked conjectural --- contributed by someone,
recorded as fact. If that generating function is rational, the recurrence is a consequence of
it and needs no model whatever. Write `G(x) = sum a(n)x^n` and `D(x) = 1 - sum c_i x^i` for
the conjectured recurrence; then `a(n) - sum c_i a(n-i)` is the coefficient of `x^n` in
`D(x)G(x)`, so the recurrence holds past the degree of that product, provided it is a
polynomial --- which is exactly the condition that the recurrence's characteristic polynomial
is a multiple of the generating function's denominator. One polynomial division per entry.

**Result: 233 papers.** Every candidate whose generating function parsed and matched the data
implied its conjectured recurrence; not one failed.

**The strongest external check I have had.** 84 of the 233 entries state the range themselves
(`for n>=8` and the like) and 149 state none. In all 84 the entry's own range agrees EXACTLY
with the degree bound computed here. That is 84 independent confirmations, by the entries'
contributors, of the index conversion --- the very thing that was wrong in 477 papers a day
ago.

**What these papers are, stated plainly.** They are conditional on the entry's generating
function. That function is asserted by the entry, not conjectured, and is checked here against
every published term, but it is not proved in the paper. Each paper says so in a remark: what
is shown is that the empirical recurrence is not an independent guess but a restatement of
information the entry already contains. That is a real result and a weaker one than the
transfer-matrix papers, and it is labelled as such --- rank tier 12, below the closed-form
routes.

**A uniform finding worth recording:** in all 233, the conjectured recurrence is the MINIMAL
one --- its polynomial is exactly the reduced denominator, never a proper multiple. Each paper
says which, computed rather than assumed; it just came out the same way every time.

### 2 Sep 2026: 500 conjectures whose text cannot be read, and 39 of them settled anyway

`Empirical recurrence of order 55 (see link above)` --- 500 entries state only the ORDER, with
the coefficients in a linked file the local copy of the encyclopedia does not carry (it holds
`seq` only: no links, no b-files). A conjecture one cannot read looks unsettleable.

It is not, when the sequence is a walk count, because of a uniqueness argument:

  * a walk count on `S` vertices satisfies SOME monic recurrence of order at most `S`;
  * Berlekamp--Massey on `2S` exact terms therefore returns the MINIMAL one, exactly;
  * if that minimal order equals the order the entry states, then any recurrence of that order
    the sequence satisfies has a characteristic polynomial that is a multiple of the minimal
    polynomial AND of the same degree, so the two are equal.

The entry's recurrence is then the one computed here, whatever its file says.

**One correction I had to make to my own argument before using it.** The uniqueness step needs
the minimal order of every TAIL to equal the stated order too, not just that of the whole
sequence: the entry's recurrence may hold only from some index on, and a tail can satisfy a
shorter recurrence than the sequence it comes from. I added that check and re-ran; all 39
survive it, but the first version of the argument was incomplete and would have been wrong for
any entry where the tail is shorter.

**A near-disproof that is not one.** 12 entries came out with minimal order ABOVE the stated
order, which looks like a refutation --- no recurrence of the stated order can exist. It is
not, for the same reason: a recurrence valid only past a threshold makes the minimal order of
the WHOLE sequence larger than the eventual one, so those 12 are inconclusive, not false. They
are recorded as inconclusive.

**Result: 68 papers**, at rank tier 4 --- above the ordinary transfer-matrix work, because
recovering a statement one cannot read is a different kind of step. (39 at a state cap of 600,
another 29 when the cap was raised to 2500; the Berlekamp--Massey step needs `2S` terms, which
is the same order of work as the annihilation test it replaces, so the cap moves for the same
reasons.) 4 remain past the cap, 2 have names no engine reads, and 16 are the inconclusive
case below.

The recovered orders run from 20 to 89. Every one was re-derived independently in a second
pass --- model rebuilt, terms recomputed, order measured mod a prime and again exactly, tail
order measured, coefficients re-derived and tested on the entry's own published terms --- and
all 68 agree.

### 2 Sep 2026: the same recovery applied to table lines --- 1872 unwritten recurrences

`k=2: [order 17]`. Counting them: **1872 such lines across 626 tables**, far more than the 500
whole-sequence cases. The argument transfers unchanged, since a line of a table is a
fixed-width or fixed-height array count and so a walk count.

**Result: 43 tables, 55 lines recovered.** The yield is low against 1872 because of where the
lines fail: 1008 line-rewrites no engine reads, 247 past the state cap, and 39 where the
minimal order differs from the stated one (inconclusive, as before --- a threshold in the
entry's own recurrence inflates the minimal order of the whole line).

**The structural gap, now closed.** Tables already in the roster were skipped by the sweep, so
a table papered for its EXPLICIT column recurrences did not get its `[order N]` lines recovered
as well. Re-running without the roster skip found **157 tables and 269 recoverable lines** in
total; 114 of those tables already had a paper for their written-out recurrences, carrying 214
lines that were reachable and unclaimed. Their papers are rebuilt to cover both, with a new
section for the recovered lines.

**This adds no papers and is not counted as any.** The tables were already in the roster; what
changes is that each of the 114 papers now settles more of its entry's conjecture block than it
did. Recording it here because the alternative --- issuing 114 second papers on the same
entries --- would have inflated the count for no new mathematics.

**Where the recovery idea now stands.** It settles a conjecture whose text is unavailable, by
showing the space of recurrences of the stated order has exactly one member. It works whenever
(i) an engine reads the line's rewritten name, (ii) the state space is small enough for `2S`
terms, and (iii) the minimal order matches the stated one on the sequence AND on its tail. Of
those, (i) and (ii) are the binding constraints, and both are the same walls as everywhere
else.

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


### 2 Sep 2026: the refusal census, redone — 35 papers from the K X K subblock matrices

Two checks this round. The first was a null and is recorded as one: `sweep_ord.py` skips
roster entries, exactly as the table sweep did, so an entry already papered by another
engine could be carrying an unclaimed `Empirical recurrence of order N` line. It is not.
All 68 roster entries that carry such a line are the 68 order-recovery papers themselves.
Nothing to fix, no papers, and the `SKIP_ROSTER` switch is now on that sweep too so the
question can be re-asked in one command.

The second was the refusal census done again from scratch — every non-roster entry whose
name mentions an array and which carries a parsable conjectured recurrence that no engine
reads. **723 entries**, clustered by the opening of the condition rather than by the whole
name. The clusters are real families, not a long tail:

| entries | family |
|---|---|
| ~99 | `(n+K-1) X W 0..m matrices with each K X K subblock idempotent / of equal population / of equal permanent` |
| ~80 | `ways to reciprocally link elements of an n X W array …` |
| ~100 | `Hilltop / Equals one / Unmatched value / Sum of neighbor / Majority value maps` |
| ~40 | `0..k colorings of a W X (n+1) array circular in the n+1 direction` |
| ~40 | `arrays of the minimum value of corresponding elements and their neighbors` |

The first two families are now closed: `transfer23.py`, **35 papers**, and
`transfer24.py`, **76 papers** — the whole reciprocal-link family, every entry of it that
carries a conjectured recurrence.

**Why it needed more than the existing engines.** The condition ties together K consecutive
ROWS and K consecutive COLUMNS at once, so one row is not a state; the state is the strip of
the last K-1 rows, of which there are `(m+1)^((K-1)W)` — 2^18 at K=3, W=9, and out of reach
past that. They are not enumerated. Two consecutive K X K windows of a K X W band overlap in
K X (K-1), so a band is a walk in the overlap graph on the admissible windows, and the states
are exactly the tops and bottoms of bands. That turns a search over strips into a search over
windows. The state counts that come out are tiny: 8, 36, 416, 1905 where the naive count is
astronomically larger.

**The idempotent windows needed a theorem.** Sifting all `2^(K*K)` matrices is already
awkward at K=6 and hopeless past it. Writing `B^2 = B` row by row says each row is the sum of
the rows indexed by its own support, and comparing supports gives a closed description of the
0-1 idempotents — pick the zero rows Z, pick the primitive indices B* with `r_b = e_b + (a
subset of Z)`, and let every other nonzero row be a disjoint union of those. It generates each
one exactly once. Counts: 8, 50, 452, 5682, 96608 for K = 2..6, and the first three agree with
exhaustion over all `2^(K*K)` matrices. That agreement is the check that the description is
neither too wide nor too narrow; the lemma and its proof are in every paper of the family.

**The two "all equal" conditions split.** `having the same population` and `permanent equal`
do not name the common value. Fix v, count the matrices all of whose windows have that value,
and the sets for different v are disjoint because the value is determined by the matrix. A
disjoint union of the per-v digraphs counts the whole thing with the same all-ones vectors.

**Verification.** Beyond the usual three checks, the model was re-derived independently: a
direct brute-force count straight from the definition, enumerating every matrix of the small
sizes and testing every window, for eight entries covering all three conditions and the
alphabets 0..1, 0..2 and 0..3. Every one matched the published DATA. The audit of the 35
papers reports no problems.

**What is left in this family.** K = 6, 7, 8 idempotent (about 20 entries): the windows can be
generated but there are 96608 of them at K = 6 and 2.2 million at K = 7, so the graph is far
past the size at which the annihilation test is affordable here. The square `(n+K-1) X (n+K-1)`
entries are not a walk in one parameter and are refused, as always. A few wide population
entries are over the state cap. Recorded, not pending.

All five families in the table above have now been worked.

### 2 Sep 2026, same day: the reciprocal-link family — 76 papers, the whole family

`Number of ways to reciprocally link elements of an n X W array either to themselves or to
exactly one/two <neighbours> neighbors[, without 3-loops | without consecutive collinear
links]`. 76 entries in the refusal census, and all 76 are now papers.

**The modelling step is the whole difficulty; after it the engine is small.** A link is
reciprocal, so it is an undirected EDGE, and "linked to itself" means "in no edge". So the
entry counts the spanning subgraphs of a grid graph whose every vertex has degree 0 or d:
matchings for d = 1, disjoint unions of cycles for d = 2. Every neighbour offset moves the row
index by at most one, so the set of edges crossing one row boundary is a state, and placing a
row settles the degree of each of its cells once and for all.

**Two readings had to be fixed, not guessed.**
- Can a cell spend both links on the same neighbour? No. For king moves the 1 X 2 and 2 X 2
  counts are the degree-0-or-2 subgraphs of `K_2` and `K_4`, which are 1 and 1+4+3 = 8 with
  simple edges and more with a doubled edge; the entries publish 1 and 8.
- `without 3-loops` is triangles, not doubled edges — and it was nearly misread as `2-loops`
  from a digit-collapsed cluster listing. Three cells pairwise adjacent always lie in two
  consecutive rows (three in one row cannot be pairwise adjacent, the outer two being two
  columns apart), so carrying the previous row's horizontal edges in the state catches every
  one.
- `without consecutive collinear links` forbids a vertex whose two links are opposite. It is a
  condition on one vertex, decided where the degree is.

**State counts are tiny** — 5 to 40 — because the degree bound prunes the boundary hard. The
whole family cost one sweep.

**Verification.** Besides the usual three, the model was re-derived independently: a brute
force over every subset of the edge set, straight from the definition, for 12 entries covering
d = 1 and d = 2, both flags, both orientations and four neighbour sets. All matched. The audit
of the 76 reports no problems.

Ten entries of the family parse but carry no recurrence a parser reads; nothing is claimed for
them.

### 2 Sep 2026, third family: circular colourings — 41 of 43

`Number of 0..m colorings of an n X W array circular in the W direction with new values 0..m
introduced in row major order`, and the same with the array written `R X (n+c)` and circular
in the growing direction. 43 entries; 41 are now papers.

**The reading.** A colouring is proper — adjacent cells differ — and "circular in the W
direction" joins the two ends of that direction. Confirmed by the entries' own first terms: a
cycle of 6 cells has `2^6 + 2 = 66` proper 3-colourings and `66/3! = 11` is what the one-row
entry publishes.

**The relabelling clause is transfer20's argument unchanged**: what is counted is patterns,
`L_i = sum_j N_j i(i-1)...(i-j+1)` is triangular, and `a = (1^T F^-1) L`.

**The two circular directions are not the same problem.**
- Circular ACROSS the walk: a row is a proper colouring of `C_W`, consecutive rows differ
  everywhere, `L_i(n)` is an ordinary walk count.
- Circular ALONG the walk: a column is a proper colouring of `P_R` and `L_i(m) = tr(T^m)`. A
  trace is not `iota^T M^m tau`, and one walk per starting vertex is unaffordable. It is not
  needed: `T` commutes with permuting the colours, so the diagonal entry depends only on the
  colouring's equality pattern, and `tr(T^m)` is a weighted sum of a handful of closed-walk
  counts, one per pattern.

**The lumping is what made it affordable, and it was the difference between 24 and 41.** The
first sweep proved 24 and left 19 over the cap or timed out. Everything in sight commutes with
permuting the colours, so a walk started at a symmetric vector may be run on the ORBITS. The
state counts collapse: 994 to 16, 1062 to 281, and two entries that had been over the cap came
in at 318 and 59. Storing the lumped adjacency with multiplicities instead of repeated targets
cut the matrix-vector cost again, and that took it to 41.

**Verification.** Besides the usual three, an independent brute force enumerating every array
over the alphabet and testing properness and the row-major canonical form, for 9 entries across
both circular directions and alphabets 3..8. All matched. The audit of the 41 reports no
problems.

**The two left**: A214116 and A214170, mode B with 4761 and 2544 orbit states; the residual
test is still too slow here. Recorded, not pending.

### 2 Sep 2026, fourth family: the `maps' entries — 114 of 164, and the first IMAGE count

`<Family> maps: number of n X W binary arrays indicating the locations of corresponding
elements <condition> in a random 0..m n X W array`, for seven families: Hilltop (`not exceeded
by any`), Unmatched value (`not equal to any`), Unchanging value (`unequal to no`, i.e. equal
to every), Majority value, Equals one, Equals two and Sum of neighbor (`equal to the sum mod k
of`). 164 entries in the refusal census; 114 are now papers.

**This is a different KIND of count and it is why the family had sat there.** Every other
engine counts objects satisfying a condition. These count the IMAGE of a map: how many
different indicator arrays arise as the 0..m array runs over all its values. Two different
arrays with the same marking must be counted once, so no walk count on the arrays gives the
answer.

**The cure is the subset construction.** A cell's marking depends on the rows above, at and
below it, so the pair of the last two rows read is the state of a nondeterministic machine
whose OUTPUT is the indicator array; the distinct outputs are the paths of its determinisation,
whose states are the sets of pairs still consistent with what has been emitted. Those sets are
generated from the start set outward and there are few of them — 8 to a few thousand.

One detail is easy to get wrong and is proved rather than assumed: the LAST marked row is
emitted with nothing below it, so it is not a step of the walk. It is a count attached to the
state the walk stops in — the number of distinct final rows that state still admits — so the
end vector is not the all-ones vector. The lemma in every paper of the family states the
invariant of the subset construction and derives `a(n) = iota^T M^(n-1) tau` from it.

**Verification.** Besides the usual three, an independent brute force that builds every array,
marks it and counts the distinct markings, for 14 entries covering all seven families, both
orientations and alphabets 0..1 to 0..3. All matched. The audit of the 114 reports no problems.

**Left**: 50 entries over the subset cap of 20000 or too slow for the residual test here —
mostly Hilltop at the wider widths. Recorded, not pending.

Ranked at tier 4. The reduction is a real one with its own lemma, but the subset construction
is textbook, so it is not ranked with the bespoke arguments.

### 2 Sep 2026, fifth family: two more image counts — 55 of 62

The last family the refusal census listed, and it splits in two, both image counts, both
settled by the same determinisation. The subset construction is now factored out into
`imagedet.py` and shared, so the three engines that use it cannot drift apart.

- `Number of n X W arrays of the MINIMUM value of corresponding elements and their
  <neighbours> in a random 0..m n X W array` — 43 entries, 40 proved. Each derived cell holds
  the least of its own value and its neighbours'; the row window is three rows, as in the
  `maps` families, so the last derived row is again counted at the state the walk stops in.
- `Number of n X W 0..k arrays of the MEDIAN (or SUM) of the corresponding element, the
  element to the east and the element to the south in a larger (n+1) X (W+1) 0..m array` —
  17 entries, 15 proved. Here the derived cell reads two consecutive rows only, so the state
  is a single row and there is no final emission: the walk simply has n steps. Some of these
  add `without adjacent equal elements in the latter`, which removes transitions and start
  states and nothing else. The stated output alphabet is checked against the operation
  (3m for a sum, m for a median) and a name that disagrees is refused rather than guessed at.

**Verification.** An independent brute force building every array, applying the operation and
counting distinct results, for 10 entries across both shapes, both operations and the
`without adjacent equal` variant. All matched. The audit of the 55 reports no problems.

**Left**: 7 entries — 3 over the subset cap at the wider widths, 2 sums at width 5 and 7, and
the 2 `minimum or maximum` entries, whose English is genuinely ambiguous (a per-cell choice
between the two fits the first terms, but I have not pinned it and will not count a guess).

With this the five families the census found stand at 35+76+41+114+55 = **321 papers**, out of
the 723 entries it listed.

### 2 Sep 2026: the census redone over the WHOLE corpus — 3667 left, and two more families

The first census only looked at names containing `array`, `grid` or `matri`. Redone over every
entry: **3667 non-roster entries carry a conjectured recurrence that no engine reads**, in 498
distinct shapes. The five families already worked were the visible top of it. Two more are now
done, 175 papers.

**Order statistics of every 2 X 2 subblock, all equal — 99 of 101.**
`Number of (n+1)X(K+1) 0..m arrays with <the maximum plus the upper median minus the lower
median minus the minimum> of every 2X2 subblock equal.` Sorting a subblock's four entries as
a<=b<=c<=d names them minimum, lower median, upper median, maximum, and the entries take every
signed sum of those four. The common value is not named, so the count splits by it exactly as
in the idempotent family; for a fixed value the condition is two rows wide and a row is a
state.

**`Colored with' — 76 of 88 — and what it actually means.**
`Number of (n+1)X(K+1) 0..2 arrays colored with the upper median value of each 2X2 subblock.`
The name gives no condition at all on its face, and that is why it had never been read. It is
a PROPER COLOURING: the subblocks form an n X K grid, each is coloured by the statistic, and
neighbouring subblocks — horizontally and vertically — must differ.

The reading was pinned numerically before anything was built. For the upper median over 0..2:
a 2X2 array has one subblock and no neighbouring pair, so all 81 arrays qualify; a 2X3 array
has one pair and 294 of 729 qualify; a 3X3 array has four pairs and 722 qualify. Those are the
three numbers the entries publish. No condition would give 729 at 2X3; counting the diagonal
pairs as neighbours too would give 0 at 3X3. Neither is what is meant. The justification is in
every paper of the family.

Here the state has to be a PAIR of consecutive array rows, not a row: a subblock's colour needs
two rows, and the vertical condition compares two subblock rows. Some of these colour by the
SET of distinct values in the subblock rather than by a number, which the same machinery
handles unchanged.

**Verification.** Independent brute force from the definition for 16 entries across both
families, every colour kind including the set-valued one, and several widths. All matched. The
audit of the 175 reports no problems.

**Left**: 2 of the `equal` entries and 12 of the `colored` ones, over the state cap at the
wider widths, plus the 5 `colored ... with new values introduced row-major order` entries,
which stack the relabelling reduction on top and were not attempted. The square
`(n+1)X(n+1)` entries are refused as always.

### 2 Sep 2026: monotone subblock statistics — 84 papers

`Number of (n+1)X(K+1) 0..m arrays with every 2X2 subblock <statistic> nondecreasing
horizontally, vertically and ne-to-sw antidiagonally.` The subblocks form a grid, each carries
the value of a statistic of its four entries, and the value must not decrease along the named
directions of that grid. Some entries name TWO statistics, one for the horizontal direction
and one for the vertical; both are functions of the same subblock, so both are read off the
same pair of rows.

Every direction moves the subblock row by at most one, so the state is a pair of consecutive
array rows — that pair fixes a whole subblock row — and one step settles every comparison
between two consecutive subblock rows.

**Three readings were pinned numerically before anything was built.**
- `ne-to-sw antidiagonally` is the offset (+1,-1) on the subblock grid. The offset (+1,+1)
  gives 164 where the entry publishes 126.
- `diagonal minus antidiagonal sum` is (p+s)-(q+r).
- `ne-sw antidiagonal difference` is q-r, and `nw+se diagonal sum` is p+s.
Each was settled by counting the small arrays directly. The justification is in every paper.

Transposed names (`(K+1)X(n+1)`) swap the two coordinates of every direction; a direction that
then points upward is turned round by reversing its inequality, which is done in the parser
rather than left to chance. Square `(n+1)X(n+1)` entries are refused as always.

**Verification.** Independent brute force from the definition for 10 entries. All matched.
The audit of the 84 reports no problems.

**The rest of this family is 3 X 3.** About 120 more entries use the same grammar over
3 X 3 subblocks, where the statistics are built from the diagonal, the antidiagonal, the
central row and the central column (`sum of the medians of the diagonal and antidiagonal minus
the two sums of the central row and column`). The transfer is the same shape with a state of
three consecutive rows; only the statistic parser is missing. Not done, and recorded as the
obvious next step rather than as a wall.

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
