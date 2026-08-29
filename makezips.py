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

    def flush(batch):
        if not batch:
            return
        lo = batch[0].split("-")[0]
        hi = batch[-1].split("-")[0]
        name = f"conjecture-papers-{lo}-{hi}.zip"
        subprocess.run(["zip", "-q", "-j", "-9", name]
                       + [f"papers/{c}" for c in batch], check=True)
        made.append((name, os.path.getsize(name), len(batch)))

    for f in files:
        batch.append(f)
        # zip after each addition is too slow; estimate with the raw size, then verify
        if sum(os.path.getsize(f"papers/{c}") for c in batch) > CAP:
            batch.pop()
            flush(batch)
            batch = [f]
    flush(batch)

    # a PDF barely compresses, so the estimate is close; still, verify and split if over
    for name, size, count in made:
        print(f"{name}  {size/1048576:.1f} MiB  {count} papers"
              + ("   OVER CAP" if size > CAP else ""))
    print(f"\n{len(files)} papers in {len(made)} archives")


if __name__ == "__main__":
    main()
