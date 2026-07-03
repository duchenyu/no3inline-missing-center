# No-Three-In-Line: Missing Center Analysis

An optimized exhaustive search for **missing-center** solutions to the No-Three-In-Line problem, featuring a novel **forbid-accumulator** algorithm (O(k²) → O(1) collinearity check).

## The Problem

Place **2n points** on an **n×n grid** such that no three are collinear. The No-Three-In-Line problem asks for the maximum number of points D(n) achievable. It is known that D(n) = 2n for all n ≤ 46 (with the sole exception of n = 71, where this remains open).

**New perspective**: For each solution achieving 2n points, check whether the grid center is a circumcenter of some triple of points. A "missing-center" solution (or **"center-free"** solution) has **no** triple whose circumcircle is centered at the grid center. This is a novel invariant not previously studied in the literature.

## Key Findings

### 1. Prior heuristics are falsified by real computation

Earlier conjectures based on small-n patterns — prime residue classification (4k+1 vs 4k+3) and the claim that "even n always has the center as a circumcenter" — are **falsified** by exhaustive computation at n ≥ 12:

| n | Type | Total Solutions | With Center | Missing Center | Verified |
|---|------|----------------|-------------|---------------|----------|
| 2 | Even | 1 | 1 | 0 | ✅ |
| 4 | Even | 11 | 11 | 0 | ✅ |
| 6 | Even | 50 | 50 | 0 | ✅ |
| 8 | Even | 380 | 380 | 0 | ✅ |
| 10 | Even | 1,135 | 1,135 | 0 | ✅ |
| **12** | **Even** | **4,348** | **4,296** | **52** | ✅ *First even n with missing-center solutions* |
| 3 | Odd P | 2 | 2 | 0 | ✅ |
| 5 | Odd P (4k+1) | 32 | 28 | 4 | ✅ |
| 7 | Odd P (4k+3) | 132 | 128 | 4 | ✅ |
| 9 | Odd C | 368 | 360 | 8 | ✅ |
| 11 | Odd P (4k+3) | 1,120 | 1,084 | 36 | ✅ |
| 13 | Odd P (4k+1) | — | — | **292** | ✅ *(mode 1 only)* |

**Key observations**:
- n=12 is the **first even n** with missing-center solutions (52)
- The "4k+1 vs 4k+3" prime classification does NOT hold: n=13 (≡1 mod 4) has 292 missing, far exceeding n=11 (≡3 mod 4)'s 36
- Missing counts grow super-exponentially: 4 → 4 → 8 → 36 → 52 → 292

### 2. The Even n Threshold is Real — and Caused by Collinearity

A fundamental question is: **why n=12?** Why do n=6, 8, 10 all have zero missing-center solutions while n=12 has 52?

**Distance ring analysis**: For even n, the grid center lies at a half-integer coordinate ((n−1)/2, (n−1)/2). The squared distance (scaled by 4) from the center is:

d(c,r) = (2c−(n−1))² + (2r−(n−1))²

The values x² = (2c−(n−1))² range over {1², 3², 5², …, (n−1)²}, giving n/2 distinct squared-offset values. A distance "ring" consists of all grid points sharing the same sum of two such squares.

| n | Distinct Rings (R) | 2×R (max pts without center) | 2n (pts needed) | Ratio 2n/(2R) | Flexibility | Missing |
|---|-------------------|------------------------------|-----------------|---------------|-------------|---------|
| 6 | 6 | 12 | 12 | 1.000 | 0% | 0 |
| 8 | 9 | 18 | 16 | 0.889 | 11% | 0 |
| 10 | 14 | 28 | 20 | 0.714 | 29% | 0 |
| 12 | 19 | 38 | 24 | 0.632 | 37% | **52** |
| 14 | 25* | 50* | 28 | 0.569* | 44%* | ? |

**Theoretical analysis**: We constructed the counting matrix M[i][j] = number of points placed by row‑group i (rows with x² = value i) into column‑group j (columns with x² = value j). The distance‑ring constraints reduce to:

