#!/bin/sh
# The open-conjecture b-file sweep, restarted after three weeks and made to wait its turn.
#
# bsweep_results.json holds 3,376 of a 10,632-entry queue and was last written on 31 August.
# 7,256 open conjectured recurrences have never been checked against their b-files -- the
# largest untouched population in the project. The one disproof the first 3,376 produced
# (A076217) is already papered as ledger 2430, so the vein is not empty, only unread.
#
# IT MUST NOT RUN WHILE ANYTHING ELSE IS FETCHING. bfile.fetch is rate-limited by a module
# global and is documented as single-process; two downloaders share no such global, so they
# double the request rate against OEIS and the only signal is a page saying "temporarily
# blocked", which bfile detects and reports as BLOCKED. So this waits for bproved's fetch to
# finish before it starts, and checks again between rounds.
cd /home/user/Conjectures/engine
waitfetch() {
  while ps -eo args | grep -q '[b]proved\.py'; do
    sleep 60
  done
}
for r in 1 2 3 4 5 6 7 8 9 10; do
  waitfetch
  _t0=$(date +%s)
  timeout 3000 python3 src/bsweep.py >> /tmp/bsweep_run.log 2>&1
  _rc=$?
  _el=$(( $(date +%s) - _t0 ))
  # IDLE BACKOFF (defect 44). A round that returns in seconds found nothing left to ask.
  # DEFECT 52. A round ending in seconds because the sweep CRASHED looks exactly like a round
  # ending in seconds because there was nothing to ask. bsweep.py died on its first entry on
  # 31 August and sat at 3,376 of 10,632 for three weeks looking like a half-read queue.
  # 0 is a clean round, 124 is `timeout' doing its job, anything else is a crash.
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- this is a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- queue read out, stopping"
    break
  fi
done
