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

Last updated 26 Aug 2026. Roster: **452 papers**, files `1-PROOF.pdf` … `452-PROOF.pdf`, **numbered by how hard the result was**: 1 is the hardest.
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
| 31 | PROOF | A000670 | one theorem, twenty entries (Bala periodicity) |
| 32 | PROOF | A002050 | one theorem, twenty entries (Bala periodicity) |
| 33 | PROOF | A004123 | one theorem, twenty entries (Bala periodicity) |
| 34 | PROOF | A006531 | one theorem, twenty entries (Bala periodicity) |
| 35 | PROOF | A052895 | one theorem, twenty entries (Bala periodicity) |
| 36 | PROOF | A064618 | one theorem, twenty entries (Bala periodicity) |
| 37 | PROOF | A080253 | one theorem, twenty entries (Bala periodicity) |
| 38 | PROOF | A162314 | one theorem, twenty entries (Bala periodicity) |
| 39 | PROOF | A167137 | one theorem, twenty entries (Bala periodicity) |
| 40 | PROOF | A259533 | one theorem, twenty entries (Bala periodicity) |
| 41 | PROOF | A301921 | one theorem, twenty entries (Bala periodicity) |
| 42 | PROOF | A305550 | one theorem, twenty entries (Bala periodicity) |
| 43 | PROOF | A306082 | one theorem, twenty entries (Bala periodicity) |
| 44 | PROOF | A316142 | one theorem, twenty entries (Bala periodicity) |
| 45 | PROOF | A316143 | one theorem, twenty entries (Bala periodicity) |
| 46 | PROOF | A316144 | one theorem, twenty entries (Bala periodicity) |
| 47 | PROOF | A320352 | one theorem, twenty entries (Bala periodicity) |
| 48 | PROOF | A354242 | one theorem, twenty entries (Bala periodicity) |
| 49 | PROOF | A354253 | one theorem, twenty entries (Bala periodicity) |
| 50 | PROOF | A355409 | one theorem, twenty entries (Bala periodicity) |
| 51 | PROOF | A243764 | general algebraic function field |
| 52 | PROOF | A243760 | general algebraic function field |
| 53 | PROOF | A285195 | general algebraic function field |
| 54 | PROOF | A243814 | general algebraic function field |
| 55 | PROOF | A055392 | general algebraic function field |
| 56 | PROOF | A243022 | general algebraic function field |
| 57 | PROOF | A168506 | general algebraic function field |
| 58 | PROOF | A242566 | general algebraic function field |
| 59 | PROOF | A270530 | general algebraic function field |
| 60 | PROOF | A127632 | general algebraic function field |
| 61 | PROOF | A130655 | general algebraic function field |
| 62 | PROOF | A166135 | general algebraic function field |
| 63 | PROOF | A212696 | general algebraic function field |
| 64 | PROOF | A261196 | general algebraic function field |
| 65 | PROOF | A270530 | general algebraic function field |
| 66 | PROOF | A185010 | general algebraic function field |
| 67 | PROOF | A185020 | general algebraic function field |
| 68 | PROOF | A200312 | general algebraic function field |
| 69 | PROOF | A162972 | transcendental e.g.f., differential module |
| 70 | PROOF | A001465 | transcendental e.g.f., differential module |
| 71 | PROOF | A085387 | transcendental e.g.f., differential module |
| 72 | PROOF | A096471 | transcendental e.g.f., differential module |
| 73 | PROOF | A066052 | transcendental e.g.f., differential module |
| 74 | PROOF | A097204 | transcendental e.g.f., differential module |
| 75 | PROOF | A000483 | transcendental e.g.f., differential module |
| 76 | PROOF | A000276 | transcendental e.g.f., differential module |
| 77 | PROOF | A002104 | transcendental e.g.f., differential module |
| 78 | PROOF | A002538 | transcendental e.g.f., differential module |
| 79 | PROOF | A066052 | transcendental e.g.f., differential module |
| 80 | PROOF | A073591 | transcendental e.g.f., differential module |
| 81 | PROOF | A108704 | transcendental e.g.f., differential module |
| 82 | PROOF | A110322 | transcendental e.g.f., differential module |
| 83 | PROOF | A185369 | transcendental e.g.f., differential module |
| 84 | PROOF | A000276 | transcendental e.g.f., differential module |
| 85 | PROOF | A000774 | transcendental e.g.f., differential module |
| 86 | PROOF | A081923 | transcendental e.g.f., differential module |
| 87 | PROOF | A102319 | several independent square roots |
| 88 | PROOF | A115256 | several independent square roots |
| 89 | PROOF | A157125 | several independent square roots |
| 90 | PROOF | A102318 | several independent square roots |
| 91 | PROOF | A107587 | several independent square roots |
| 92 | PROOF | A218185 | several independent square roots |
| 93 | PROOF | A025567 | several independent square roots |
| 94 | PROOF | A071684 | several independent square roots |
| 95 | PROOF | A179648 | several independent square roots |
| 96 | PROOF | A184120 | several independent square roots |
| 97 | PROOF | A026163 | several independent square roots |
| 98 | PROOF | A102318 | several independent square roots |
| 99 | PROOF | A101500 | several independent square roots |
| 100 | PROOF | A102319 | several independent square roots |
| 101 | PROOF | A107587 | several independent square roots |
| 102 | PROOF | A072100 | several independent square roots |
| 103 | PROOF | A025567 | several independent square roots |
| 104 | PROOF | A334509 | identity between different entries |
| 105 | PROOF | A298022 | identity between different entries |
| 106 | PROOF | A273676 | identity between different entries |
| 107 | PROOF | A273832 | identity between different entries |
| 108 | PROOF | A319371 | identity between different entries |
| 109 | PROOF | A110320 | identity between different entries |
| 110 | PROOF | A309878 | identity between different entries |
| 111 | PROOF | A315520 | identity between different entries |
| 112 | PROOF | A346370 | identity between different entries |
| 113 | PROOF | A191625 | residual test on the posted g.f. |
| 114 | PROOF | A186341 | residual test on the posted g.f. |
| 115 | PROOF | A026743 | residual test on the posted g.f. |
| 116 | PROOF | A191786 | residual test on the posted g.f. |
| 117 | PROOF | A210496 | residual test on the posted g.f. |
| 118 | PROOF | A182892 | residual test on the posted g.f. |
| 119 | PROOF | A270724 | residual test on the posted g.f. |
| 120 | PROOF | A190171 | residual test on the posted g.f. |
| 121 | PROOF | A257515 | residual test on the posted g.f. |
| 122 | PROOF | A190788 | residual test on the posted g.f. |
| 123 | PROOF | A212205 | residual test on the posted g.f. |
| 124 | PROOF | A270661 | residual test on the posted g.f. |
| 125 | PROOF | A157021 | residual test on the posted g.f. |
| 126 | PROOF | A165537 | residual test on the posted g.f. |
| 127 | PROOF | A166287 | residual test on the posted g.f. |
| 128 | PROOF | A174013 | residual test on the posted g.f. |
| 129 | PROOF | A178072 | residual test on the posted g.f. |
| 130 | PROOF | A182894 | residual test on the posted g.f. |
| 131 | PROOF | A114584 | residual test on the posted g.f. |
| 132 | PROOF | A164586 | residual test on the posted g.f. |
| 133 | PROOF | A189053 | residual test on the posted g.f. |
| 134 | PROOF | A182904 | residual test on the posted g.f. |
| 135 | PROOF | A274295 | residual test on the posted g.f. |
| 136 | PROOF | A226434 | residual test on the posted g.f. |
| 137 | PROOF | A108600 | residual test on the posted g.f. |
| 138 | PROOF | A114851 | residual test on the posted g.f. |
| 139 | PROOF | A125306 | residual test on the posted g.f. |
| 140 | PROOF | A166290 | residual test on the posted g.f. |
| 141 | PROOF | A228770 | residual test on the posted g.f. |
| 142 | PROOF | A257300 | residual test on the posted g.f. |
| 143 | PROOF | A089324 | residual test on the posted g.f. |
| 144 | PROOF | A104625 | residual test on the posted g.f. |
| 145 | PROOF | A113956 | residual test on the posted g.f. |
| 146 | PROOF | A116383 | residual test on the posted g.f. |
| 147 | PROOF | A162548 | residual test on the posted g.f. |
| 148 | PROOF | A173993 | residual test on the posted g.f. |
| 149 | PROOF | A244886 | residual test on the posted g.f. |
| 150 | PROOF | A157003 | residual test on the posted g.f. |
| 151 | PROOF | A163493 | residual test on the posted g.f. |
| 152 | PROOF | A191398 | residual test on the posted g.f. |
| 153 | PROOF | A135582 | residual test on the posted g.f. |
| 154 | PROOF | A139376 | residual test on the posted g.f. |
| 155 | PROOF | A346074 | residual test on the posted g.f. |
| 156 | PROOF | A190166 | residual test on the posted g.f. |
| 157 | PROOF | A025251 | residual test on the posted g.f. |
| 158 | PROOF | A228771 | residual test on the posted g.f. |
| 159 | PROOF | A025268 | residual test on the posted g.f. |
| 160 | PROOF | A025272 | residual test on the posted g.f. |
| 161 | PROOF | A385252 | residual test on the posted g.f. |
| 162 | PROOF | A025758 | residual test on the posted g.f. |
| 163 | PROOF | A114464 | residual test on the posted g.f. |
| 164 | PROOF | A127154 | residual test on the posted g.f. |
| 165 | PROOF | A135335 | residual test on the posted g.f. |
| 166 | PROOF | A165540 | residual test on the posted g.f. |
| 167 | PROOF | A171416 | residual test on the posted g.f. |
| 168 | PROOF | A188314 | residual test on the posted g.f. |
| 169 | PROOF | A254314 | residual test on the posted g.f. |
| 170 | PROOF | A270661 | residual test on the posted g.f. |
| 171 | PROOF | A003440 | residual test on the posted g.f. |
| 172 | PROOF | A110521 | residual test on the posted g.f. |
| 173 | PROOF | A114190 | residual test on the posted g.f. |
| 174 | PROOF | A116387 | residual test on the posted g.f. |
| 175 | PROOF | A128096 | residual test on the posted g.f. |
| 176 | PROOF | A157021 | residual test on the posted g.f. |
| 177 | PROOF | A160823 | residual test on the posted g.f. |
| 178 | PROOF | A166287 | residual test on the posted g.f. |
| 179 | PROOF | A174808 | residual test on the posted g.f. |
| 180 | PROOF | A185089 | residual test on the posted g.f. |
| 181 | PROOF | A186940 | residual test on the posted g.f. |
| 182 | PROOF | A190736 | residual test on the posted g.f. |
| 183 | PROOF | A219314 | residual test on the posted g.f. |
| 184 | PROOF | A100095 | residual test on the posted g.f. |
| 185 | PROOF | A100097 | residual test on the posted g.f. |
| 186 | PROOF | A191313 | residual test on the posted g.f. |
| 187 | PROOF | A191790 | residual test on the posted g.f. |
| 188 | PROOF | A273351 | residual test on the posted g.f. |
| 189 | PROOF | A278472 | residual test on the posted g.f. |
| 190 | PROOF | A108296 | residual test on the posted g.f. |
| 191 | PROOF | A116391 | residual test on the posted g.f. |
| 192 | PROOF | A110198 | residual test on the posted g.f. |
| 193 | PROOF | A182879 | residual test on the posted g.f. |
| 194 | PROOF | A182887 | residual test on the posted g.f. |
| 195 | PROOF | A135925 | residual test on the posted g.f. |
| 196 | PROOF | A025256 | residual test on the posted g.f. |
| 197 | PROOF | A025258 | residual test on the posted g.f. |
| 198 | PROOF | A000781 | residual test on the posted g.f. |
| 199 | PROOF | A025245 | residual test on the posted g.f. |
| 200 | PROOF | A025257 | residual test on the posted g.f. |
| 201 | PROOF | A025269 | residual test on the posted g.f. |
| 202 | PROOF | A025270 | residual test on the posted g.f. |
| 203 | PROOF | A025275 | residual test on the posted g.f. |
| 204 | PROOF | A032096 | residual test on the posted g.f. |
| 205 | PROOF | A102880 | residual test on the posted g.f. |
| 206 | PROOF | A111053 | residual test on the posted g.f. |
| 207 | PROOF | A152120 | residual test on the posted g.f. |
| 208 | PROOF | A159771 | residual test on the posted g.f. |
| 209 | PROOF | A166694 | residual test on the posted g.f. |
| 210 | PROOF | A166696 | residual test on the posted g.f. |
| 211 | PROOF | A191796 | residual test on the posted g.f. |
| 212 | PROOF | A217711 | residual test on the posted g.f. |
| 213 | PROOF | A278023 | residual test on the posted g.f. |
| 214 | PROOF | A279014 | residual test on the posted g.f. |
| 215 | PROOF | A000483 | residual test on the posted g.f. |
| 216 | PROOF | A025757 | residual test on the posted g.f. |
| 217 | PROOF | A026030 | residual test on the posted g.f. |
| 218 | PROOF | A026031 | residual test on the posted g.f. |
| 219 | PROOF | A048775 | residual test on the posted g.f. |
| 220 | PROOF | A116409 | residual test on the posted g.f. |
| 221 | PROOF | A126322 | residual test on the posted g.f. |
| 222 | PROOF | A128750 | residual test on the posted g.f. |
| 223 | PROOF | A143955 | residual test on the posted g.f. |
| 224 | PROOF | A165203 | residual test on the posted g.f. |
| 225 | PROOF | A168505 | residual test on the posted g.f. |
| 226 | PROOF | A176605 | residual test on the posted g.f. |
| 227 | PROOF | A181933 | residual test on the posted g.f. |
| 228 | PROOF | A191585 | residual test on the posted g.f. |
| 229 | PROOF | A215973 | residual test on the posted g.f. |
| 230 | PROOF | A234269 | residual test on the posted g.f. |
| 231 | PROOF | A236407 | residual test on the posted g.f. |
| 232 | PROOF | A270363 | residual test on the posted g.f. |
| 233 | PROOF | A098521 | residual test on the posted g.f. |
| 234 | PROOF | A100096 | residual test on the posted g.f. |
| 235 | PROOF | A100099 | residual test on the posted g.f. |
| 236 | PROOF | A105849 | residual test on the posted g.f. |
| 237 | PROOF | A105864 | residual test on the posted g.f. |
| 238 | PROOF | A105865 | residual test on the posted g.f. |
| 239 | PROOF | A108308 | residual test on the posted g.f. |
| 240 | PROOF | A114194 | residual test on the posted g.f. |
| 241 | PROOF | A115967 | residual test on the posted g.f. |
| 242 | PROOF | A120010 | residual test on the posted g.f. |
| 243 | PROOF | A124431 | residual test on the posted g.f. |
| 244 | PROOF | A124431 | residual test on the posted g.f. |
| 245 | PROOF | A126568 | residual test on the posted g.f. |
| 246 | PROOF | A132364 | residual test on the posted g.f. |
| 247 | PROOF | A141342 | residual test on the posted g.f. |
| 248 | PROOF | A155051 | residual test on the posted g.f. |
| 249 | PROOF | A157100 | residual test on the posted g.f. |
| 250 | PROOF | A162477 | residual test on the posted g.f. |
| 251 | PROOF | A166076 | residual test on the posted g.f. |
| 252 | PROOF | A166300 | residual test on the posted g.f. |
| 253 | PROOF | A168503 | residual test on the posted g.f. |
| 254 | PROOF | A174107 | residual test on the posted g.f. |
| 255 | PROOF | A174169 | residual test on the posted g.f. |
| 256 | PROOF | A176332 | residual test on the posted g.f. |
| 257 | PROOF | A184018 | residual test on the posted g.f. |
| 258 | PROOF | A188312 | residual test on the posted g.f. |
| 259 | PROOF | A188482 | residual test on the posted g.f. |
| 260 | PROOF | A191782 | residual test on the posted g.f. |
| 261 | PROOF | A217333 | residual test on the posted g.f. |
| 262 | PROOF | A257072 | residual test on the posted g.f. |
| 263 | PROOF | A261681 | residual test on the posted g.f. |
| 264 | PROOF | A073155 | residual test on the posted g.f. |
| 265 | PROOF | A114589 | residual test on the posted g.f. |
| 266 | PROOF | A114590 | residual test on the posted g.f. |
| 267 | PROOF | A162481 | residual test on the posted g.f. |
| 268 | PROOF | A188460 | residual test on the posted g.f. |
| 269 | PROOF | A188464 | residual test on the posted g.f. |
| 270 | PROOF | A190725 | residual test on the posted g.f. |
| 271 | PROOF | A191526 | residual test on the posted g.f. |
| 272 | PROOF | A191531 | residual test on the posted g.f. |
| 273 | PROOF | A211278 | residual test on the posted g.f. |
| 274 | PROOF | A026327 | residual test on the posted g.f. |
| 275 | PROOF | A081207 | residual test on the posted g.f. |
| 276 | PROOF | A102882 | residual test on the posted g.f. |
| 277 | PROOF | A182881 | residual test on the posted g.f. |
| 278 | PROOF | A191309 | residual test on the posted g.f. |
| 279 | PROOF | A191319 | residual test on the posted g.f. |
| 280 | PROOF | A191790 | residual test on the posted g.f. |
| 281 | PROOF | A273351 | residual test on the posted g.f. |
| 282 | PROOF | A025248 | residual test on the posted g.f. |
| 283 | PROOF | A025249 | residual test on the posted g.f. |
| 284 | PROOF | A026017 | residual test on the posted g.f. |
| 285 | PROOF | A071717 | residual test on the posted g.f. |
| 286 | PROOF | A081672 | residual test on the posted g.f. |
| 287 | PROOF | A093387 | residual test on the posted g.f. |
| 288 | PROOF | A104722 | residual test on the posted g.f. |
| 289 | PROOF | A109263 | residual test on the posted g.f. |
| 290 | PROOF | A118093 | residual test on the posted g.f. |
| 291 | PROOF | A118974 | residual test on the posted g.f. |
| 292 | PROOF | A126323 | residual test on the posted g.f. |
| 293 | PROOF | A128723 | residual test on the posted g.f. |
| 294 | PROOF | A135334 | residual test on the posted g.f. |
| 295 | PROOF | A141351 | residual test on the posted g.f. |
| 296 | PROOF | A141353 | residual test on the posted g.f. |
| 297 | PROOF | A163824 | residual test on the posted g.f. |
| 298 | PROOF | A165201 | residual test on the posted g.f. |
| 299 | PROOF | A279014 | residual test on the posted g.f. |
| 300 | PROOF | A025756 | residual test on the posted g.f. |
| 301 | PROOF | A026027 | residual test on the posted g.f. |
| 302 | PROOF | A026135 | residual test on the posted g.f. |
| 303 | PROOF | A050168 | residual test on the posted g.f. |
| 304 | PROOF | A059279 | residual test on the posted g.f. |
| 305 | PROOF | A063395 | residual test on the posted g.f. |
| 306 | PROOF | A071722 | residual test on the posted g.f. |
| 307 | PROOF | A082134 | residual test on the posted g.f. |
| 308 | PROOF | A097180 | residual test on the posted g.f. |
| 309 | PROOF | A097189 | residual test on the posted g.f. |
| 310 | PROOF | A097331 | residual test on the posted g.f. |
| 311 | PROOF | A100193 | residual test on the posted g.f. |
| 312 | PROOF | A103973 | residual test on the posted g.f. |
| 313 | PROOF | A106181 | residual test on the posted g.f. |
| 314 | PROOF | A108623 | residual test on the posted g.f. |
| 315 | PROOF | A126180 | residual test on the posted g.f. |
| 316 | PROOF | A128732 | residual test on the posted g.f. |
| 317 | PROOF | A134389 | residual test on the posted g.f. |
| 318 | PROOF | A143013 | residual test on the posted g.f. |
| 319 | PROOF | A143954 | residual test on the posted g.f. |
| 320 | PROOF | A157418 | residual test on the posted g.f. |
| 321 | PROOF | A158196 | residual test on the posted g.f. |
| 322 | PROOF | A158197 | residual test on the posted g.f. |
| 323 | PROOF | A191585 | residual test on the posted g.f. |
| 324 | PROOF | A257290 | residual test on the posted g.f. |
| 325 | PROOF | A054341 | residual test on the posted g.f. |
| 326 | PROOF | A071715 | residual test on the posted g.f. |
| 327 | PROOF | A090413 | residual test on the posted g.f. |
| 328 | PROOF | A091699 | residual test on the posted g.f. |
| 329 | PROOF | A098664 | residual test on the posted g.f. |
| 330 | PROOF | A099363 | residual test on the posted g.f. |
| 331 | PROOF | A100098 | residual test on the posted g.f. |
| 332 | PROOF | A105872 | residual test on the posted g.f. |
| 333 | PROOF | A106272 | residual test on the posted g.f. |
| 334 | PROOF | A121724 | residual test on the posted g.f. |
| 335 | PROOF | A121725 | residual test on the posted g.f. |
| 336 | PROOF | A126931 | residual test on the posted g.f. |
| 337 | PROOF | A126932 | residual test on the posted g.f. |
| 338 | PROOF | A127361 | residual test on the posted g.f. |
| 339 | PROOF | A127363 | residual test on the posted g.f. |
| 340 | PROOF | A155051 | residual test on the posted g.f. |
| 341 | PROOF | A166078 | residual test on the posted g.f. |
| 342 | PROOF | A166587 | residual test on the posted g.f. |
| 343 | PROOF | A166588 | residual test on the posted g.f. |
| 344 | PROOF | A185087 | residual test on the posted g.f. |
| 345 | PROOF | A190724 | residual test on the posted g.f. |
| 346 | PROOF | A225887 | residual test on the posted g.f. |
| 347 | PROOF | A227081 | residual test on the posted g.f. |
| 348 | PROOF | A257178 | residual test on the posted g.f. |
| 349 | PROOF | A257388 | residual test on the posted g.f. |
| 350 | PROOF | A257838 | residual test on the posted g.f. |
| 351 | PROOF | A001712 | residual test on the posted g.f. |
| 352 | PROOF | A025175 | residual test on the posted g.f. |
| 353 | PROOF | A025577 | residual test on the posted g.f. |
| 354 | PROOF | A055217 | residual test on the posted g.f. |
| 355 | PROOF | A081052 | residual test on the posted g.f. |
| 356 | PROOF | A103821 | residual test on the posted g.f. |
| 357 | PROOF | A107231 | residual test on the posted g.f. |
| 358 | PROOF | A110199 | residual test on the posted g.f. |
| 359 | PROOF | A116406 | residual test on the posted g.f. |
| 360 | PROOF | A128734 | residual test on the posted g.f. |
| 361 | PROOF | A191307 | residual test on the posted g.f. |
| 362 | PROOF | A278472 | residual test on the posted g.f. |
| 363 | PROOF | A034863 | residual test on the posted g.f. |
| 364 | PROOF | A174195 | residual test on the posted g.f. |
| 365 | PROOF | A192480 | residual test on the posted g.f. |
| 366 | PROOF | A158495 | residual test on the posted g.f. |
| 367 | PROOF | A189176 | residual test on the posted g.f. |
| 368 | PROOF | A194724 | residual test on the posted g.f. |
| 369 | PROOF | A210474 | residual test on the posted g.f. |
| 370 | PROOF | A262768 | residual test on the posted g.f. |
| 371 | PROOF | A026029 | residual test on the posted g.f. |
| 372 | PROOF | A064088 | residual test on the posted g.f. |
| 373 | PROOF | A064089 | residual test on the posted g.f. |
| 374 | PROOF | A064090 | residual test on the posted g.f. |
| 375 | PROOF | A064091 | residual test on the posted g.f. |
| 376 | PROOF | A064092 | residual test on the posted g.f. |
| 377 | PROOF | A067299 | residual test on the posted g.f. |
| 378 | PROOF | A068551 | residual test on the posted g.f. |
| 379 | PROOF | A080243 | residual test on the posted g.f. |
| 380 | PROOF | A106271 | residual test on the posted g.f. |
| 381 | PROOF | A114191 | residual test on the posted g.f. |
| 382 | PROOF | A116881 | residual test on the posted g.f. |
| 383 | PROOF | A122920 | residual test on the posted g.f. |
| 384 | PROOF | A132864 | residual test on the posted g.f. |
| 385 | PROOF | A133305 | residual test on the posted g.f. |
| 386 | PROOF | A133306 | residual test on the posted g.f. |
| 387 | PROOF | A133307 | residual test on the posted g.f. |
| 388 | PROOF | A133308 | residual test on the posted g.f. |
| 389 | PROOF | A141222 | residual test on the posted g.f. |
| 390 | PROOF | A154623 | residual test on the posted g.f. |
| 391 | PROOF | A155587 | residual test on the posted g.f. |
| 392 | PROOF | A157328 | residual test on the posted g.f. |
| 393 | PROOF | A158196 | residual test on the posted g.f. |
| 394 | PROOF | A158197 | residual test on the posted g.f. |
| 395 | PROOF | A191993 | residual test on the posted g.f. |
| 396 | PROOF | A225034 | residual test on the posted g.f. |
| 397 | PROOF | A242172 | residual test on the posted g.f. |
| 398 | PROOF | A002867 | residual test on the posted g.f. |
| 399 | PROOF | A014533 | residual test on the posted g.f. |
| 400 | PROOF | A051524 | residual test on the posted g.f. |
| 401 | PROOF | A081046 | residual test on the posted g.f. |
| 402 | PROOF | A098519 | residual test on the posted g.f. |
| 403 | PROOF | A098520 | residual test on the posted g.f. |
| 404 | PROOF | A101596 | residual test on the posted g.f. |
| 405 | PROOF | A101601 | residual test on the posted g.f. |
| 406 | PROOF | A101602 | residual test on the posted g.f. |
| 407 | PROOF | A111779 | residual test on the posted g.f. |
| 408 | PROOF | A112703 | residual test on the posted g.f. |
| 409 | PROOF | A119012 | residual test on the posted g.f. |
| 410 | PROOF | A128057 | residual test on the posted g.f. |
| 411 | PROOF | A128746 | residual test on the posted g.f. |
| 412 | PROOF | A132900 | residual test on the posted g.f. |
| 413 | PROOF | A151483 | residual test on the posted g.f. |
| 414 | PROOF | A167481 | residual test on the posted g.f. |
| 415 | PROOF | A171556 | residual test on the posted g.f. |
| 416 | PROOF | A176479 | residual test on the posted g.f. |
| 417 | PROOF | A182401 | residual test on the posted g.f. |
| 418 | PROOF | A208355 | residual test on the posted g.f. |
| 419 | PROOF | A210064 | residual test on the posted g.f. |
| 420 | PROOF | A240558 | residual test on the posted g.f. |
| 421 | PROOF | A141771 | residual test on the posted g.f. |
| 422 | PROOF | A025754 | residual test on the posted g.f. |
| 423 | PROOF | A097188 | residual test on the posted g.f. |
| 424 | PROOF | A097192 | residual test on the posted g.f. |
| 425 | PROOF | A334511 | closed form against the posted g.f. |
| 426 | PROOF | A333905 | closed form against the posted g.f. |
| 427 | PROOF | A049486 | closed form against the posted g.f. |
| 428 | PROOF | A267879 | closed form against the posted g.f. |
| 429 | PROOF | A267802 | closed form against the posted g.f. |
| 430 | PROOF | A267847 | closed form against the posted g.f. |
| 431 | PROOF | A126501 | closed form against the posted g.f. |
| 432 | PROOF | A128153 | closed form against the posted g.f. |
| 433 | PROOF | A272706 | closed form against the posted g.f. |
| 434 | PROOF | A025271 | one posted operator divides another |
| 435 | PROOF | A138164 | one posted operator divides another |
| 436 | PROOF | A143017 | one posted operator divides another |
| 437 | PROOF | A159772 | one posted operator divides another |
| 438 | PROOF | A000986 | one posted operator divides another |
| 439 | PROOF | A022917 | one posted operator divides another |
| 440 | PROOF | A217447 | one posted operator divides another |
| 441 | PROOF | A226302 | one posted operator divides another |
| 442 | PROOF | A026165 | one posted operator divides another |
| 443 | PROOF | A185966 | one posted operator divides another |
| 444 | PROOF | A200753 | one posted operator divides another |
| 445 | PROOF | A217358 | one posted operator divides another |
| 446 | PROOF | A228960 | one posted operator divides another |
| 447 | PROOF | A003435 | one posted operator divides another |
| 448 | PROOF | A228331 | one posted operator divides another |
| 449 | PROOF | A273019 | one posted operator divides another |
| 450 | PROOF | A386834 | one posted operator divides another |
| 451 | PROOF | A228330 | one posted operator divides another |
| 452 | PROOF | A228333 | one posted operator divides another |

