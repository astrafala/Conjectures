# Pending batch notes

Batch notes are appended here by the hourly working routine and folded into `LEDGER.md` by the
daily one. Everything written up to and including 20 September 2026 has been folded; this file
holds no unfolded notes.

## 20 September 2026 (later) — the transfer21 vein read out in full

`uniform.build` now dispatches `transfer21` to `transfer17.build_pairfree`, verified on 243
shapes with zero mismatches. The whole capped `transfer21` population has since been asked, and
the reading is complete:

| | |
|---:|---|
| 78 | capped off-roster `transfer21` entries |
| **5** | proved and installed |
| 73 | asked again and still over the cap |
| 0 | left unasked |

Fifteen of the 78 carried a conjecture and all fifteen were refused a priori by
`transfer17.build`'s `(alpha+1)^(2W) > cap` test and by nothing else. **Five of those fifteen
now build and prove**; the other ten exceed the cap for real, not a priori. At `W=7` over
alphabet `0..2` the pair test demands `3^14 = 4,782,969` against a cap of two million, and the
pair-free build returns the same sequence in 663,553 states — so the a-priori refusal was
wrong about five entries and right about ten.

That is the honest shape of it. The swap was worth making and is permanent, and it bought five
results rather than fifteen.
