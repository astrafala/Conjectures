# Priority, attribution, and what to do if someone posts one of these

**Author:** Adrian Perez Fontelles, independent researcher.
**First public location:** this repository.
**Licence:** CC BY 4.0 — see `LICENSE`. You may reuse and adapt anything here, including
commercially, **provided you credit Adrian Perez Fontelles**.

## What is and is not protected

A licence protects the **writing**: these papers, their text, their proofs as written. It does
not protect a **mathematical fact**. Nobody can own "A123456 satisfies this recurrence", and
nobody should. Two people can prove the same thing independently and both be right.

So the protection here is not a ban. It is a **date** and a **credit requirement**:

* if someone reaches the same result on their own, that is theirs and this changes nothing;
* if someone reads a paper here and then posts it, this repository is the dated public record
  that it was here first, and the licence requires that credit be given.

## The dated record

`MANIFEST.tsv` lists every result in the roster: the OEIS entry it settles, the verdict, the
argument used, the date the paper carries, the path, and the SHA-256 of the PDF. `MANIFEST.sha256`
holds the hash of that file. Anyone can recompute all of it from this repository:

```
cd engine && python3 src/manifest.py     # rewrites MANIFEST.tsv
sha256sum -c MANIFEST.sha256             # checks it matches what was committed
```

Three independent things fix that file to a date:

1. **Git history on GitHub.** Every commit is dated and the push is recorded on GitHub's own
   servers. Commit dates can be set by hand; GitHub's received-push record cannot.
2. **A Zenodo release.** `.zenodo.json` is ready. Linking the repository to Zenodo and cutting
   a GitHub release mints a **DOI** with a fixed publication date, held by CERN, independent of
   GitHub and of me. This is the ordinary academic priority mechanism and it is the single
   strongest step available. **Do this.**
3. **An OpenTimestamps stamp.** Free, no account, anchors the hash of `MANIFEST.tsv` in the
   Bitcoin blockchain, which nobody can backdate:
   ```
   pip install opentimestamps-client
   ots stamp MANIFEST.tsv          # writes MANIFEST.tsv.ots -- commit it
   ots verify MANIFEST.tsv.ots     # anyone can check it, forever
   ```

With the DOI and the stamp, "I had this on 8 September 2026" stops being a claim and becomes a
fact anyone can check without trusting me, GitHub, or each other.

## If someone posts one of these to the OEIS

1. Check the manifest: find the A-number, note the paper's date and the commit that added it.
2. Reply on the entry, politely, citing the DOI and the paper. State that the result was
   published on that date and ask for the attribution the licence requires.
3. If they will not, the OEIS editors can be emailed with the DOI. OEIS takes attribution
   seriously; that is what the record is for.
4. If they got there independently, say so and leave it. Two proofs is not a problem.

## Nothing here has been posted to the OEIS

Not one comment, formula or link. Posting is the author's to do, by hand, when he chooses.
