#!/usr/bin/env python3
"""Run a function with a timeout that actually works.

signal.alarm only fires between Python bytecodes. Sympy spends much of its time inside
compiled routines -- minimal_polynomial, Groebner bases, flint arithmetic -- and a SIGALRM
raised there is not delivered until control returns, which for a genuinely stuck
computation is never. Whole sweeps stalled for hours on a single entry that way, with the
per-item alarm armed and useless.

A child process can be killed by the operating system regardless of what it is doing, so
each item runs in its own process and the parent enforces the wall clock.
"""
import multiprocessing as mp


def _target(q, fn, args, kwargs):
    try:
        q.put(("ok", fn(*args, **(kwargs or {}))))
    except Exception as e:
        q.put(("err", f"{type(e).__name__}: {str(e)[:80]}"))


def call(fn, args=(), kwargs=None, timeout=180):
    """(status, value): status is 'ok', 'err' or 'timeout'."""
    ctx = mp.get_context("fork")
    q = ctx.Queue()
    p = ctx.Process(target=_target, args=(q, fn, args, kwargs))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join(5)
        if p.is_alive():
            p.kill()
            p.join()
        return "timeout", None
    try:
        return q.get_nowait()
    except Exception:
        return "err", "the worker produced no result"
