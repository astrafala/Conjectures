#!/bin/sh
# The cusp-form dimension family: 51 entries settled by a classical closed formula rather than
# by any transfer matrix. Every sweep reads them now.
cd /home/user/Conjectures/engine
# IDLE BACKOFF (defect 44). A round of this loop that finds work takes minutes -- BUDGET
# alone is 90 seconds or more -- so a round that returns in seconds found nothing, and the
# only thing relaunching it achieves is another interpreter start. Thirteen veins were doing
# exactly that at once: /tmp was wiped by a container restart at 02:00 and by 02:05 the runner
# logs held about twenty-five thousand lines, almost all of them the empty result dict, while
# Phase 5 -- the one job with 1,904 entries of real work left -- wrote nothing for an hour.
# Reading the clock needs nothing from the sweep and so works for every script below, not just
# sweep_shard. Stopping is not retirement: restart_all.sh relaunches this an hour from now,
# which is when a changed engine could have reopened the vein.
for r in 1 2 3 4 5 6 7 8; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/cusp.txt BUDGET=120 \
      timeout 1700 python3 src/sweep_shard.py 200000 $i 3 >> /tmp/cusp_$i.log 2>&1 &
  done
  wait
  for i in 0 1; do
    TARGETS=cusp_cands.json HITS=cuspcf_hits_$i.json DONE=cuspcf_done_$i.json \
      CFSHARD=$i CFNSHARD=2 BUDGET=120 \
      timeout 1700 python3 src/sweep_cf.py 200000 >> /tmp/cuspcf_$i.log 2>&1 &
  done
  wait
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/cusp.txt BUDGET=120 SCUT=20000 \
      timeout 1700 python3 src/ordtails.py 200000 $i 3 >> /tmp/cuspt_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  # `wait' with NO OPERANDS is specified to return zero, always -- so reading $? after it
  # tells you nothing about the shards, and the defect-52 check was inert in every runner
  # that launches more than one. Waiting on each pid in turn is the portable way to get a
  # status back. 124 is `timeout' doing its job, not a crash.
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # DEFECT 52. A round that ends in seconds was read as "nothing left to ask". A round that
  # ends in seconds because the sweep CRASHED ends in seconds too, and said the same thing.
  # bsweep.py died on its first entry with AttributeError on 31 August and sat at 3,376 of
  # 10,632 for three weeks looking like a half-read queue; the moment it was put in a runner
  # the backoff would have called that queue read out. An exit code tells the two apart for
  # nothing: 0 is a clean round, 124 is `timeout' doing its job, anything else is a crash and
  # must never be mistaken for an empty vein.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- read out under the current engines, stopping"
    break
  fi
done