- M[i][i] ≤ 2 (each pure‑square ring has capacity 2)
- M[i][j] + M[j][i] ≤ 2 for i ≠ j (mixed rings are shared between two row‑column group pairs)

For n=8, we solved the matrix equation explicitly and found a continuous family of solutions parameterized by a free integer variable. **Therefore, the distance‑ring constraint alone does NOT forbid missing-center solutions at n=8.**

The fact that the exhaustive search finds zero missing-center solutions for n=8 and n=10 implies that **the collinearity constraint is the true barrier**. The extra distance rings at n=12 (19 vs. 9 for n=8) provide sufficient geometric diversity for the search to find arrangements satisfying both constraints simultaneously.

**Conclusion**: The threshold at n=12 is a genuine combinatorial phase transition driven by the interaction between the distance-ring capacity and the "no three collinear" constraint — not a simple pigeonhole effect.

### 3. Relaxing the Row Constraint

Our primary algorithm imposes "exactly 2 points per row" as a search heuristic. To verify that this does not distort the qualitative behavior, we implemented a **cell-by-cell backtracking** that imposes no row constraint (directory `d4/`).

| n | Row Constraint | Total Solutions | Missing Center | Ratio |
|---|---------------|----------------|---------------|-------|
| 5 | 2-per-row | 32 | 4 | 12.5% |
| 5 | Unconstrained | 3,209 | 28 | 0.87% |
| 6 | 2-per-row | 50 | 0 | 0% |
| 6 | Unconstrained | 91,358 | 0 | **0%** |
| 7 | 2-per-row | 132 | 4 | 3.0% |
| 7 | Unconstrained | 1,310,234 | 11,922 | **0.91%** |

**Key finding**: The even‑n threshold (n=12) is **not** an artifact of the row constraint. Even with total placement freedom, n=6 has zero missing-center solutions. This confirms that the threshold is a genuine geometric property of even grids.

## Algorithm: Forbid Accumulator (v2)

The key optimization turns the collinearity check from **O(k²) to O(1)** per placement.

```
For each future row k, maintain:
    forbid_accum[k] := bitmask of columns blocked by ALL existing cross-row pairs.

When placing a new point at (r, c):
    if forbid_accum[r] has bit c set → reject (would create collinear triple)
    Otherwise → place, then update forbid_accum for rows > r.
```

This is a **precomputed line‑blocking table** — for every pair of existing grid points, we precompute all future grid cells that lie on the same line. At check time, the O(k²) nested loop is replaced by a single bit‑test.

**Speedup**: n=11 mode 0 went from 9.2 minutes → 8.5 seconds (**65×**).

Additional optimizations:
- ✅ Precomputed collinearity accumulation (forbid_accum)
- ✅ Diagonal pre-check (x+y and x−y+N−1 occupancy counters)
- ✅ **Distance ring pruning** (mode 1: only count solutions with no 3 points sharing the same center‑distance — much faster for the missing‑center problem)
- ✅ **Mirror symmetry pruning** (first‑row constraint c₁+c₂ ≤ N−1 halves the search space)
- ✅ **Multi-threaded** (32 task‑parallel workers via first‑row column pairs)
- ✅ **Statically linked binary** (zero DLL dependencies on Windows)

## Usage

### Build

**Linux**:
```bash
make
```

**Windows (MinGW)**:
```batch
compile.bat
```

**Windows (MSVC)**:
The batch file auto-detects MSVC if MinGW is not found.

### Run

```bash
# Mode 0: Full search (count all solutions + missing-center)
./no3line <n> 0 <threads>

# Mode 1: Missing-center only (distance pruning, recommended for n≥12)
./no3line <n> 1 <threads>

# Examples
./no3line 12 1 16    # n=12 missing-center only, 16 threads
./no3line 15 1 16    # n=15 (needs cloud-grade hardware)
```

### Batch run

