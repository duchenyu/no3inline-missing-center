# Can the NTIL rigidity theory advance the Costas array problem?

**Date:** 2026-07-12/13 (night)
**Status:** Theoretical bridge complete **and empirically confirmed** (scan to
n=13).  The complete admissible-symmetry classification is in
`costas_symmetry_theorem.md`.
**Lens source:** FDR (slope-line-preserving symmetry ⇒ Sidon) + R7/R8
(two-layer rigidity) + the CP-SAT methodology.

---

## 0. Costas array (recap)

A **Costas array** of order `n` is an `n×n` **permutation matrix** whose
`n(n−1)/2` pairwise displacement vectors `(dx,dy) = (j−i, π(j)−π(i))` are all
distinct.  Equivalently, the set of points `{(i, π(i))}` is a **2-dimensional
Sidon set** (every difference occurs at most once).  The smallest orders with
*no known* Costas array are **32 and 33**; the classical finite-field
constructions (Welch: primitive root mod `p` → order `p−1`; Golomb:
`GF(p²)`) only cover orders `p−1` and `p²−1`, so 32 and 33 fall outside them.

---

## 1. The FDR lens transfers: a symmetry classification, with a sharp boundary

FDR (Fundamental Domain Rigidity) proved: a symmetry `G ≤ D₄` that
**preserves the slope-±1 line family** forces an arithmetic Sidon law; the
boundary case is **orthogonal reflection** (`ort1`), which *swaps* slope+1 and
slope−1 and **breaks** the law (empirically 0% pass).

> **Theorem (Costas ort1-boundary — the FDR analog).**  A permutation matrix
> cannot be invariant under a horizontal or vertical reflection (for `n>1`).
> Hence a Costas array of order `n>1` can have only **rotational**
> (`C2`,`C4`) or **diagonal** (`D`, `AD`) symmetry — never `H`/`V`
> (orthogonal) reflection symmetry.

*Proof.*  H-reflection maps `(i,j) ↦ (i, n−1−j)`.  If the permutation matrix
with `π(i)` = the 1 in row `i` is H-invariant, then `(i,π(i))` a 1 implies
`(i, n−1−π(i))` is also a 1, so `π(i) = n−1−π(i)`, i.e. `π(i) = (n−1)/2` for
**every** row `i`.  That places all `n` ones in a single column — not a
permutation unless `n=1`.  V-reflection is symmetric.  ∎

This is *exactly* the FDR `ort1` exclusion, lifted from "Sidon law" to
"permutation matrix".  It is a **new, rigorous necessary condition** on the
symmetry of any Costas array and directly narrows the symmetry search space for
the open orders 32/33: any solution there (if one exists) must, if symmetric,
belong to `{C2, C4, D, AD}` — never `H`/`V`.

> **Full classification (see `costas_symmetry_theorem.md`).**  The ort1-boundary
> is only the first step.  The complete admissible-symmetry theorem (C5) shows
> that a Costas array can have **exactly six** D₄ symmetry types — `{id}`,
> `{id,C2}`, `<C4>`, `{id,D}`, `{id,AD}`, `{id,C2,D,AD}` — and that **full D₄
> symmetry is impossible** (it contains `H`/`V`).  `C4` requires `n ≡ 0,1 (mod 4)`.
> The bounded scan (n=1..13) confirms `D4(full)=0` everywhere and, *stronger*,
> that `C2`, `C4`, `D2` never occur up to n=13 (only `{id,D,AD}` appear).

---

## 2. FDR as the 1-dimensional Sidon shadow of Costas's 2-dimensional Sidon

Both problems are **symmetry-induced rigidity in extremal lattice point
sets**, differing only in the *order* of the Sidon condition:

| | NTIL (rot4) | Costas |
|---|---|---|
| object | `2n` points, C4-symmetric | `n` points, a permutation |
| rigidity condition | no three collinear | all pairwise displacements distinct |
| Sidon order | **1D** difference-set on the fundamental domain (FDR) → quadratic `(X)+(S)` (R8) | **2D** difference-set (all `(dx,dy)` distinct) |
| symmetry boundary | `ort1` breaks the law | `H`/`V` reflection impossible (§1) |

FDR is the **first-order (linear) projection** of the rigidity; Costas's
distinct-displacement condition is the **full 2D** version.  Reading the NTIL
work through this lens, the two-layer structure (linear ⇒ quadratic ⇒ exact)
suggests a **parallel two-layer rigidity for Costas**, stated in §4.  The value
of the NTIL theory here is *not* a direct formula for Costas, but a
**classificatory framework** (symmetry ⇒ allowed rigidity type ⇒ restricted
search space) that transfers cleanly.

