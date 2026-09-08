#!/bin/sh
# Start every long-running job that is not already running. Idempotent: safe to run on every
# wake-up, and the guard is what stops a second copy of a sweep from being launched on top of
# a live one -- two writers on one hits file destroy each other's results.
cd /home/user/Conjectures/engine
running() { ps -eo args | grep -q "[/]tmp/$1"; }
start() { running "$1" || { nohup /bin/sh "/tmp/$1" >/dev/null 2>&1 & echo "started $1"; }; }
[ -f /tmp/forever.sh ] || cp src/forever.sh /tmp/forever.sh
start forever.sh
start p5cap.sh
start tails2.sh
start p12run.sh
ps -eo args | grep -oE "src/[a-z_0-9]+\.py" | sort | uniq -c | sort -rn
