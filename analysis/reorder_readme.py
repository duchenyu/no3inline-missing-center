#!/usr/bin/env python3
# Reorder README.md (v4): split on '## ' only, extract '### '-level sub-sections by
# substring, rename each block's OWN header in place (no double headers), reassemble.
# Z3 dropped; duplicate "Relaxing" merged.
import re

PATH = "README.md"
with open(PATH, encoding="utf-8") as f:
    raw = f.read()

lines = raw.split("\n")
preamble = []
sections = []
cur_h = None
cur_b = []
for line in lines:
    if line.startswith("## ") and not line.startswith("### "):
        if cur_h is None:
            preamble = cur_b
            cur_b = []
        else:
            sections.append((cur_h, "\n".join(cur_b)))
        cur_h = line
        cur_b = []
    else:
        cur_b.append(line)
if cur_h is not None:
    sections.append((cur_h, "\n".join(cur_b)))

sec = {h: b for h, b in sections}
def body_of(h):
    return sec[h]
def between(s, a, b):
    return s[s.index(a):s.index(b)]
def after_to_end(s, a):
    return s[s.index(a):]

H_PROBLEM = "## The Problem"
H_KEYFIND = "## Key Findings"
H_USAGE = "## Usage"
H_REPO = "## Repository Structure"
H_RESULTS = "## Results Data"
H_C4THM = "## The C₄ Theorem — A Proven Result ✔"
H_D4REC = "## D₄ Full Reconstruction and Quantitative Model"
H_SIDE = "## Side Exploration: Higher-Dimensional Generalizations"
H_REFS = "## References"
H_ACK = "## Acknowledgments"
H_CITE = "## Citation"
H_LIC = "## License"

kf = body_of(H_KEYFIND)
c4 = body_of(H_C4THM)
d4 = body_of(H_D4REC)

sec1 = between(kf, "### 1. Prior heuristics are falsified by real computation",
              "### 2. Odd n Growth — n=11 Marks Ring-Pair Threshold >100")
sec2 = between(kf, "### 2. Odd n Growth — n=11 Marks Ring-Pair Threshold >100",
              "### 3. The Even n Threshold is Real — and Caused by Collinearity")
sec3 = between(kf, "### 3. The Even n Threshold is Real — and Caused by Collinearity",
              "### 4. Symmetry and Cycle Structure of Missing-Center Solutions")
sec4 = between(kf, "### 4. Symmetry and Cycle Structure of Missing-Center Solutions",
              "### 5. Relaxing the Row Constraint")
sec5 = after_to_end(kf, "### 5. Relaxing the Row Constraint")

c2_start = sec4.index("#### C₂ theorem (180° rotational symmetry)")
fc_start = sec4.index("#### Four-colouring invariant (verified)")
c2_block = sec4[c2_start:fc_start]
fc_block = sec4[fc_start:]
sec4_clean = sec4[:sec4.index("#### D₄ Symmetry Analysis")]

sec1 = sec1.replace("### 1. Prior heuristics are falsified by real computation",
                    "### 3.1 Prior heuristics are falsified by real computation", 1)
sec1 = sec1.replace("### Missing-Center Absence in Catalogued Symmetry Classes at n≥33",
                    "#### Missing-Center Absence in Catalogued Symmetry Classes at n≥33", 1)
sec2 = sec2.replace("### 2. Odd n Growth — n=11 Marks Ring-Pair Threshold >100",
                    "### 3.2 Odd n Growth — n=11 Marks Ring-Pair Threshold >100", 1)
sec3 = sec3.replace("### 3. The Even n Threshold is Real — and Caused by Collinearity",
                    "### 3.3 The Even n Threshold is Real — and Caused by Collinearity", 1)
sec4_clean = sec4_clean.replace(
    "### 4. Symmetry and Cycle Structure of Missing-Center Solutions",
    "### 3.4 Symmetry and Cycle Structure of Missing-Center Solutions", 1)
sec5 = sec5.replace("### 5. Relaxing the Row Constraint",
                    "### 3.12 Relaxing the Row Constraint", 1)

c4thm_core = c4[:c4.index("### C₄ Evolution Across Even n — From Theory to n=72")]
c4evo = between(c4, "### C₄ Evolution Across Even n — From Theory to n=72",
               "### C₄ Orbit Selection: Cycle Decomposition Insight")
c4orb = between(c4, "### C₄ Orbit Selection: Cycle Decomposition Insight",
               "### Direction 4: Ring Collision Graph — Sum-of-Two-Squares Structure")
dir4 = between(c4, "### Direction 4: Ring Collision Graph — Sum-of-Two-Squares Structure",
              "### Direction 5: Odd $n$ Missing-Center Existence Bounds")
dir5 = between(c4, "### Direction 5: Odd $n$ Missing-Center Existence Bounds",
              "### Direction 6: Proving the rot2 UNSAT Threshold at $n=31$")
dir6 = between(c4, "### Direction 6: Proving the rot2 UNSAT Threshold at $n=31$",
              "### Direction 7: The Even n Threshold — Empirically Characterized")
