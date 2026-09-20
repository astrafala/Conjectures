#!/bin/sh
# Start every long-running job that is not already running. Idempotent: safe to run on every
# wake-up, and the guard is what stops a second copy of a sweep from being launched on top of
# a live one -- two writers on one hits file destroy each other's results.
#
# p12run.sh was dropped once Phase 12 finished. p5last.sh was dropped on the same belief about
# Phase 5 and the belief was wrong: its ok count has stood at 3,847 since 8 September while
# its total grew with every hit, and 2,100 results have never been recomputed from cold. It is
# back as p5run.sh. A runner with nothing
# left to do still takes its share of the CPU away from the sweeps that do have work.
# livenew.sh is not here either -- the live re-check has nothing to read until a sweep has
# found something, so it belongs in the batch, not in the rotation.
cd /home/user/Conjectures/engine
# every runner belongs here: a container restart wipes /tmp, and a sweep that is
# not in this list simply never comes back -- which is how two veins sat idle for
# a whole day earlier in this project.
for f in forever.sh tails3.sh gfrun.sh readable.sh lexrun.sh lexcf.sh mfrun.sh tabrun.sh wordrun.sh cusprun.sh ecarun.sh gfdefrun.sh gdrun.sh fcfrun.sh sndrun.sh ca2drun.sh b8run.sh lrrun.sh cfpoolrun.sh galrun.sh degrun.sh precrun.sh zeilbrun.sh np2run.sh caprun.sh rcaprun.sh resrun.sh t21run.sh oomrun.sh p5run.sh; do
  [ -f "/tmp/$f" ] || cp "src/$f" "/tmp/$f"
done
running() { ps -eo args | grep -q "[/]tmp/$1"; }
start() { running "$1" || { nohup /bin/sh "/tmp/$1" >/dev/null 2>&1 & echo "started $1"; }; }
for f in forever.sh tails3.sh gfrun.sh readable.sh lexrun.sh lexcf.sh mfrun.sh tabrun.sh wordrun.sh cusprun.sh ecarun.sh gfdefrun.sh gdrun.sh fcfrun.sh sndrun.sh ca2drun.sh b8run.sh lrrun.sh cfpoolrun.sh galrun.sh degrun.sh precrun.sh zeilbrun.sh np2run.sh caprun.sh rcaprun.sh resrun.sh t21run.sh oomrun.sh p5run.sh; do
  start "$f"
done
ps -eo args | grep -oE "src/[a-z_0-9]+\.py" | sort | uniq -c | sort -rn
