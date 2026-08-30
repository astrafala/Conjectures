#!/usr/bin/env python3
"""Run a per-item function across several processes, with a real per-item timeout, a
wall-clock budget, and progress saved after every item.

Two things forced this. Background jobs only advance while the session is active, so a
sweep started with nohup makes no progress between turns and has to run in the foreground
in bounded slices. And multiprocessing.Pool workers are daemonic, so they cannot fork the
child that timeoutrun.py needs to kill a computation stuck inside sympy's compiled code.

So the scheduler is written directly: keep WORKERS children alive, each on one item with
its own deadline, harvest results as they finish, and stop when the budget runs out. The
progress file makes the sweep resumable, which is what lets it be sliced at all.
"""
import json, os, time
import multiprocessing as mp


def _target(q, fn, item):
    try:
        q.put(("ok", fn(item)))
    except Exception as e:
        q.put(("err", f"{type(e).__name__}: {str(e)[:100]}"))


def run(fn, items, key, progress, per_item=180, budget=540, workers=4, report=None):
    """fn(item) -> jsonable. key(item) -> a stable id. Returns the progress dict."""
    done = json.load(open(progress)) if os.path.exists(progress) else {}
    todo = [it for it in items if key(it) not in done]
    ctx = mp.get_context("fork")
    live, t0 = {}, time.time()
    i = 0
    while (todo or live) and time.time() - t0 < budget:
        while todo and len(live) < workers and time.time() - t0 < budget:
            it = todo.pop(0)
            q = ctx.Queue()
            p = ctx.Process(target=_target, args=(q, fn, it))
            p.start()
            live[p.pid] = (p, q, it, time.time())
        time.sleep(0.2)
        for pid, (p, q, it, start) in list(live.items()):
            fin = not p.is_alive()
            over = time.time() - start > per_item
            if not (fin or over):
                continue
            res = None
            try:
                res = q.get_nowait()
            except Exception:
                pass
            if p.is_alive():
                p.terminate(); p.join(3)
                if p.is_alive():
                    p.kill(); p.join()
            del live[pid]
            done[key(it)] = res if res else ["timeout", None]
            i += 1
            if report:
                report(it, done[key(it)])
            json.dump(done, open(progress, "w"))
    for p, q, it, s in live.values():
        p.terminate(); p.join(3)
    json.dump(done, open(progress, "w"))
    print(f"  {i} done this slice, {len(done)}/{len(items)} total", flush=True)
    return done