dir7 = between(c4, "### Direction 7: The Even n Threshold — Empirically Characterized",
              "### Z3 Solver Cross-Validation (analysis/z3_solver.py, analysis/z3_solver_v2.py)")
relax2 = after_to_end(c4, "### Relaxing the Row Constraint — Explored")
relax2_code = relax2[relax2.index("**Code**:"):].strip()

c4evo = c4evo.replace("### C₄ Evolution Across Even n — From Theory to n=72",
                      "### 3.5 C₄ Evolution Across Even n — From Theory to n=72", 1)
c4orb = c4orb.replace("### C₄ Orbit Selection: Cycle Decomposition Insight",
                      "### 3.6 C₄ Orbit Selection: Cycle Decomposition Insight", 1)
dir4 = dir4.replace("### Direction 4: Ring Collision Graph — Sum-of-Two-Squares Structure",
                    "### 3.8 Ring Collision Graph — Sum-of-Two-Squares Structure", 1)
dir5 = dir5.replace("### Direction 5: Odd $n$ Missing-Center Existence Bounds",
                    "### 3.9 Odd-n Missing-Center Existence Bounds", 1)
dir6 = dir6.replace("### Direction 6: Proving the rot2 UNSAT Threshold at $n=31$",
                    "### 3.10 The rot2 UNSAT Threshold at n=31", 1)
dir7 = dir7.replace("### Direction 7: The Even n Threshold — Empirically Characterized",
                    "### 3.11 The Even-n Threshold — Empirically Characterized", 1)

d4_core = d4[:d4.index("### Structure of C₄ Solutions and the Row-Degree Theorem")]
d4_core = d4_core.replace("### D₄ Equivalence Class → Full Solution Counts",
                          "#### D₄ Equivalence Class → Full Solution Counts", 1)
d4_core = d4_core.replace("### Three-Factor Quantitative Model",
                          "#### Three-Factor Quantitative Model", 1)
d4_core = d4_core.replace("### Refined Model: Sum-of-Two-Squares Theory",
                          "#### Refined Model: Sum-of-Two-Squares Theory", 1)
rowdeg = between(d4, "### Structure of C₄ Solutions and the Row-Degree Theorem",
                "### Empirical Observations on C₄ Solution Structure")
empc4 = after_to_end(d4, "### Empirical Observations on C₄ Solution Structure")
rowdeg = rowdeg.replace("### Structure of C₄ Solutions and the Row-Degree Theorem",
                        "### 2.5 Structure of C₄ Solutions and the Row-Degree Theorem", 1)
empc4 = empc4.replace("### Empirical Observations on C₄ Solution Structure",
                      "### 3.14 Empirical Observations on C₄ Solution Structure", 1)

c2_block = c2_block.replace("#### C₂ theorem (180° rotational symmetry)",
                            "### 2.2 C₂ Theorem (180° rotational symmetry)", 1)
fc_block = fc_block.replace("#### Four-colouring invariant (verified)",
                            "### 2.3 Four-colouring Invariant (verified)", 1)

out = []
out.append("\n".join(preamble).rstrip())
out.append("")
out.append(H_PROBLEM)
out.append(body_of(H_PROBLEM).lstrip("\n"))

out.append("")
out.append("## 2. Proven Results")
out.append("")
out.append("This section collects every result that is **proven** (theorem or lemma with proof), as opposed to the computational observations gathered in §3.")
out.append("")
out.append("### 2.1" + H_C4THM[2:])
out.append(c4thm_core.lstrip("\n"))
out.append("")
out.append(c2_block.strip("\n"))
out.append("")
out.append(fc_block.strip("\n"))
out.append("")
out.append("### 2.4 Ring-Population Lemma (rot4)")
out.append("")
out.append("Every C₄-orbit of the grid is a square of 4 vertices, all equidistant from the centre. Hence every distance ring used by a rot4 solution is a union of complete orbits, and its population is a multiple of 4. Empirically the observed populations are 4, 8, 12, or 16 (across all 21,601 rot4 solutions for n = 12–72). This is a direct corollary of the C₄ orbit structure in §2.1 — a structural property, not an independent missing-centre criterion. (The “multiple of 4” law is specific to even-n rot4; rct4 orbits can have size 2, so it does not extend to rct4.)")
out.append("")
out.append(rowdeg.strip("\n"))

