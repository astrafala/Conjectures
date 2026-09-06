# The ten-thousand deep check

A single pre-planned pass over everything — every paper, every engine, every reading,
every comment, every number, every word, and the way the work itself is done.

**[PLAN.md](PLAN.md)** is the plan, written down in advance so that the check cannot be
shaped by what is convenient when it fires. Thirteen phases, none optional.

It runs on its own the moment the roster passes **10,000** settled conjectures.
`engine/src/dc_gate.py` holds that condition, so it is code rather than a note somebody
has to remember:

```
$ python3 src/dc_gate.py
9115 papers; the deep check is not due (885 to go)
```

The mechanical phases are already written and are run as ordinary checks in the meantime,
which is the point of writing them early — Phase 1 found 173 comments with no date on the
day it was written.

| Script | Phase |
| --- | --- |
| `engine/src/dc_gate.py` | the trigger |
| `engine/src/dc_phase1.py` | inventory integrity |
| `engine/src/dc_phase2.py` | content that must not be in a paper |

When the check runs it writes `REPORT.md` here: every phase, every count, every defect,
the fix, and the commit that made it.