### What the ranking means

Papers are numbered by how hard the result was, 1 hardest. The tiers, and where they fall:

| ranks | what the proof required |
|---|---|
| 1-30 | a separate argument found for that one problem |
| 31-50 | one theorem (Bala periodicity), proved once and applied to twenty entries |
| 51- | a decision procedure over a generating function the entry already posts |

So **ranks 1-50 are the ones with mathematics on the page**. Everything from 51 on is a
real proof of a genuinely open conjecture, but the argument lives in the engine rather
than in the paper.

Within the mechanical range the order is: recurrence derived from the summand by
telescoping; general algebraic function field; transcendental e.g.f.; several independent
square roots; identity between entries; the standard residual test; closed form against
the posted g.f.; and last, one posted operator dividing another -- honestly the
shallowest thing here, since both recurrences were already on the entry. Inside each tier
the order is by the size of the object handled: order of the recurrence first, then degree
of the residual.

`rank-map.json` records what each paper was numbered before. A new result is ranked into
position, not appended.


### Caveats to disclose when handing these over

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


### Still unexploited

`a(n) = A######(m*n+k)` for `m ≥ 2` — 14 such conjectures. The `m`-section of a rational
g.f. is rational: `G(y) = (1/m) Σ_{r<m} ζ^{−rk} F(ζ^r y^{1/m})`. Fiddly with roots of
unity, maybe two or three results. Not attempted.


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
