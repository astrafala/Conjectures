#!/usr/bin/env python3
"""Write JSON so a second writer cannot leave a torn file behind.

Two processes writing one file with `json.dump(open(f, 'w'))` do not merely race for the last
word: the loser's partial output is interleaved with the winner's and the result parses as
nothing at all. Two of the second-conjecture sweep's shard files were destroyed that way when
a foreground run was started on shards a background runner already owned.

Writing to a temporary file in the same directory and renaming it over the target makes the
replacement atomic on POSIX, so a reader sees either the old file or the new one and never a
half of each. The shard files are progress and are rebuildable, but a torn file also stops the
sweep that reads it, and that is a whole run lost for nothing.
"""
import json
import os
import tempfile


def dump(obj, path, **kw):
    d = os.path.dirname(os.path.abspath(path)) or '.'
    fd, tmp = tempfile.mkstemp(dir=d, prefix='.tmp-', suffix='.json')
    try:
        with os.fdopen(fd, 'w') as fh:
            json.dump(obj, fh, **kw)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def load(path, default=None):
    """read, tolerating a file an older non-atomic writer already tore"""
    try:
        return json.load(open(path))
    except FileNotFoundError:
        return default
    except ValueError:
        return default