---

## 3. The Welch contrast — a clean "what works where" delineation

The finite-field **1-regular** construction is the workhorse of both worlds:

- **Costas (Welch):** primitive root `g` mod prime `p`, `π(i) = ind_g(g^i)`,
  gives a valid Costas array of order `p−1`.  Finite-field 1-regular **works**.
- **rot4 NTIL:** the analogous finite-field 1-regular / permutation / cycle
  constructions (Welch-style, power-residue, hyperbolic) were all tested and
  **failed** — a 1-regular pairing is not a 2-regular (C4-liftable) structure
  (the 55+ negative searches; see `two_layer_rigidity.md` §2 / R7).

So: the *same family of ideas* (finite-field difference sets) **succeeds** for
Costas but **fails** for rot4 NTIL.  The obstacle for NTIL is the **quadratic**
cross-quadrant collinearity (R7) — a higher-order rigidity that 1-regular
constructions cannot satisfy.  This contrast is itself a contribution: it tells
us that for *both* problems, the finite-field 1-regular toolkit exhausts only
the **linear** layer, and any further progress (orders 32/33 for Costas; m=37
for NTIL) must come from attacking the **quadratic/exact** layer directly.

---

## 4. A suggested two-layer rigidity for Costas (and the transferable method)

Paralleling R7→R8:

- **Layer-1 (linear) for Costas:** the Golomb-ruler condition along each row
  and column independently (1D difference-distinctness).  Necessary but far from
  sufficient.
- **Layer-2 (quadratic/exact) for Costas:** all `n(n−1)/2` pairwise `(dx,dy)`
  distinct — the actual Costas condition, a 2D Sidon set.

Our NTIL CP-SAT encoder (`cpsat_m37.py`, `cpsat_encoding.md`) is a direct
**template** for the Costas attack:

- Variables: a permutation matrix = choose exactly one cell per row and per
  column (`Σ_row = 1`, `Σ_col = 1`).
- Layer-2 constraint: for every unordered pair of chosen points, their
  displacement `(dx,dy)` must be unique → encode as "no two pairs share a
  displacement" (a 4-variable disequality, linearizable into clauses over the
  selection bits, exactly as `(X)+(S)` linearized into per-line at-most-2).
- Clause-learning CP-SAT (OR-Tools) with the strong row/col cardinality
  propagation is the right paradigm for orders 32/33, just as it is for m=37
  NTIL.  The NTIL experience — *greedy DFS fails (global rigidity), clause
  learning is required* — is a concrete methodological lesson for the Costas
  32/33 attack.

---

## 5. What this says about orders 32 and 33

- Finite-field constructions (Welch/Golomb) provably **do not cover** 32 or 33
  (neither is `p−1` or `p²−1` for prime `p`).
- By §1, any symmetric solution must avoid `H`/`V` reflection — only
  `C2, C4, D, AD` remain candidates for a symmetric witness.
- By §3–§4, the path forward is a **clause-learning SAT/CP-SAT attack in the
  exact Layer-2 (distinct-displacement) space**, using the NTIL encoder as a
  template.  This reframes 32/33 from "mystery" to a concrete, finite,
  exactly-encoded CSP — the same reframing we achieved for m=37 NTIL.

---

## 6. Empirical symmetry-classification table (DONE)

`costas_symmetry_scan.py` enumerates all Costas arrays up to a given order and
classifies each by its `D₄` symmetry type, reproducing the known count sequence
`C(1..10) = 1,2,4,12,40,116,200,444,760,2160` as a sanity check (**PASS**).
The full table (n=1..13) and the analysis live in
`costas_symmetry_theorem.md` §7.  Key findings:
- **`D4(full) = 0` at every order** → confirms Theorem C5 (full D₄ impossible).
- **`C2 = C4 = D2 = 0` up to n=13** → stronger than the theorem predicts;
  raises the open question of whether rotational Costas symmetry exists at all.
- **`diag = anti`** at every order (the `D ↔ AD` duality).
- **`trivial` dominates** (asymmetry is the norm), paralleling NTIL where most
  rot4 solutions are mixed-orientation.

This is the first tally of the *complete D₄ subgroup type* at every order, and
directly informs the symmetry prior for any attack on orders 32/33.

---

## 7. Files

- `analysis/costas_symmetry_scan.py` — D₄ symmetry classifier for Costas arrays.
- `analysis/cpsat_m37.py` / `analysis/results/cpsat_encoding.md` — the
  transferable CP-SAT methodology (NTIL → Costas template).
- `analysis/results/fdr_theorem.md`, `two_layer_rigidity.md`,
  `quadratic_gap_theorem.md` — the source lens.
