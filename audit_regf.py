#!/usr/bin/env python3
"""Re-run the generating-function pipeline, from scratch, on the roster's symbolic papers.

These papers are not walk counts, so audit_deep cannot rebuild them. What can be redone is
the derivation itself: regf.py is the driver that produced them, and running it again on
today's export re-reads the entry's own generating function, re-derives the residual, and
re-checks the conjecture on the terms. A paper whose conjecture no longer comes back PROVED
is flagged for reading rather than trusted.
"""
import json, os, sys, collections
SC = '/tmp/claude-0/-home-user-Conjectures/a6c6c48d-a8e1-5e03-bfd7-16e8d9d94539/scratchpad'
w, N = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 1)
os.environ['RES'] = 'audit_regf_w%d.json' % w
os.environ.setdefault('PER', '120')
import regf

st = json.load(open(SC + '/status.json'))
todo = sorted(a for a, v in st.items()
              if v in ('symbolic engine, no numeric rebuild', 'claim is not a plain recurrence'))
todo = [a for i, a in enumerate(todo) if i % N == w]
regf.main(todo)
