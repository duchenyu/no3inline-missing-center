#!/usr/bin/env python3
# Cleanup pass on the v4-transformed README.md (currently a v2-style output that
# emits BOTH the renamed header and the original header for every subsection).
#  - Delete the 13 duplicate OLD headers (the 2nd of each pair).
#  - Merge the Relaxing duplicate ("### 3.12 ..." empty placeholder + "### 5. ..." with body).
#  - Fix stale "Direction N" prose/comment references.
#  - Fix the Acknowledgments Z3 false "independent cross-validation" claim.
import collections, re

PATH = "README.md"
with open(PATH, encoding="utf-8") as f:
    lines = f.read().split("\n")

# OLD headers that are duplicates of a just-renamed new header. Each is unique
# in the file (appears only as the stray duplicate), so delete globally.
OLD_HEADERS = [
    "### 1. Prior heuristics are falsified by real computation",
    "### 2. Odd n Growth — n=11 Marks Ring-Pair Threshold >100",
    "### 3. The Even n Threshold is Real — and Caused by Collinearity",
    "### 4. Symmetry and Cycle Structure of Missing-Center Solutions",
    "### C₄ Evolution Across Even n — From Theory to n=72",
    "### C₄ Orbit Selection: Cycle Decomposition Insight",
    "### Direction 4: Ring Collision Graph — Sum-of-Two-Squares Structure",
    "### Direction 5: Odd $n$ Missing-Center Existence Bounds",
    "### Direction 6: Proving the rot2 UNSAT Threshold at $n=31$",
    "### Direction 7: The Even n Threshold — Empirically Characterized",
    "### Empirical Observations on C₄ Solution Structure",
    "### Structure of C₄ Solutions and the Row-Degree Theorem",
]
old_set = set(OLD_HEADERS)

removed = []
out = []
for ln in lines:
    if ln.rstrip("\r") in old_set:
        removed.append(ln)
        continue
    out.append(ln)

text = "\n".join(out)

# Merge Relaxing: collapse the empty "### 3.12 ..." placeholder + "### 5. ..." into one 3.12.
before = text
text = text.replace(
    "### 3.12 Relaxing the Row Constraint\n### 5. Relaxing the Row Constraint",
    "### 3.12 Relaxing the Row Constraint",
)
relax_merged = text != before

# Stale "Direction N" prose reference.
text = text.replace("See Direction 7 for analysis.", "See \u00a73.11 for analysis.")

# Stale "(Direction N)" labels in the repository tree.
text = text.replace(
    "# C++ source: unconstrained search (Direction 4)",
    "# C++ source: unconstrained search",
)
text = text.replace(
    "# Circumcircle spectrum (Direction 2)",
    "# Circumcircle spectrum",
)

# Acknowledgments: the Z3/SCIP line falsely claimed "used for independent cross-validation".
# Z3/SCIP were actually evaluated only as candidate engines for the attempted n=74 C\u2084 search.
text = text.replace(
    "- The developers of [Z3](https://github.com/Z3Prover/z3) (SMT solver) and [SCIP](https://www.scipopt.org/) (MIP solver) used for independent cross-validation.",
    "- The developers of [Z3](https://github.com/Z3Prover/z3) (SMT solver) and [SCIP](https://www.scipopt.org/) (MIP solver), evaluated as candidate engines for the attempted n=74 C\u2084-solution search (\u00a72.5).",
)

# Normalise any triple+ blank lines to double.
text = re.sub(r"\n{3,}", "\n\n", text)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(text)

# --- verification ---
print("removed old-header duplicates:", len(removed))
for r in removed:
    print("   -", r)
print("relaxing merged:", relax_merged)
hdr = [l for l in text.split("\n") if l.startswith("### ")]
dups = [h for h, c in collections.Counter(hdr).items() if c > 1]
print("duplicate ### headers:", dups if dups else "none")
print("Direction [0-9] remaining:", text.count("Direction 4") + text.count("Direction 5")
      + text.count("Direction 6") + text.count("Direction 7")
      + ("See Direction" in text))
print("Z3 cross-validation claim present:", "used for independent cross-validation" in text)
print("total lines:", text.count("\n"))
