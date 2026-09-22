# Pending batch notes

Batch notes are appended here by the hourly working routine and folded into `LEDGER.md` by the
daily one.

## 22 September 2026 (morning) — A253494, and an honest note on how small the claim is

**A253494**, `transfer31`, S=48,293, roster 13,791 → 13,792. Its conjecture is
`a(n) = 6a(n-1) - 11a(n-2) + 6a(n-3) for n>6` — characteristic roots 1, 2 and 3 — and the entry
carries two other `Empirical:` lines saying the same thing a different way, a closed form
`49*3^(n-1) + 5322*2^(n-1) + 38777` and Colin Barker's generating function with denominator
`(1-x)(1-2x)(1-3x)`.

**Said plainly: this is a small claim.** An order-3 recurrence whose roots are 1, 2, 3 is about
as simple a linear structure as this vein produces, and the entry's own closed form makes that
visible to anyone reading it. The work is still real — a proof has to show the count satisfies
the recurrence, which is what the 48,293-state transfer matrix does, and the entry says
"Empirical" three times — but nobody should read it as a surprising structure.

Its DATA guard read **16** terms, so this one has an empirical check of its own and did not need
the b-file fallback.

## 22 September 2026 — correction: the clock runner DID produce a result

I said several times, and it went into LEDGER.md's 21–22 September section as
*"the re-settinged cap and clock runners have produced nothing at all"*, that none of the
runners whose lists and settings were fixed overnight had yielded anything.

**That is wrong for `tmorun`.** A253494 was on `deep-check/tmolist.txt` — it is absent from the
current file only because the roster strip removed it once it was papered, and git history
confirms it was there at the time. The runner's `PROVED: 1` for this generation is that entry.

So the budget raise paid. `tmorun` asked at `BUDGET=300` against a list where **39 of its 62
entries carried a `uniall_tmo` row of exactly 300** — the vein whose whole subject is the clock,
re-asking at a budget already known to be too short. Raised to 500, it proved A253494.

The claim stands for the others: `caprun`, `rcaprun` and `resrun` have still produced nothing,
and `t21run` turned out to be asking nothing at all (defect 57) and is retired. **The next daily
fold should amend the 21–22 September section accordingly** — the sentence as written is false.

What the veins are refusing now, which is the more useful half: across all six runners the
dominant reason this generation is *out of budget on an earlier pass* — 19, 4, 3, 15 and 28 of
their asked entries respectively. **The clock, not the cap, is what is holding the remaining
pool**, and every one of those rows was written at a budget the runner has already raised past
once.
