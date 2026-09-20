#!/bin/sh
# Deep check Phase 5, the mathematics recomputed from cold, put back into the rotation.
#
# restart_all.sh says "p5last.sh and p12run.sh were dropped once Phases 5 and 12 finished".
# Phase 5 had not finished. Its `ok' count has stood at 3,847 since 8 September while its total
# -- derived from every non-FAILS hit in uniall_hits.json that carries coeffs and an engine --
# has gone on growing with every sweep, and today's sweeps alone pushed it from 5,942 to 5,971.
# The status line has read "left 2,100" all day.
#
# 2,100 results whose model, threshold and exactness have never been rebuilt in a fresh process.
# That is not a search for new results; it is whether the ones already counted are right, which
# matters more. A runner switched off on the belief that it was done is the same defect as a
# refusal list nobody re-read (STATE.md defects 34, 40, 41) -- something was recorded as
# finished, and the machinery that would have shown otherwise was the thing turned off.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  for i in 0 1 2; do
    P5CAP=8000000 timeout 1700 python3 src/dc_phase5.py $i 3 300 >> /tmp/p5run_$i.log 2>&1 &
  done
  wait
done
