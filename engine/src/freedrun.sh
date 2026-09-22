#!/bin/sh
# The entries that are askable at 8,000,000 RIGHT NOW: their cap row records a refusal at a
# smaller cap, they carry a conjecture, they are still open, and an engine reads them. The list
# is `deep-check/cap-askable.json' / `cap-freed.txt', regenerated from `uniall_caps.json'
# whenever the refusal files change.
#
# It began as the 1,110 that defect 69 freed from `done', on an estimate of "29 of 40 prove"
# that was drawn from the first forty of a SORTED list and skipped the openness check the sweep
# does first. Tested properly, that estimate was zero: 349 of the 396 refuse at the build even
# at 8,000,000, 46 are settled on their own page. The list here is now the honest residue --
# entries whose recorded refusal is below this runner's cap, so the cap skip lets them through
# and the question has actually never been put to them at this setting.
#
# Asked directly rather than waiting for the main sweep, which runs at CAP=2,000,000 and would
# skip every one of them: that is exactly the cap their rows record.
cd /home/user/Conjectures/engine
for r in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  _t0=$(date +%s)
  _pids=""
  for i in 0 1 2; do
    ANUMS_FILE=deep-check/cap-freed.txt BUDGET=300 TAG=freed MEMGB=5 \
      timeout 1700 python3 src/sweep_shard.py 8000000 $i 3 >> /tmp/freed_$i.log 2>&1 &
    _pids="$_pids $!"
  done
  _rc=0
  for _p in $_pids; do
    if wait "$_p"; then :; else _s=$?; [ $_s -ne 124 ] && _rc=$_s; fi
  done
  _el=$(( $(date +%s) - _t0 ))
  # defect 52: a crash ends in seconds and so does an empty vein; the exit code tells them apart
  if [ $_rc -ne 0 ] && [ $_rc -ne 124 ]; then
    echo "round FAILED with exit $_rc after ${_el}s -- a crash, NOT an empty vein; stopping"
    break
  fi
  if [ $_el -lt 60 ]; then
    echo "round found nothing in ${_el}s -- the freed list is read out, stopping"
    # defect 65: say WHY this stopped, so restart_all does not undo an idle backoff.
    date +%s > "/tmp/$(basename "$0").readout"
    break
  fi
done
