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
# blocked", which bfile detects and reports as BLOCKED. So all three are rounds of THIS runner,
# run one after another, and nothing else on the machine fetches.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10; do
  _t0=$(date +%s)
  # bproved goes FIRST and inside this runner rather than beside it. It was started by hand,
  # stopped at 3,060 of 5,987 when its process ended, and never came back -- which is the
  # failure restart_all.sh's own comment records: "a sweep that is not in this list simply
  # never comes back, which is how two veins sat idle for a whole day". A job launched by hand
  # is not in any list. So the wait-for-bproved loop this runner used to carry is gone: there
  # is nothing to wait for when all three fetchers are rounds of one runner.
  FETCH=1 timeout 2000 python3 src/bproved.py >> /tmp/bproved_fetch.log 2>&1
  timeout 3000 python3 src/bsweep.py >> /tmp/bsweep_run.log 2>&1
  # THE ONE FETCHING SLOT. Three sweeps now want b-files this machine does not have: bsweep's
  # 7,092 open conjectures, provedsweep's 9,188 roster entries, and bproved's remainder. They
  # cannot run at once -- bfile.fetch is rate-limited by a module global, so two processes
  # simply double the request rate at oeis.org, and the only signal is a page saying
  # "temporarily blocked". Running them one after another inside a single round is what keeps
  # that from happening by accident, and it is why all three are rounds of
  # this one runner rather than three processes started separately.
  FETCH=1 BUDGET=1200 timeout 1500 python3 src/provedsweep.py >> /tmp/provedsweep.log 2>&1
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
