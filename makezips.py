#!/usr/bin/env python3
"""Package every paper for delivery, packing each archive as full as the send limit
allows so there are as few archives as possible.

Papers are added in numerical order and an archive is closed only when the next paper
would push it past the cap, so the numbering stays contiguous within each archive.
"""
import os, subprocess, sys

CAP = int(float(os.environ.get("CAP_MIB", "28")) * 1024 * 1024)


def main():
    files = sorted(os.listdir("papers"), key=lambda f: int(f.split("-")[0]))
    for f in os.listdir("."):
        if f.startswith("conjecture-papers-") and f.endswith(".zip"):
            os.remove(f)
    made, batch = [], []

    def zip_of(batch, name):
        if os.path.exists(name):
            os.remove(name)
        # PDFs are already compressed, so -9 buys almost nothing and costs a great deal:
        # the shrink loop below re-zips the whole batch each time it drops a paper, and at
        # -9 that turned a fifteen-minute pack into hours. The cap is still checked on the
        # ACTUAL size, so a weaker setting cannot produce an oversized archive.
        subprocess.run(["zip", "-q", "-j", "-1", name]
                       + [c for c in batch], check=True)
        return os.path.getsize(name)

    def flush(batch):
        """Write the archive, shrinking it until the ACTUAL size is within the cap.

        Capping the raw total instead left every archive several MiB short, because a
        PDF still compresses a little; the delivery limit applies to the compressed size.
        Whatever has to come off the end is RETURNED, so it opens the next archive
        instead of being lost -- dropping it silently left a hole in the numbering.
        """
        dropped = []
        while batch:
            lo, hi = batch[0].split("-")[0], batch[-1].split("-")[0]
            name = f"conjecture-papers-{lo}-{hi}.zip"
            size = zip_of(batch, name)
            if size <= CAP or len(batch) == 1:
                made.append((name, size, len(batch)))
                return dropped
            os.remove(name)
            dropped.insert(0, batch.pop())
        return dropped

    carry = []
    for f in files:
        batch.append(f)
        # a PDF barely compresses, so the raw total is a close estimate of the archive
        # size: bounding it at the cap itself means the shrink loop below almost never
        # fires. Bounding it at 1.25*CAP instead made every archive start ~7 MiB too big
        # and re-zip the whole batch once per dropped paper, which is where the pack time
        # went.
        if sum(os.path.getsize(c) for c in batch) > CAP:
            batch.pop()
            batch = flush(batch) + [f]
    while batch:
        batch = flush(batch)

    # a PDF barely compresses, so the estimate is close; still, verify and split if over
    for name, size, count in made:
        print(f"{name}  {size/1048576:.1f} MiB  {count} papers"
              + ("   OVER CAP" if size > CAP else ""))
    print(f"\n{len(files)} papers in {len(made)} archives")


if __name__ == "__main__":
    main()