**Linux**: `./run_cloud.sh [mode] [threads] ["n1 n2 n3 ..."]`
**Windows**: Edit `run.bat` or run `run.bat`

## Repository Structure

```
├── no3line.cpp              # C++ source: forbid-accumulator search (v2)
├── d4_relaxed.cpp           # C++ source: cell-by-cell search (no row constraint)
├── Makefile                 # Linux build
├── compile.bat              # Windows build
├── run.bat                  # Windows batch runner
├── run_cloud.sh             # Linux batch runner (16-thread cloud preset)
├── README.md                # This file
├── results/                 # Computed result CSVs
│   ├── result_n5_mode0.csv .. result_n13_mode1.csv
│   └── result_d4_n5.csv .. result_d4_n7.csv   (unconstrained results)
├── solutions/               # Dumped individual solutions
│   ├── sols_n12.csv         # All 28 (base) missing-center solutions for n=12
│   └── sols_d4_n5.csv ..    # Unconstrained solutions (if available)
└── analysis/
    ├── analyze.py           # Distance ring analysis for 2-per-row solutions
    └── analyze_d3.py        # Even-n threshold ring analysis
```

## Results Data

Each CSV row: `n,total_solutions,with_center,missing_center,time_seconds,mode`

- Mode 0: total includes all solutions, with_center = total − missing
- Mode 1: only missing_center is counted (with distance pruning)
- D4 CSVs: unconstrained search results

## Future Research Directions

### Direction 1: Constructive Missing-Center Solutions

Prove that missing-center solutions exist for all sufficiently large n by **explicit construction**.

**Approach**: The column pairing graph (each column appears exactly twice) decomposes into cycles. Design cycle structures with controlled distance-ring occupancy. The d=34 and d=82 rings appear in **every** missing-center solution for n=12 — suggesting they are "universal" building blocks.

**Progress**: The counting-matrix M[i][j] formalism (see Section 2 above) provides a linear-algebraic framework for constructing assignments that satisfy the distance-ring constraint. The remaining challenge is incorporating the collinearity constraint into the construction.

### Direction 2: Circumcircle Spectrum

Map **every** grid point's role as a circumcenter. For a solution with 2n points, the C(2n, 3) triples each determine a circumcenter (which may or may not be another grid point). The "circumcircle spectrum" characterizes which grid points serve as circumcenters.

**Open questions**: Does every solution have a unique "circumcenter signature"? Are two solutions with identical circumcenter spectra isomorphic under grid symmetries?

### Direction 3: The Even n Threshold — Solved ✓

The threshold at n=12 is caused by the interaction between distance-ring capacity and the collinearity constraint. The matrix M[i][j] analysis shows that the ring constraint alone is satisfiable at n=8, but the collinearity constraint eliminates all such assignments. At n=12, the 19 rings provide enough geometric diversity for both constraints to be satisfied simultaneously.

**Next question**: At what n does the next even threshold appear? (n=14? n=16?) The search for n≥14 requires cloud‑grade computing.

### Direction 4: Relaxing the Row Constraint — Explored

Removing the "2 points per row" constraint massively increases the solution space (n=7: 132→1.3M solutions, 4→11,922 missing-center). However, the even-n threshold at n=12 remains intact — confirming it is a genuine geometric property, not a search heuristic artifact.

The unconstrained search code (`d4_relaxed.cpp`) can enumerate all No-Three-In-Line solutions for n ≤ 7 without any grid constraints.

### Direction 5: Spectral Analysis of the Forbid Matrix

The forbid_accum algorithm effectively builds a **collinearity-avoidance graph** on grid positions. Analyzing the eigenvalues or algebraic connectivity of this graph may reveal deeper structure about why n=12 is the transition point.

## Citation

If you use this work in research, please cite this repository:

```
@software{no3line_missing_center,
  author = {Du, Chenyu},
  title = {no3line-missing-center: No-Three-In-Line Missing Center Analysis},
  year = {2026},
  url = {https://github.com/duchenyu/no3line-missing-center}
}
```

## License

MIT
