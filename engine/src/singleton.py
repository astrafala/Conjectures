#!/usr/bin/env python3
"""Refuse to run a second copy of a script that has a single output.

Three scripts in one session were started twice by accident -- rank.py, sync_sources.py and
paperdates.py -- and each time the two copies fought over the same directory or cache. Two
of them died; the third silently did the work twice. The pattern is always the same, so it
is written once here instead of a fourth time.

    import singleton; singleton.claim('paperdates')

A stale lock left by a killed process is ignored: the check is whether that pid still exists.
"""
import atexit
import os

import repopaths


def claim(name):
    lock = os.path.join(repopaths.ROOT, 'engine', f'.{name}.lock')
    if os.path.exists(lock):
        try:
            other = int(open(lock).read().strip())
        except Exception:
            other = None
        if other is not None and other != os.getpid() and os.path.exists(f'/proc/{other}'):
            raise SystemExit(f'{name} (pid {other}) is already running; refusing to start')
    open(lock, 'w').write(str(os.getpid()))
    atexit.register(lambda: os.path.exists(lock) and os.remove(lock))
