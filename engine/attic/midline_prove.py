#!/usr/bin/env python3
"""Run the residual test over the mid-line generating function entries."""
import json, os
import scan_prove

if __name__ == "__main__":
    scan_prove.json.load = scan_prove.json.load     # no-op, keeps the import honest
    orig = json.load
    def patched(fp, *a, **k):
        return orig(fp, *a, **k)
    os.environ.setdefault("REDO", "1")
    # point the sweep at the mid-line cache
    src = open("scan_prove.py").read()
    src = src.replace('json.load(open("scan-cache.json"))',
                      'json.load(open(os.environ.get("CACHE", "scan-cache.json")))')
    ns = {"__name__": "midline"}
    exec(compile(src, "scan_prove_patched", "exec"), ns)
    ns["main"]()
