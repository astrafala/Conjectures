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
