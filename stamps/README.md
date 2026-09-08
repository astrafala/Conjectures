# Timestamps

Each pair here is a snapshot of the roster and its OpenTimestamps proof:

| file | what it is |
| --- | --- |
| `MANIFEST-<date><letter>.tsv` | the roster exactly as it stood, one line per result, with the SHA-256 of every paper |
| `MANIFEST-<date><letter>.tsv.ots` | a proof that that exact file existed on that date, anchored in the Bitcoin blockchain |

Check any of them with:

```
pip install opentimestamps-client
ots verify stamps/MANIFEST-2026-09-08a.tsv.ots
```

A stamp reads "pending confirmation" for a few hours after it is made; that is the calendar
servers waiting for a Bitcoin block. `ots upgrade <file>.ots` completes the proof once it is
in, and from then on it can be checked with no server at all.

**Both the manifest and its stamp must be kept.** A proof of a hash is worthless without the
file that hashes to it, so the old manifest is never overwritten -- a new one is added.
