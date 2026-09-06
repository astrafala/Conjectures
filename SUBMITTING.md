# Getting this checked, and getting credit for it

Written for the author. Everything below needs a login, so none of it is done for you.

---

## If somebody else gets there first

Every paper prints the day it was written, and
[comments/by-date.md](comments/by-date.md) lists every entry in the order it was settled,
earliest first. That file is the priority record.

If a conjecture here is settled and commented on the OEIS by somebody else **after** the
date recorded for it, nothing here is removed and nothing here is wrong: the work was done
on the day the paper says, and that day came first. Post the comment anyway — an entry can
carry more than one proof, and the record shows when each was made.

A paper comes down for one reason only: the result turns out to have been settled **before**
the date on the paper. Then it was never ours, the paper is withdrawn, and the count comes
down with it.

---

## The blunt version

**Nobody is going to review 8887 papers.** Any plan that starts with "publish all of them and
wait for review" ends with nothing happening. There are three realistic routes, and they do
different jobs:

| Route | What it gives you | Effort | Real review? |
| --- | --- | --- | --- |
| **OEIS comments** | Your name on the entry itself, checked by an editor | Slow, ongoing | **Yes** |
| **Zenodo release** | A DOI, a permanent citable record, your name | Ten minutes | No |
| **arXiv** | Visibility to the field, your name | Needs endorsement | No, but read |

Do all three, in that order of importance.

---

## 1. OEIS — this is the one that counts

This is the only route where a human expert actually checks the claim and your name ends up
attached to it permanently.

**The limit is 3 pending submissions at a time.** It was 7 until 2019 and was lowered because
editors were overwhelmed. You can ask for more by writing to `admin@oeis.org`; the OEIS wiki
says people who submit cleanly formatted material usually are not held to 3.

**Before you submit anything, email `admin@oeis.org` and say what you are doing.** Explain that
you have machine-assisted proofs for a large number of empirical recurrences, that you want to
add comments recording them, and ask how they would like it handled. Do this first. Turning up
unannounced and filing thousands of comments on Hardin entries is the fastest way to get your
submissions blocked, and it would be a reasonable reaction on their part.

**Drafts are ready.** [`comments/`](comments/) has one section per entry: the OEIS entry, the
date the result was obtained, the paper that proves it, what the entry still records as
unsettled, and the text proposed for posting. `comments/index.csv` lists all of them.
`comments/submission-order.txt` is an ordered queue: corrections first, because those are the
ones an editor can verify against the entry's own data without trusting anything, then the
named proofs. The first three are A197230, A129454, A141135.

**Post the date with the comment.** An OEIS comment is stamped with the day it is posted. The
date recorded in `comments/` is the day the result was obtained, and it is worth saying so in
the submission so the record is unambiguous.

**Say it is a proof, and say how it was obtained.** The OEIS wiki asks explicitly that you
state whether something is a conjecture or a theorem you can prove. Link the paper. Mention the
work was machine-assisted — it will come out anyway, and volunteering it reads very differently
from being caught at it.

---

## 2. Zenodo — ten minutes, gives you a DOI

Zenodo mints a permanent DOI for a GitHub repository and puts your name on the record. No
review, but it makes the work citable and timestamps your authorship.

1. Sign in at [zenodo.org](https://zenodo.org) with GitHub.
2. Under **GitHub** in your Zenodo settings, flip the switch on `astrafala/Conjectures`.
3. On GitHub, **Releases → Create a new release**, tag it `v1.0`, publish.
4. Zenodo picks it up and issues the DOI within a few minutes.

`.zenodo.json` in this repository already carries the title, your name, the description and the
CC BY licence, so the record comes out right without editing.

**Note:** the repository is about 1.6 GB of PDFs. Zenodo's normal per-record limit is 50 GB, so
this is fine, but the archive will take a while to build.

---

## 3. arXiv — submit ONE paper, not 8887

`OVERVIEW.pdf` is the submittable object: the method, the verification, and the error record,
with the roster as supporting data. Uploading thousands of near-identical papers would be
rejected and would look bad.

- Category: **math.CO**, cross-list **cs.SC**.
- A first submission to math.CO **needs an endorsement** from an existing arXiv author. You
  request it through the arXiv interface and it names people who can give it.
- Link the repository and the DOI from section 2 in the abstract.
- arXiv requires disclosure of AI involvement in the work. The overview paper already states
  it; do not remove that.

---

## What your name is on right now

- Every one of the 8887 PDFs carries `Adrian Perez Fontelles, Independent researcher`.
- `README.md`, `METHODOLOGY.md`, `LEDGER.md`, `CITATION.cff` and `.zenodo.json` all name you as
  author and set out what you specified and directed.
- `LICENSE` is CC BY 4.0, so anyone reusing the papers is required to credit you.
- GitHub shows a **Cite this repository** button, generated from `CITATION.cff`.

## One warning worth reading twice

The value of this depends entirely on it being right. Eight thousand correct results and one
loudly wrong one, submitted to people who then check it, leaves you worse off than having
submitted nothing. That is why the overview paper leads with what is *not* claimed, why the
error record is in it, and why the queue starts with the corrections rather than the headline
proofs. Keep it that way.