out.append("")
out.append("## 3. Empirical Findings")
out.append("")
out.append("All material in this section is **computational observation**, not proof. Headings and tables report what exhaustive search and the Flammenkamp / mvr databases actually contain.")
out.append("")
out.append(sec1.strip("\n"))
out.append("")
out.append(sec2.strip("\n"))
out.append("")
out.append(sec3.strip("\n"))
out.append("")
out.append(sec4_clean.strip("\n"))
out.append("")
out.append(c4evo.strip("\n"))
out.append("")
out.append(c4orb.strip("\n"))
out.append("")
out.append("### 3.7 D₄ Reconstruction & Quantitative Model")
out.append(d4_core.lstrip("\n"))
out.append("")
out.append(dir4.strip("\n"))
out.append("")
out.append(dir5.strip("\n"))
out.append("")
out.append(dir6.strip("\n"))
out.append("")
out.append(dir7.strip("\n"))
out.append("")
out.append(sec5.strip("\n"))
out.append("")
out.append(relax2_code)
out.append("")
out.append("### 3.13 Construction Attempts & Open Problems")
out.append("")
out.append("""A natural next step is to turn the invariants above into an **explicit construction** of 2n-point solutions for a whole infinite sub-family of even n (e.g. n ≡ 0 mod 4), lifting existence from computational evidence to a partial proof of D(n) = 2n.

The C₂ theorem (§2.2) reduces this to a single clean obstacle: choose n R₁₈₀-orbit seeds whose central directions are pairwise distinct (this automatically rules out all collinearity *through* the centre), and avoid collinearity on lines *not* through the centre. Three explicit generators were tested and all failed broadly:

- **Modular polynomial seeds** `c(i) = f(i) mod n`, R₁₈₀-doubled — across 8 formulas and even n ≤ 80, only n = 4 succeeded.
- **R₁₈₀-doubled finite-field parabola** on prime grids p ≤ 59 — 0 successes (the doubled curve creates 2 + 1 collinear points).
- **Deterministic greedy placement** with the C₂ direction rule enforced — 0 successes for even n ≤ 80 (the construction stalls immediately).

These failures are *algorithmic limitations, not a proof of non-existence* (2n solutions are known to exist for all even n ≤ 72). They show that **off-centre collinearity is the genuine hard core** of the problem. The realistic contribution is therefore: (a) publish the C₄ and C₂ theorems as novel structural invariants, and (b) use them to *characterise* known solutions, not to claim a closed-form construction. The existence question D(n) ≥ 2n remains open in general.""")
out.append("")
out.append(empc4.strip("\n"))

out.append("")
out.append("## 4. Methodology & Verification")
out.append("")
out.append("""**Exhaustive search (`no3line.cpp`).** A backtracking search places exactly 2 points per row and column, pruned by a precomputed collinearity accumulator (O(1) per candidate) and a distance-ring filter that forbids any ring from reaching 3 points (the missing-centre detector). Mode 0 enumerates all solutions; mode 1 counts missing-centre solutions only (recommended for n ≥ 12). The same engine was cross-checked against the independent C++ full enumeration and against the Flammenkamp / mvr databases (D₄-inequivalent counts agree to <1%).

**Independent verifier (`verify_solution.py`).** Every published solution dump is re-checked from scratch with three independent tests: (1) no three points collinear (exact integer area), (2) centre-presence via the distance-ring distribution, (3) each column used exactly twice. This is the primary reliability guarantee for all counts reported above.

**Unconstrained search (`d4_relaxed.cpp`).** A cell-by-cell backtrack with no 2-per-row rule, used to confirm that the even-n threshold is geometric, not a search artefact (§3.12).""")

out.append("")
out.append("## 5. Higher-Dimensional Generalizations")
out.append(body_of(H_SIDE).lstrip("\n"))

out.append("")
out.append(H_USAGE)
out.append(body_of(H_USAGE).lstrip("\n"))
out.append("")
out.append(H_REPO)
out.append(body_of(H_REPO).lstrip("\n"))
out.append("")
out.append(H_RESULTS)
out.append(body_of(H_RESULTS).lstrip("\n"))
out.append("")
out.append(H_REFS)
out.append(body_of(H_REFS).lstrip("\n"))
out.append("")
out.append(H_ACK)
out.append(body_of(H_ACK).lstrip("\n"))
out.append("")
out.append(H_CITE)
out.append(body_of(H_CITE).lstrip("\n"))
out.append("")
out.append(H_LIC)
out.append(body_of(H_LIC).lstrip("\n"))

new_text = "\n".join(out)
new_text = re.sub(r"\n{3,}", "\n\n", new_text)
with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_text)

print("=== top-level (## ) order ===")
for ln in new_text.split("\n"):
    if ln.startswith("## ") and not ln.startswith("### "):
        print(ln)
# duplicate-header scan
import collections
hdr = [l for l in new_text.split("\n") if l.startswith("### ")]
dups = [h for h, c in collections.Counter(hdr).items() if c > 1]
print("duplicate ### headers:", dups if dups else "none")
for s in ["Three-Factor Quantitative Model", "D₄-inequivalent solution counts",
          "Refined Model: Sum-of-Two-Squares", "Por-Wood", "n=74 C₄ solution",
          "Empirical Observations on C₄", "C₄ Orbit Selection"]:
    print(f"  present {s!r}: {s in new_text}")
print("Z3 section:", "Z3 Solver Cross-Validation (analysis" in new_text)
print("Relaxing dup:", "Relaxing the Row Constraint — Explored" in new_text)
print("total lines:", new_text.count(chr(10)))
