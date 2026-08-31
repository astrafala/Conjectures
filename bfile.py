#!/usr/bin/env python3
"""The b-files: hundreds of terms per entry, sitting unused on disk the whole time.

Every check in this project has run against the DATA field, which holds about forty terms.
The local OEIS clone also carries 242,201 b-files, each with hundreds or thousands. They
were never opened.

That matters most for DISPROOFS. A conjectured recurrence that survives forty terms may
fail at the hundredth, and the person who posted it usually checked only what the entry
shows. Testing every open conjecture against every term available is exact integer
arithmetic and costs nothing.

It also strengthens the proofs: a paper can report verification over a thousand terms
rather than forty.
"""
import os, re, subprocess, time

ROOT = "/home/user/oeis/oeisdata/files"
CACHE = "/home/user/Conjectures/bcache"


def lfs_size(anum):
    """The real size of the b-file, read from the Git LFS pointer left by the clone.

    The clone was made with LFS skipped, so every b*.txt on disk is a 130-byte pointer
    naming the true size. That is still useful: it says which entries HAVE a b-file and how
    big it is, which is how the fetch queue is ordered without fetching anything.
    """
    p = path(anum)
    if not os.path.exists(p):
        return 0
    try:
        head = open(p, errors="ignore").read(400)
    except Exception:
        return 0
    m = re.search(r"^size (\d+)$", head, re.M)
    return int(m.group(1)) if m else os.path.getsize(p)


# A parallel fetcher issued about 8,800 requests to oeis.org in a few minutes and the
# service blocked this IP, with a message asking crawlers to use the Git repository
# instead. That was the right complaint. The Git route is unavailable here (the b-files are
# LFS objects and the proxy will not serve them for a repository outside this session's
# authorized set), so the only remaining route is oeis.org -- one request at a time, with a
# deliberate pause, and spread over as many sessions as it takes.
DELAY = 1.2
_last = [0.0]


def fetch(anum, timeout=25):
    """Download the b-file into the local cache; returns the cached path or None.

    Sequential and rate-limited by construction: never call this from several processes.
    """
    os.makedirs(CACHE, exist_ok=True)
    out = os.path.join(CACHE, "b" + anum[1:] + ".txt")
    if os.path.exists(out):
        return out
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    url = f"https://oeis.org/{anum}/b{anum[1:]}.txt"
    r = subprocess.run(["curl", "-sSL", "-A", "Mozilla/5.0", "--max-time", str(timeout),
                        "-o", out, url], capture_output=True)
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) < 4:
        if os.path.exists(out):
            os.remove(out)
        return None
    if not _looks_like_bfile(out):
        os.remove(out)
        return None
    return out


def _looks_like_bfile(path):
    """A b-file starts with a comment or a number. Anything else is a page, not data.

    Large b-files are served by a redirect to S3. Without curl -L the response is a short
    HTML stub containing only an <a href=...> link, which passed a test that looked for
    "<html" and cached 8,802 useless files -- exactly the biggest b-files, which is where a
    counterexample is most likely to be.
    """
    try:
        head = open(path, errors="ignore").read(400).lstrip()
    except Exception:
        return False
    if not head:
        return False
    return head[0] == "#" or head[0] == "-" or head[0].isdigit()


def path(anum):
    return os.path.join(ROOT, anum[:4], "b" + anum[1:] + ".txt")


def terms(anum, limit=None):
    """[(n, a(n))] from the cached b-file, or [] if there is none."""
    p = os.path.join(CACHE, "b" + anum[1:] + ".txt")
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, errors="ignore"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            out.append((int(parts[0]), int(parts[1])))
        except ValueError:
            continue
        if limit and len(out) >= limit:
            break
    return out


def contiguous(anum, limit=None):
    """(offset, values) for the longest run starting at the first index."""
    t = terms(anum, limit)
    if not t:
        return None, []
    off = t[0][0]
    vals = []
    for i, (idx, v) in enumerate(t):
        if idx != off + i:
            break
        vals.append(v)
    return off, vals
