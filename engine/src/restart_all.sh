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
# Anchored, because a substring match sees any process that merely MENTIONS the path. A shell
# whose command line happened to contain the words /tmp/p5run.sh was enough to make this report
# that p5run.sh was already up, and restart_all.sh then skipped the one runner the machine had
# been cleared for. Nothing said so: a skipped runner and a running one print the same nothing.
# start() launches exactly `/bin/sh /tmp/<name>', so match that and not a substring of it.
running() { ps -eo args | grep -qE "^(/bin/)?sh /tmp/$1( |$)"; }
# The copy belongs INSIDE the guard, and both halves of that matter. It must not be skipped when
# /tmp/$f already exists -- that guard meant an edited runner did not take effect until the next
# container restart, so tonight's idle backoff would have sat in src/ unused for an hour. And it
# must not overwrite a runner that is RUNNING: /bin/sh reads a script lazily by byte offset, so
# rewriting it underneath a live shell makes it resume at whatever now sits at that offset.
# Copying only when the runner is not running satisfies both.
# DEFECT 65. The idle backoff and this restarter were fighting, and the restarter won once
# per firing. Every runner stops itself when a round finds nothing -- that is defect 44, and
# it is right -- and then this relaunched it, because "not running" was the only test. With
# 33 runners the container reached a load average of 46 on 4 cores, which is where defect 64
# came from: a wall-clock BUDGET on a machine at 11x oversubscription is worth a fraction of
# itself, and the shortfall was being written into uniall_tmo.json and read back as the
# entry's difficulty.
#
# A runner that stopped because its vein was read out now says so, in /tmp/<name>.readout,
# and is left alone for READOUT_HOLD seconds. A runner that CRASHED writes no marker and is
# restarted immediately, which is exactly the distinction defect 52 exists to make -- the two
# look identical from the outside and must not be treated alike.
#
# An hour is chosen to match the wake-up rhythm: long enough to stop the churn, short enough
# that a changed engine, a raised budget or a widened pool is picked up on the next firing.
# Clearing the marker by hand (or a container restart wiping /tmp) re-tries everything, which
# is what should happen after an engine changes.
READOUT_HOLD=${READOUT_HOLD:-3600}
readout() {
  m="/tmp/$1.readout"
  [ -f "$m" ] || return 1
  t=$(cat "$m" 2>/dev/null) || return 1
  n=$(date +%s)
  [ $(( n - t )) -lt "$READOUT_HOLD" ]
}
# returns 0 only when it actually LAUNCHED something, so the cap below counts launches and
# not holds. Returning 0 for a hold made a firing that held eight read-out runners think it
# had started eight and stop looking, which is the opposite of what the cap is for.
start() {
  running "$1" && return 1
  if readout "$1"; then
    echo "held  $1 (read out $(( $(date +%s) - $(cat /tmp/$1.readout) ))s ago)"
    return 1
  fi
  cp "src/$1" "/tmp/$1"
  nohup /bin/sh "/tmp/$1" >/dev/null 2>&1 &
  echo "started $1"
  return 0
}
RUNNERS="forever.sh tails3.sh gfrun.sh readable.sh lexrun.sh lexcf.sh mfrun.sh tabrun.sh wordrun.sh cusprun.sh ecarun.sh gfdefrun.sh gdrun.sh fcfrun.sh sndrun.sh ca2drun.sh b8run.sh lrrun.sh cfpoolrun.sh galrun.sh degrun.sh precrun.sh zeilbrun.sh np2run.sh caprun.sh rcaprun.sh resrun.sh oomrun.sh t17run.sh t21ckrun.sh tmorun.sh p5run.sh bsweeprun.sh capwhyrun.sh freedrun.sh galwhyrun.sh galraysrun.sh"

# DEFECT 66, and it is defect 65's feedback loop closing on itself. Starting all 33 runners
# at once, each with 2-6 shards, put 92 python processes and 42 sweep_shard instances on FOUR
# cores: load average 56, about 0.04 cores each. At that point nothing finishes, every
# wall-clock budget is worth a fortieth of itself (defect 64), and -- the part that makes it
# self-sustaining -- the idle backoff cannot fire either, because it declares a vein read out
# only when a round returns in under 60 seconds, and under this load even an empty round
# cannot start four interpreters that fast. The machine was too busy to notice it had nothing
# to do.
#
# So the number started per firing is capped, and the starting point rotates, so every runner
# gets its turn across successive wake-ups rather than all of them fighting on every one.
# Runners already up are not counted against the cap -- the cap is on new work, not on total
# work -- and the read-out hold above still applies first.
MAXSTART=${MAXSTART:-8}
# DEFECT 67. Capping the runners STARTED per firing is not a cap on what is running. Each
# runner spawns 2-6 shards and the firings come every minute or two, so eight new runners a
# firing still climbed back to 74 python jobs on 4 cores -- 18x oversubscribed, which is the
# state defect 64 measured and defect 66 explained. The quantity that matters is the number
# of jobs ALREADY running, so that is what is checked: above MAXJOBS this firing starts
# nothing and lets the machine drain. Six jobs per core is the ceiling; the sweeps are
# CPU-bound, so beyond that every extra process only makes every BUDGET worth less.
# Lowered from 24 to 12 on 22 September, on evidence rather than taste: over several merges
# in a row the twenty-six running sweep shards returned "0 new hits" while walking their skip
# lists, and the measurement work that IS producing findings -- classifying galcoord's 355
# declines, which is where the frontier actually is -- was getting a ninth of a core. Three
# jobs per core instead of six. The sweeps are not retired, they drain as their rounds end and
# the rotation brings them back; what changes is that they stop crowding out the work that has
# somewhere to go.
MAXJOBS=${MAXJOBS:-12}
_jobs=$(ps -eo args | grep -c 'python3 src/')
if [ "$_jobs" -ge "$MAXJOBS" ]; then
  echo "holding all starts: $_jobs python jobs already running (MAXJOBS=$MAXJOBS), load $(cut -d' ' -f1 /proc/loadavg) on $(nproc) cores"
  exit 0
fi
OFFFILE=/tmp/restart_all.offset
off=$(cat "$OFFFILE" 2>/dev/null || echo 0)
case "$off" in ''|*[!0-9]*) off=0 ;; esac
n=0; i=0; started=0
set -- $RUNNERS
total=$#
while [ $i -lt $total ]; do
  idx=$(( (off + i) % total ))
  f=$(echo $RUNNERS | cut -d' ' -f$(( idx + 1 )))
  i=$(( i + 1 ))
  if start "$f"; then started=$(( started + 1 )); fi
  if [ $started -ge $MAXSTART ]; then break; fi
done
echo $(( (off + i) % total )) > "$OFFFILE"
echo "load $(cut -d' ' -f1 /proc/loadavg) on $(nproc) cores; $(ps -eo args | grep -c 'python3 src/') python jobs" 
ps -eo args | grep -oE "src/[a-z_0-9]+\.py" | sort | uniq -c | sort -rn
