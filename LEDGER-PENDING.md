# Pending ledger notes

Written by the hourly working routine; folded into LEDGER.md and cleared by the daily
routine. Not a published document.

## 7 September 2026 --- two papers withdrawn: somebody else was three days earlier

The local OEIS mirror was two days stale. Refreshed to the 7 September export and every one
of the 9676 roster entries re-checked for settlement wording. **27 entries carry such
wording; 25 of them are about a different statement on the same entry** --- the pattern the
openness checker's own docstring records, and the papers involved already say so in their own
first pages (paper 0007 names Greathouse's 2013 confirmation of the square case and proves
Kaydalov's rectangle case; paper 0005 names Adamczewski on Conjectures B and C and proves A).

**Two are real, and both are withdrawn.**

- **A105872**, paper 9503, dated 25 August 2026.
- **A127361**, paper 9509, dated 25 August 2026.

Both prove R. J. Mathar's conjectured polynomial-coefficient recurrence. The entries now
carry `[Proved in Easwar (2026). - Rohun Easwar, Aug 31 2026]`, and the linked preprint is
arXiv:2608.22053, **submitted 22 August 2026** --- verified on the arXiv abstract page, not
inferred from the identifier. That is three days before the date on my papers. The standing
rule is that a result found after mine stays and one found before mine goes; these were found
before mine, so they go. Roster 9703 -> 9701.

Easwar's preprint is cited by six OEIS entries (A002897, A034015, A094213, A105872, A127361,
A290575); only those two were ever in the roster, so nothing else is affected.

**What this says about the method.** The freshness of the mirror is part of the count. A
two-day-old export cost two papers that should never have been claimed, and would have kept
costing them silently. The check is cheap --- one `git pull` and a scan of 9676 entries in
under a minute --- and belongs at the start of every session, not at the end.

## 7 September 2026 --- the 208 the queue never reached: 76 more

The 799 conjecture-carrying candidates were swept in rounds bounded by wall-clock, and the
round ended before the list did: **208 were left unprocessed rather than refused**, which is
a different thing and had to be checked rather than assumed. It was worth checking --- one of
them, A279576, settles in three seconds from a standing start.

Swept at thirty seconds an entry: **76 proved**, thirty-five of them arrays of permutations
under an offset condition, nineteen on permutation arrays with a fixed displacement, ten more
on the same family, and a tail of four engines. None is contradicted by its own published
data.

**Refusals, with the cap beside them, as the rule requires.** 92 refused with `state space >
cap` at **cap 2000000**; 3 exceeded the thirty-second budget in the annihilation test rather
than in the build, and are worth a longer pass rather than a bigger cap; 30 are not open.

**A cost measured, not guessed.** The heavy end of this pool is real work, not a bug:
A264014 builds 1048576 states in 84 seconds. That is why the pass was run at thirty seconds
and the expensive tail deferred, instead of letting four entries consume the whole budget.

**Settlement re-checked before counting.** `freshcheck.py` over all 9750 roster entries
against the 7 September export: 25 carry settlement wording, the same 25 already examined,
every one about a different statement on the same entry. None of the 76 new entries is among
them.
