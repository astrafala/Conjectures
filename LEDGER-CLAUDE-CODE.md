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

Last updated 30 Aug 2026. Roster: **456 papers**, files `1-PROOF.pdf` … `456-PROOF.pdf`, **numbered by how hard the result was**: 1 is the hardest.
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
| 28 | another recurrence posted |
| 19 | a sum without binomials |
| 5 | an e.g.f. |
| 26 | transcendental or an infinite sum |
| 24 | should have worked -- all 24 turned out to be already settled |
| 20 | parses but does not match the published terms |
| 10 | a continued fraction |
| 13 | the residual test crashed |
| 29 | DISPROOF | A000040 | gcd-sum evaluation | Mathar |
| 30 | DISPROOF | A008365 | gcd-sum evaluation | Mathar |
| 31 | PROOF | A000670 | gcd-sum evaluation | Mathar |
| 32 | PROOF | A002050 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 33 | PROOF | A004123 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 34 | PROOF | A006531 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 35 | PROOF | A052895 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 36 | PROOF | A064618 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 37 | PROOF | A080253 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 38 | PROOF | A162314 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 39 | PROOF | A167137 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 40 | PROOF | A259533 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 41 | PROOF | A301921 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 42 | PROOF | A305550 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 43 | PROOF | A306082 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 44 | PROOF | A316142 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 45 | PROOF | A316143 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 46 | PROOF | A316144 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 47 | PROOF | A320352 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 48 | PROOF | A354242 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 49 | PROOF | A354253 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 50 | PROOF | A355409 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 51 | DISPROOF | A098660 | eventual periodicity mod m, period dividing phi(m) | Mathar |
| 52 | DISPROOF | A103769 | conjectured P-recursive recurrence | Mathar |
| 53 | DISPROOF | A119967 | conjectured P-recursive recurrence | Mathar |
| 54 | DISPROOF | A129366 | conjectured P-recursive recurrence | Mathar |
| 55 | PROOF | A000180 | conjectured P-recursive recurrence | Mathar |
| 56 | PROOF | A127905 | conjectured P-recursive recurrence | Mathar |
| 57 | PROOF | A045742 | conjectured P-recursive recurrence | Mathar |
| 58 | PROOF | A243585 | conjectured P-recursive recurrence | Mathar |
| 59 | PROOF | A026005 | conjectured P-recursive recurrence | Mathar |
| 60 | PROOF | A359643 | conjectured P-recursive recurrence | Mathar |
| 61 | PROOF | A156894 | conjectured P-recursive recurrence | Mathar |
| 62 | PROOF | A156894 | conjectured P-recursive recurrence | Mathar |
| 63 | PROOF | A371753 | conjectured P-recursive recurrence | Mathar |
| 64 | PROOF | A226751 | conjectured P-recursive recurrence | Mathar |
| 65 | PROOF | A386830 | conjectured P-recursive recurrence | Mathar |
| 66 | PROOF | A243764 | conjectured P-recursive recurrence | Mathar |
| 67 | PROOF | A243760 | conjectured P-recursive recurrence | Mathar |
| 68 | PROOF | A285195 | conjectured P-recursive recurrence | Mathar |
| 69 | PROOF | A243814 | conjectured P-recursive recurrence | Mathar |
| 70 | PROOF | A055392 | conjectured P-recursive recurrence | Mathar |
| 71 | PROOF | A308726 | conjectured P-recursive recurrence | Mathar |
| 72 | PROOF | A243022 | conjectured P-recursive recurrence | Mathar |
| 73 | PROOF | A168506 | conjectured P-recursive recurrence | Mathar |
| 74 | PROOF | A242566 | conjectured P-recursive recurrence | Mathar |
| 75 | PROOF | A270530 | conjectured P-recursive recurrence | Mathar |
| 76 | PROOF | A127632 | conjectured P-recursive recurrence | Mathar |
| 77 | PROOF | A130655 | conjectured P-recursive recurrence | Mathar |
| 78 | PROOF | A166135 | conjectured P-recursive recurrence | Mathar |
| 79 | PROOF | A212696 | conjectured P-recursive recurrence | Mathar |
| 80 | PROOF | A261196 | conjectured P-recursive recurrence | Mathar |
| 81 | PROOF | A270530 | conjectured P-recursive recurrence | Mathar |
| 82 | PROOF | A185010 | conjectured P-recursive recurrence | Mathar |
| 83 | PROOF | A185020 | conjectured P-recursive recurrence | Mathar |
| 84 | PROOF | A200312 | conjectured P-recursive recurrence | Mathar |
| 85 | PROOF | A162972 | conjectured P-recursive recurrence | Mathar |
| 86 | PROOF | A001465 | conjectured P-recursive recurrence | Mathar |
| 87 | PROOF | A085387 | conjectured P-recursive recurrence | Mathar |
| 88 | PROOF | A096471 | conjectured P-recursive recurrence | Mathar |
| 89 | PROOF | A066052 | conjectured P-recursive recurrence | Mathar |
| 90 | PROOF | A097204 | conjectured P-recursive recurrence | Mathar |
| 91 | PROOF | A000483 | conjectured P-recursive recurrence | Mathar |
| 92 | PROOF | A000276 | conjectured P-recursive recurrence | Mathar |
| 93 | PROOF | A002104 | conjectured P-recursive recurrence | Mathar |
| 94 | PROOF | A002538 | conjectured P-recursive recurrence | Mathar |
| 95 | PROOF | A066052 | conjectured P-recursive recurrence | Mathar |
| 96 | PROOF | A073591 | conjectured P-recursive recurrence | Mathar |
| 97 | PROOF | A108704 | conjectured P-recursive recurrence | Mathar |
| 98 | PROOF | A110322 | conjectured P-recursive recurrence | Mathar |
| 99 | PROOF | A185369 | conjectured P-recursive recurrence | Mathar |
| 100 | PROOF | A000276 | conjectured P-recursive recurrence | Mathar |
| 101 | PROOF | A000774 | conjectured P-recursive recurrence | Mathar |
| 102 | PROOF | A094905 | conjectured P-recursive recurrence | Mathar |
| 103 | PROOF | A005654 | conjectured P-recursive recurrence | Mathar |
| 104 | PROOF | A116385 | conjectured P-recursive recurrence | Mathar |
| 105 | PROOF | A005558 | conjectured P-recursive recurrence | Mathar |
| 106 | PROOF | A065942 | conjectured P-recursive recurrence | Mathar |
| 107 | PROOF | A081181 | conjectured P-recursive recurrence | Mathar |
| 108 | PROOF | A081204 | conjectured P-recursive recurrence | Mathar |
| 109 | PROOF | A005558 | conjectured P-recursive recurrence | Mathar |
| 110 | PROOF | A005559 | conjectured P-recursive recurrence | Mathar |
| 111 | PROOF | A005560 | conjectured P-recursive recurrence | Mathar |
| 112 | PROOF | A005561 | conjectured P-recursive recurrence | Mathar |
| 113 | PROOF | A005562 | conjectured P-recursive recurrence | Mathar |
| 114 | PROOF | A081204 | conjectured P-recursive recurrence | Mathar |
| 115 | PROOF | A081205 | conjectured P-recursive recurrence | Mathar |
| 116 | PROOF | A213203 | conjectured P-recursive recurrence | Mathar |
| 117 | PROOF | A242429 | conjectured P-recursive recurrence | Mathar |
| 118 | PROOF | A026018 | conjectured P-recursive recurrence | Mathar |
| 119 | PROOF | A092634 | conjectured P-recursive recurrence | Mathar |
| 120 | PROOF | A026026 | conjectured P-recursive recurrence | Mathar |
| 121 | PROOF | A052227 | conjectured P-recursive recurrence | Mathar |
| 122 | PROOF | A228329 | conjectured P-recursive recurrence | Mathar |
| 123 | PROOF | A259457 | conjectured P-recursive recurrence | Mathar |
| 124 | PROOF | A268554 | conjectured P-recursive recurrence | Mathar |
| 125 | PROOF | A102319 | conjectured P-recursive recurrence | Mathar |
| 126 | PROOF | A115256 | conjectured P-recursive recurrence | Mathar |
| 127 | PROOF | A157125 | conjectured P-recursive recurrence | Mathar |
| 128 | PROOF | A102318 | conjectured P-recursive recurrence | Mathar |
| 129 | PROOF | A107587 | conjectured P-recursive recurrence | Mathar |
| 130 | PROOF | A218185 | conjectured P-recursive recurrence | Mathar |
| 131 | PROOF | A025567 | conjectured P-recursive recurrence | Mathar |
| 132 | PROOF | A071684 | conjectured P-recursive recurrence | Mathar |
| 133 | PROOF | A179648 | conjectured P-recursive recurrence | Mathar |
| 134 | PROOF | A184120 | conjectured P-recursive recurrence | Mathar |
| 135 | PROOF | A026163 | conjectured P-recursive recurrence | Mathar |
| 136 | PROOF | A102318 | conjectured P-recursive recurrence | Mathar |
| 137 | PROOF | A101500 | conjectured P-recursive recurrence | Mathar |
| 138 | PROOF | A102319 | conjectured P-recursive recurrence | Mathar |
| 139 | PROOF | A107587 | conjectured P-recursive recurrence | Mathar |
| 140 | PROOF | A072100 | conjectured P-recursive recurrence | Mathar |
| 141 | PROOF | A025567 | conjectured P-recursive recurrence | Mathar |
| 142 | PROOF | A334509 | conjectured P-recursive recurrence | Spezia |
| 143 | PROOF | A298022 | conjectured P-recursive recurrence | Spezia |
| 144 | PROOF | A273676 | conjectured P-recursive recurrence | Mathar |
| 145 | PROOF | A273832 | conjectured P-recursive recurrence | Mathar |
| 146 | PROOF | A319371 | conjectured P-recursive recurrence | Mathar |
| 147 | PROOF | A110320 | conjectured P-recursive recurrence | McGarvey |
| 148 | PROOF | A309878 | conjectured P-recursive recurrence | Mathar |
| 149 | PROOF | A315520 | conjectured P-recursive recurrence | Spezia |
| 150 | PROOF | A346370 | conjectured P-recursive recurrence | Kurkov |
| 151 | PROOF | A191625 | conjectured P-recursive recurrence | Mathar |
| 152 | PROOF | A186341 | conjectured P-recursive recurrence | Mathar |
| 153 | PROOF | A026743 | conjectured P-recursive recurrence | Mathar |
| 154 | PROOF | A191786 | conjectured P-recursive recurrence | Mathar |
| 155 | PROOF | A210496 | conjectured P-recursive recurrence | Mathar |
| 156 | PROOF | A182892 | conjectured P-recursive recurrence | Mathar |
| 157 | PROOF | A270724 | conjectured P-recursive recurrence | Mathar |
| 158 | PROOF | A190171 | conjectured P-recursive recurrence | Mathar |
| 159 | PROOF | A257515 | conjectured P-recursive recurrence | Mathar |
| 160 | PROOF | A190788 | conjectured P-recursive recurrence | Mathar |
| 161 | PROOF | A095981 | conjectured P-recursive recurrence | Mathar |
| 162 | PROOF | A212205 | conjectured P-recursive recurrence | Mathar |
| 163 | PROOF | A270661 | conjectured P-recursive recurrence | Mathar |
| 164 | PROOF | A157021 | conjectured P-recursive recurrence | Mathar |
| 165 | PROOF | A165537 | conjectured P-recursive recurrence | Mathar |
| 166 | PROOF | A166287 | conjectured P-recursive recurrence | Mathar |
| 167 | PROOF | A174013 | conjectured P-recursive recurrence | Mathar |
| 168 | PROOF | A178072 | conjectured P-recursive recurrence | Mathar |
| 169 | PROOF | A182894 | conjectured P-recursive recurrence | Mathar |
| 170 | PROOF | A114584 | conjectured P-recursive recurrence | Mathar |
| 171 | PROOF | A164586 | conjectured P-recursive recurrence | Mathar |
| 172 | PROOF | A189053 | conjectured P-recursive recurrence | Mathar |
| 173 | PROOF | A182904 | conjectured P-recursive recurrence | Mathar |
| 174 | PROOF | A274295 | conjectured P-recursive recurrence | Mathar |
| 175 | PROOF | A226434 | conjectured P-recursive recurrence | Mathar |
| 176 | PROOF | A257104 | conjectured P-recursive recurrence | Mathar |
| 177 | PROOF | A108600 | conjectured P-recursive recurrence | Mathar |
| 178 | PROOF | A114851 | conjectured P-recursive recurrence | Mathar |
| 179 | PROOF | A125306 | conjectured P-recursive recurrence | Mathar |
| 180 | PROOF | A166290 | conjectured P-recursive recurrence | Mathar |
| 181 | PROOF | A228770 | conjectured P-recursive recurrence | Mathar |
| 182 | PROOF | A257300 | conjectured P-recursive recurrence | Mathar |
| 183 | PROOF | A089324 | conjectured P-recursive recurrence | Mathar |
| 184 | PROOF | A104625 | conjectured P-recursive recurrence | Mathar |
| 185 | PROOF | A113956 | conjectured P-recursive recurrence | Mathar |
| 186 | PROOF | A116383 | conjectured P-recursive recurrence | Mathar |
| 187 | PROOF | A162548 | conjectured P-recursive recurrence | Mathar |
| 188 | PROOF | A173993 | conjectured P-recursive recurrence | Mathar |
| 189 | PROOF | A244886 | conjectured P-recursive recurrence | Mathar |
| 190 | PROOF | A157003 | conjectured P-recursive recurrence | Mathar |
| 191 | PROOF | A163493 | conjectured P-recursive recurrence | Mathar |
| 192 | PROOF | A191398 | conjectured P-recursive recurrence | Mathar |
| 193 | PROOF | A135582 | conjectured P-recursive recurrence | Mathar |
| 194 | PROOF | A139376 | conjectured P-recursive recurrence | Mathar |
| 195 | PROOF | A346074 | conjectured P-recursive recurrence | Mathar |
| 196 | PROOF | A190166 | conjectured P-recursive recurrence | Mathar |
| 197 | PROOF | A025251 | conjectured P-recursive recurrence | Mathar |
| 198 | PROOF | A228771 | conjectured P-recursive recurrence | Mathar |
| 199 | PROOF | A025268 | conjectured P-recursive recurrence | Mathar |
| 200 | PROOF | A025272 | conjectured P-recursive recurrence | Mathar |
| 201 | PROOF | A385252 | conjectured P-recursive recurrence | Mathar |
| 202 | PROOF | A025758 | conjectured P-recursive recurrence | Mathar |
| 203 | PROOF | A114464 | conjectured P-recursive recurrence | Mathar |
| 204 | PROOF | A127154 | conjectured P-recursive recurrence | Mathar |
| 205 | PROOF | A135335 | conjectured P-recursive recurrence | Mathar |
| 206 | PROOF | A165540 | conjectured P-recursive recurrence | Mathar |
| 207 | PROOF | A171416 | conjectured P-recursive recurrence | Mathar |
| 208 | PROOF | A188314 | conjectured P-recursive recurrence | Mathar |
| 209 | PROOF | A254314 | conjectured P-recursive recurrence | Mathar |
| 210 | PROOF | A270661 | conjectured P-recursive recurrence | Mathar |
| 211 | PROOF | A003440 | conjectured P-recursive recurrence | Mathar |
| 212 | PROOF | A110521 | conjectured P-recursive recurrence | Mathar |
| 213 | PROOF | A114190 | conjectured P-recursive recurrence | Mathar |
| 214 | PROOF | A116387 | conjectured P-recursive recurrence | Mathar |
| 215 | PROOF | A128096 | conjectured P-recursive recurrence | Mathar |
| 216 | PROOF | A157021 | conjectured P-recursive recurrence | Mathar |
| 217 | PROOF | A160823 | conjectured P-recursive recurrence | Mathar |
| 218 | PROOF | A166287 | conjectured P-recursive recurrence | Mathar |
| 219 | PROOF | A174808 | conjectured P-recursive recurrence | Mathar |
| 220 | PROOF | A185089 | conjectured P-recursive recurrence | Mathar |
| 221 | PROOF | A186940 | conjectured P-recursive recurrence | Mathar |
| 222 | PROOF | A190736 | conjectured P-recursive recurrence | Mathar |
| 223 | PROOF | A219314 | conjectured P-recursive recurrence | Mathar |
| 224 | PROOF | A100095 | conjectured P-recursive recurrence | Mathar |
| 225 | PROOF | A100097 | conjectured P-recursive recurrence | Mathar |
| 226 | PROOF | A191313 | conjectured P-recursive recurrence | Mathar |
| 227 | PROOF | A191790 | conjectured P-recursive recurrence | Mathar |
| 228 | PROOF | A273351 | conjectured P-recursive recurrence | Mathar |
| 229 | PROOF | A278472 | conjectured P-recursive recurrence | Mathar |
| 230 | PROOF | A108296 | conjectured P-recursive recurrence | Mathar |
| 231 | PROOF | A116391 | conjectured P-recursive recurrence | Mathar |
| 232 | PROOF | A110198 | conjectured P-recursive recurrence | Mathar |
| 233 | PROOF | A182879 | conjectured P-recursive recurrence | Mathar |
| 234 | PROOF | A182887 | conjectured P-recursive recurrence | Mathar |
| 235 | PROOF | A135925 | conjectured P-recursive recurrence | Mathar |
| 236 | PROOF | A007901 | conjectured P-recursive recurrence | Mathar |
| 237 | PROOF | A025256 | conjectured P-recursive recurrence | Mathar |
| 238 | PROOF | A025258 | conjectured P-recursive recurrence | Mathar |
| 239 | PROOF | A000781 | conjectured P-recursive recurrence | Mathar |
| 240 | PROOF | A025245 | conjectured P-recursive recurrence | Mathar |
| 241 | PROOF | A025257 | conjectured P-recursive recurrence | Mathar |
| 242 | PROOF | A025269 | conjectured P-recursive recurrence | Mathar |
| 243 | PROOF | A025270 | conjectured P-recursive recurrence | Mathar |
| 244 | PROOF | A025275 | conjectured P-recursive recurrence | Mathar |
| 245 | PROOF | A032096 | conjectured P-recursive recurrence | Mathar |
| 246 | PROOF | A102880 | conjectured P-recursive recurrence | Mathar |
| 247 | PROOF | A111053 | conjectured P-recursive recurrence | Mathar |
| 248 | PROOF | A152120 | conjectured P-recursive recurrence | Mathar |
| 249 | PROOF | A159771 | conjectured P-recursive recurrence | Mathar |
| 250 | PROOF | A166694 | conjectured P-recursive recurrence | Mathar |
| 251 | PROOF | A166696 | conjectured P-recursive recurrence | Mathar |
| 252 | PROOF | A191796 | conjectured P-recursive recurrence | Mathar |
| 253 | PROOF | A217711 | conjectured P-recursive recurrence | Mathar |
| 254 | PROOF | A278023 | conjectured P-recursive recurrence | Mathar |
| 255 | PROOF | A279014 | conjectured P-recursive recurrence | Mathar |
| 256 | PROOF | A000483 | conjectured P-recursive recurrence | Mathar |
| 257 | PROOF | A025757 | conjectured P-recursive recurrence | Mathar |
| 258 | PROOF | A026030 | conjectured P-recursive recurrence | Mathar |
| 259 | PROOF | A026031 | conjectured P-recursive recurrence | Mathar |
| 260 | PROOF | A048775 | conjectured P-recursive recurrence | Mathar |
| 261 | PROOF | A116409 | conjectured P-recursive recurrence | Mathar |
| 262 | PROOF | A126322 | conjectured P-recursive recurrence | Mathar |
| 263 | PROOF | A128750 | conjectured P-recursive recurrence | Mathar |
| 264 | PROOF | A143955 | conjectured P-recursive recurrence | Mathar |
| 265 | PROOF | A165203 | conjectured P-recursive recurrence | Mathar |
| 266 | PROOF | A168505 | conjectured P-recursive recurrence | Mathar |
| 267 | PROOF | A176605 | conjectured P-recursive recurrence | Mathar |
| 268 | PROOF | A181933 | conjectured P-recursive recurrence | Mathar |
| 269 | PROOF | A191585 | conjectured P-recursive recurrence | Mathar |
| 270 | PROOF | A215973 | conjectured P-recursive recurrence | Mathar |
| 271 | PROOF | A234269 | conjectured P-recursive recurrence | Mathar |
| 272 | PROOF | A236407 | conjectured P-recursive recurrence | Mathar |
| 273 | PROOF | A270363 | conjectured P-recursive recurrence | Mathar |
| 274 | PROOF | A098521 | conjectured P-recursive recurrence | Mathar |
| 275 | PROOF | A100096 | conjectured P-recursive recurrence | Mathar |
| 276 | PROOF | A100099 | conjectured P-recursive recurrence | Mathar |
| 277 | PROOF | A105849 | conjectured P-recursive recurrence | Mathar |
| 278 | PROOF | A105864 | conjectured P-recursive recurrence | Mathar |
| 279 | PROOF | A105865 | conjectured P-recursive recurrence | Mathar |
| 280 | PROOF | A108308 | conjectured P-recursive recurrence | Mathar |
| 281 | PROOF | A114194 | conjectured P-recursive recurrence | Mathar |
| 282 | PROOF | A115967 | conjectured P-recursive recurrence | Mathar |
| 283 | PROOF | A120010 | conjectured P-recursive recurrence | Mathar |
| 284 | PROOF | A124431 | conjectured P-recursive recurrence | Mathar |
| 285 | PROOF | A124431 | conjectured P-recursive recurrence | Mathar |
| 286 | PROOF | A126568 | conjectured P-recursive recurrence | Mathar |
| 287 | PROOF | A132364 | conjectured P-recursive recurrence | Mathar |
| 288 | PROOF | A141342 | conjectured P-recursive recurrence | Mathar |
| 289 | PROOF | A155051 | conjectured P-recursive recurrence | Mathar |
| 290 | PROOF | A157100 | conjectured P-recursive recurrence | Mathar |
| 291 | PROOF | A166076 | conjectured P-recursive recurrence | Mathar |
| 292 | PROOF | A166300 | conjectured P-recursive recurrence | Mathar |
| 293 | PROOF | A168503 | conjectured P-recursive recurrence | Mathar |
| 294 | PROOF | A174107 | conjectured P-recursive recurrence | Mathar |
| 295 | PROOF | A174169 | conjectured P-recursive recurrence | Mathar |
| 296 | PROOF | A176332 | conjectured P-recursive recurrence | Mathar |
| 297 | PROOF | A184018 | conjectured P-recursive recurrence | Mathar |
| 298 | PROOF | A188312 | conjectured P-recursive recurrence | Mathar |
| 299 | PROOF | A188482 | conjectured P-recursive recurrence | Mathar |
| 300 | PROOF | A191782 | conjectured P-recursive recurrence | Mathar |
| 301 | PROOF | A217333 | conjectured P-recursive recurrence | Mathar |
| 302 | PROOF | A257072 | conjectured P-recursive recurrence | Mathar |
| 303 | PROOF | A261681 | conjectured P-recursive recurrence | Mathar |
| 304 | PROOF | A073155 | conjectured P-recursive recurrence | Mathar |
| 305 | PROOF | A105524 | conjectured P-recursive recurrence | Mathar |
| 306 | PROOF | A114589 | conjectured closed form | Mathar |
| 307 | PROOF | A114590 | conjectured closed form | Mathar |
| 308 | PROOF | A162481 | conjectured closed form | Mathar |
| 309 | PROOF | A188460 | conjectured closed form | Mathar |
| 310 | PROOF | A188464 | conjectured closed form | Mathar |
| 311 | PROOF | A190725 | conjectured closed form | Mathar |
| 312 | PROOF | A191526 | conjectured P-recursive recurrence | Mathar |
| 313 | PROOF | A191531 | conjectured P-recursive recurrence | Mathar |
| 314 | PROOF | A211278 | conjectured P-recursive recurrence | Mathar |
| 315 | PROOF | A026327 | conjectured P-recursive recurrence | Mathar |
| 316 | PROOF | A081207 | conjectured P-recursive recurrence | Mathar |
| 317 | PROOF | A102882 | conjectured P-recursive recurrence | Mathar |
| 318 | PROOF | A182881 | conjectured P-recursive recurrence | Mathar |
| 319 | PROOF | A191309 | conjectured P-recursive recurrence | Mathar |
| 320 | PROOF | A191319 | conjectured P-recursive recurrence | Mathar |
| 321 | PROOF | A191790 | conjectured P-recursive recurrence | Mathar |
| 322 | PROOF | A273351 | conjectured P-recursive recurrence | Mathar |
| 323 | PROOF | A025248 | conjectured P-recursive recurrence | Mathar |
| 324 | PROOF | A025249 | conjectured P-recursive recurrence | Mathar |
| 325 | PROOF | A026017 | conjectured P-recursive recurrence | Mathar |
| 326 | PROOF | A071717 | conjectured P-recursive recurrence | Mathar |
| 327 | PROOF | A081672 | conjectured P-recursive recurrence | Mathar |
| 328 | PROOF | A104722 | conjectured P-recursive recurrence | Mathar |
| 329 | PROOF | A109263 | sequence equals a convergent infinite series | Mathar |
| 330 | PROOF | A118093 | sequence equals a convergent infinite series | Mathar |
| 331 | PROOF | A118974 | conjectured P-recursive recurrence | Mathar |
| 332 | PROOF | A121320 | conjectured P-recursive recurrence | Mathar |
| 333 | PROOF | A126323 | conjectured P-recursive recurrence | Mathar |
| 334 | PROOF | A128723 | conjectured P-recursive recurrence | Mathar |
| 335 | PROOF | A135334 | conjectured P-recursive recurrence | Mathar |
| 336 | PROOF | A141351 | conjectured P-recursive recurrence | Mathar |
| 337 | PROOF | A141353 | conjectured P-recursive recurrence | Mathar |
| 338 | PROOF | A163824 | conjectured P-recursive recurrence | Mathar |
| 339 | PROOF | A165201 | conjectured P-recursive recurrence | Mathar |
| 340 | PROOF | A279014 | conjectured P-recursive recurrence | Mathar |
| 341 | PROOF | A025756 | conjectured P-recursive recurrence | Mathar |
| 342 | PROOF | A026027 | conjectured P-recursive recurrence | Mathar |
| 343 | PROOF | A026135 | conjectured P-recursive recurrence | Mathar |
| 344 | PROOF | A050168 | conjectured P-recursive recurrence | Mathar |
| 345 | PROOF | A059279 | conjectured P-recursive recurrence | Mathar |
| 346 | PROOF | A063395 | conjectured P-recursive recurrence | Mathar |
| 347 | PROOF | A071722 | conjectured P-recursive recurrence | Mathar |
| 348 | PROOF | A082134 | conjectured P-recursive recurrence | Mathar |
| 349 | PROOF | A097180 | conjectured P-recursive recurrence | Mathar |
| 350 | PROOF | A097189 | conjectured P-recursive recurrence | Mathar |
| 351 | PROOF | A097331 | conjectured P-recursive recurrence | Mathar |
| 352 | PROOF | A100193 | conjectured P-recursive recurrence | Mathar |
| 353 | PROOF | A103973 | conjectured P-recursive recurrence | Mathar |
| 354 | PROOF | A106181 | conjectured P-recursive recurrence | Mathar |
| 355 | PROOF | A108623 | conjectured P-recursive recurrence | Mathar |
| 356 | PROOF | A126180 | conjectured P-recursive recurrence | Mathar |
| 357 | PROOF | A128732 | conjectured P-recursive recurrence | Mathar |
| 358 | PROOF | A134389 | conjectured P-recursive recurrence | Mathar |
| 359 | PROOF | A143013 | conjectured P-recursive recurrence | Mathar |
| 360 | PROOF | A143954 | conjectured P-recursive recurrence | Mathar |
| 361 | PROOF | A157418 | conjectured P-recursive recurrence | Mathar |
| 362 | PROOF | A158196 | conjectured P-recursive recurrence | Mathar |
| 363 | PROOF | A158197 | conjectured P-recursive recurrence | Mathar |
| 364 | PROOF | A191585 | conjectured P-recursive recurrence | Mathar |
| 365 | PROOF | A257290 | conjectured P-recursive recurrence | Mathar |
| 366 | PROOF | A054341 | conjectured P-recursive recurrence | Mathar |
| 367 | PROOF | A071715 | conjectured P-recursive recurrence | Mathar |
| 368 | PROOF | A090413 | conjectured P-recursive recurrence | Mathar |
| 369 | PROOF | A090826 | conjectured P-recursive recurrence | Mathar |
| 370 | PROOF | A091699 | conjectured P-recursive recurrence | Mathar |
| 371 | PROOF | A098664 | conjectured P-recursive recurrence | Mathar |
| 372 | PROOF | A099363 | conjectured P-recursive recurrence | Mathar |
| 373 | PROOF | A100098 | conjectured P-recursive recurrence | Mathar |
| 374 | PROOF | A105872 | conjectured P-recursive recurrence | Mathar |
| 375 | PROOF | A119975 | conjectured P-recursive recurrence | Mathar |
| 376 | PROOF | A121724 | conjectured P-recursive recurrence | Mathar |
| 377 | PROOF | A121725 | conjectured P-recursive recurrence | Mathar |
| 378 | PROOF | A126931 | conjectured P-recursive recurrence | Mathar |
| 379 | PROOF | A126932 | conjectured P-recursive recurrence | Mathar |
| 380 | PROOF | A127361 | conjectured P-recursive recurrence | Mathar |
| 381 | PROOF | A127363 | conjectured P-recursive recurrence | Mathar |
| 382 | PROOF | A155051 | conjectured P-recursive recurrence | Mathar |
| 383 | PROOF | A166078 | conjectured P-recursive recurrence | Mathar |
| 384 | PROOF | A166587 | conjectured P-recursive recurrence | Mathar |
| 385 | PROOF | A166588 | conjectured P-recursive recurrence | Mathar |
| 386 | PROOF | A176006 | conjectured P-recursive recurrence | Mathar |
| 387 | PROOF | A185087 | conjectured P-recursive recurrence | Mathar |
| 388 | PROOF | A190724 | conjectured P-recursive recurrence | Mathar |
| 389 | PROOF | A225887 | conjectured P-recursive recurrence | Mathar |
| 390 | PROOF | A227081 | conjectured P-recursive recurrence | Mathar |
| 391 | PROOF | A257178 | conjectured P-recursive recurrence | Mathar |
| 392 | PROOF | A257388 | conjectured P-recursive recurrence | Mathar |
| 393 | PROOF | A257838 | conjectured P-recursive recurrence | Mathar |
| 394 | PROOF | A001712 | conjectured P-recursive recurrence | Mathar |
| 395 | PROOF | A025175 | conjectured P-recursive recurrence | Mathar |
| 396 | PROOF | A025577 | conjectured P-recursive recurrence | Mathar |
| 397 | PROOF | A026023 | conjectured P-recursive recurrence | Mathar |
| 398 | PROOF | A055217 | conjectured P-recursive recurrence | Mathar |
| 399 | PROOF | A081052 | identity between OEIS entries | Mathar |
| 400 | PROOF | A103821 | identity between OEIS entries | Mathar |
| 401 | PROOF | A107231 | identity between OEIS entries | Mathar |
| 402 | PROOF | A110199 | identity between OEIS entries | Mathar |
| 403 | PROOF | A116406 | identity between OEIS entries | Mathar |
| 404 | PROOF | A128734 | identity between OEIS entries | Mathar |
| 405 | PROOF | A191307 | identity between OEIS entries | Mathar |
| 406 | PROOF | A278472 | identity between OEIS entries | Mathar |
| 407 | PROOF | A034863 | identity between OEIS entries | Mathar |
| 408 | PROOF | A128652 | conjectured P-recursive recurrence | Mathar |
| 409 | PROOF | A174195 | conjectured P-recursive recurrence | Mathar |
| 410 | PROOF | A192480 | conjectured P-recursive recurrence | Mathar |
| 411 | PROOF | A158495 | conjectured P-recursive recurrence | Mathar |
| 412 | PROOF | A189176 | conjectured P-recursive recurrence | Mathar |
| 413 | PROOF | A194724 | conjectured P-recursive recurrence | Mathar |
| 414 | PROOF | A210474 | conjectured P-recursive recurrence | Mathar |
| 415 | PROOF | A262768 | conjectured P-recursive recurrence | Mathar |
| 416 | PROOF | A026029 | conjectured closed form | Mathar |
| 417 | PROOF | A064088 | conjectured closed form | Mathar |
| 418 | PROOF | A064089 | conjectured closed form | Mathar |
| 419 | PROOF | A064090 | conjectured P-recursive recurrence | Mathar |
| 420 | PROOF | A064091 | conjectured P-recursive recurrence | Mathar |
| 421 | PROOF | A064092 | conjectured P-recursive recurrence | Mathar |
| 422 | PROOF | A067299 | conjectured P-recursive recurrence | Mathar |
| 423 | PROOF | A068551 | conjectured P-recursive recurrence | Mathar |
| 424 | PROOF | A080243 | conjectured P-recursive recurrence | Mathar |
| 425 | PROOF | A114191 | conjectured P-recursive recurrence | Mathar |
| 426 | PROOF | A116881 | conjectured P-recursive recurrence | Mathar |
| 427 | PROOF | A122920 | conjectured P-recursive recurrence | Mathar |
| 428 | PROOF | A132864 | conjectured P-recursive recurrence | Mathar |
| 429 | PROOF | A133305 | conjectured P-recursive recurrence | Mathar |
| 430 | PROOF | A133306 | conjectured P-recursive recurrence | Mathar |
| 431 | PROOF | A133307 | conjectured P-recursive recurrence | Mathar |
| 432 | PROOF | A133308 | conjectured P-recursive recurrence | Mathar |
| 433 | PROOF | A141222 | conjectured P-recursive recurrence | Mathar |
| 434 | PROOF | A154623 | conjectured P-recursive recurrence | Mathar |
| 435 | PROOF | A157328 | conjectured P-recursive recurrence | Mathar |
| 436 | PROOF | A158196 | conjectured P-recursive recurrence | Mathar |
| 437 | PROOF | A158197 | conjectured P-recursive recurrence | Mathar |
| 438 | PROOF | A191993 | conjectured P-recursive recurrence | Mathar |
| 439 | PROOF | A225034 | conjectured P-recursive recurrence | Berselli |
| 440 | PROOF | A242172 | conjectured P-recursive recurrence | Mathar |
| 441 | PROOF | A002867 | conjectured P-recursive recurrence | Mathar |
| 442 | PROOF | A014533 | conjectured P-recursive recurrence | Mathar |
| 443 | PROOF | A051524 | conjectured P-recursive recurrence | Mathar |
| 444 | PROOF | A081046 | conjectured P-recursive recurrence | Mathar |
| 445 | PROOF | A098519 | conjectured P-recursive recurrence | Mathar |
| 446 | PROOF | A098520 | conjectured P-recursive recurrence | Mathar |
| 447 | PROOF | A101596 | conjectured P-recursive recurrence | Mathar |
| 448 | PROOF | A101601 | conjectured P-recursive recurrence | Mathar |
| 449 | PROOF | A101602 | conjectured P-recursive recurrence | Mathar |
| 450 | PROOF | A111779 | conjectured P-recursive recurrence | Mathar |
| 451 | PROOF | A112703 | conjectured P-recursive recurrence | Mathar |
| 452 | PROOF | A119012 | conjectured P-recursive recurrence | Mathar |
| 453 | PROOF | A128057 | conjectured P-recursive recurrence | Mathar |
| 454 | PROOF | A128746 | conjectured P-recursive recurrence | Mathar |
| 455 | PROOF | A132900 | conjectured P-recursive recurrence | Mathar |
| 456 | PROOF | A151483 | conjectured P-recursive recurrence | Mathar |
| 457 | PROOF | A167481 | conjectured P-recursive recurrence | Mathar |
| 458 | PROOF | A171556 | conjectured P-recursive recurrence | Mathar |
| 459 | PROOF | A176479 | conjectured P-recursive recurrence | Mathar |
| 460 | PROOF | A182401 | conjectured P-recursive recurrence | Mathar |
| 461 | PROOF | A208355 | conjectured P-recursive recurrence | Mathar |
| 462 | PROOF | A210064 | conjectured P-recursive recurrence | Mathar |
| 463 | PROOF | A240558 | conjectured P-recursive recurrence | Mathar |
| 464 | PROOF | A141771 | conjectured P-recursive recurrence | Mathar |
| 465 | PROOF | A025754 | conjectured P-recursive recurrence | Mathar |
| 466 | PROOF | A097188 | conjectured P-recursive recurrence | Mathar |
| 467 | PROOF | A097192 | conjectured P-recursive recurrence | Mathar |
| 468 | PROOF | A334511 | conjectured P-recursive recurrence | Spezia |
| 469 | PROOF | A333905 | conjectured P-recursive recurrence | Spezia |
| 470 | PROOF | A049486 | conjectured P-recursive recurrence | Mathar |
| 471 | PROOF | A267879 | conjectured P-recursive recurrence | Spezia |
| 472 | PROOF | A267802 | conjectured P-recursive recurrence | Barker |
| 473 | PROOF | A267847 | conjectured P-recursive recurrence | Barker |
| 474 | PROOF | A126501 | conjectured P-recursive recurrence | Barker |
| 475 | PROOF | A128153 | conjectured P-recursive recurrence | Mathar |
| 476 | PROOF | A272706 | conjectured P-recursive recurrence | Blomberg |
| 477 | PROOF | A025271 | conjectured P-recursive recurrence | Mathar |
| 478 | PROOF | A138164 | conjectured P-recursive recurrence | Mathar |
| 479 | PROOF | A143017 | conjectured P-recursive recurrence | Mathar |
| 480 | PROOF | A159772 | conjectured P-recursive recurrence | Mathar |
| 481 | PROOF | A000986 | conjectured P-recursive recurrence | Mathar |
| 482 | PROOF | A022917 | conjectured P-recursive recurrence | Mathar |
| 483 | PROOF | A217447 | conjectured P-recursive recurrence | Mathar |
| 484 | PROOF | A226302 | conjectured P-recursive recurrence | Mathar |
| 485 | PROOF | A026165 | conjectured P-recursive recurrence | Mathar |
| 486 | PROOF | A185966 | conjectured P-recursive recurrence | Mathar |
| 487 | PROOF | A200753 | conjectured P-recursive recurrence | Mathar |
| 488 | PROOF | A217358 | conjectured P-recursive recurrence | Mathar |
| 489 | PROOF | A228960 | conjectured P-recursive recurrence | Mathar |
| 490 | PROOF | A003435 | conjectured P-recursive recurrence | Mathar |
| 491 | PROOF | A228331 | conjectured P-recursive recurrence | Mathar |
| 492 | PROOF | A273019 | conjectured P-recursive recurrence | Mathar |
| 493 | PROOF | A386834 | conjectured P-recursive recurrence | Mathar |
| 494 | PROOF | A228330 | conjectured P-recursive recurrence | Mathar |
| 495 | PROOF | A228333 | conjectured P-recursive recurrence | Mathar |

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

### Still unexploited

`a(n) = A######(m*n+k)` for `m ≥ 2` — 14 such conjectures. The `m`-section of a rational
g.f. is rational: `G(y) = (1/m) Σ_{r<m} ζ^{−rk} F(ζ^r y^{1/m})`. Fiddly with roots of
unity, maybe two or three results. Not attempted.

`xref.py` resolves a definition that names another sequence into a closed form, using only
formulas those entries state as fact. Written and tested; not yet swept. Roughly 40 entries
have a shape it can reach, and the triangle references `A######(n,k)` -- another 21 -- need
the triangle's own formula first.

Word-counting entries ("binary strings of length n with equally many 001 and 010") are a
recognisable family among the 268 unreadable ones, and they are not out of reach: a
transfer matrix in two variables gives a rational `R(x,u)`, the sequence is
`[x^n][u^0]R`, and a diagonal of a bivariate rational function is algebraic. Not attempted.

The second Lagrange form, `a(n) = [x^n] φ(x)^(n+1)/(n+1)` (A182401 and others), gives
`A(t) = w(t)/t` with `w = t φ(w)`. `diagonal.py` handles only the first form; the
parser refuses this one because the exponent divides rather than multiplies. Same
machinery, a different residue. Not attempted.


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
