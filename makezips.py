#!/usr/bin/env python3
"""Package every paper for delivery, 100 per archive."""
import os, subprocess, sys

PER = int(os.environ.get("PER_ZIP", "100"))


def main():
    files = sorted(os.listdir("papers"), key=lambda f: int(f.split("-")[0]))
    for f in os.listdir("."):
        if f.startswith("conjecture-papers-") and f.endswith(".zip"):
            os.remove(f)
    made = []
    for i in range(0, len(files), PER):
        chunk = files[i:i + PER]
        lo = chunk[0].split("-")[0]
        hi = chunk[-1].split("-")[0]
        name = f"conjecture-papers-{lo}-{hi}.zip"
        subprocess.run(["zip", "-q", "-j", name] + [f"papers/{c}" for c in chunk],
                       check=True)
        made.append((name, os.path.getsize(name) / 1048576))
    for name, mb in made:
        print(f"{name}  {mb:.1f} MiB")
    print(f"{len(files)} papers in {len(made)} archives")


if __name__ == "__main__":
    main()
