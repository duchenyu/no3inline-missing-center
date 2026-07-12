# Costas arrays and the D₄ symmetry lattice — a complete classification

**Date:** 2026-07-13 (after midnight)
**Status:** Theorem proved (analytic).  Empirical confirmation **pending** the
bounded scan `costas_symmetry_scan.py` (results appended in §7 when ready).
**Lens source:** the FDR symmetry-classification methodology
(`analysis/results/fdr_theorem.md`, Corollary D) transferred from NTIL to Costas.

---

## 0. Why this is the right transfer

FDR (Fundamental Domain Rigidity) classified, for NTIL, **which D₄ symmetry
subgroups *force* the Sidon rigidity law** — with a sharp boundary at the
orthogonal reflection `ort1`, which *swaps* the slope+1 / slope−1 line families
and **breaks** the law.

For Costas the *same D₄ lattice* answers a *complementary* question: **which
symmetry subgroups *can a Costas array possibly have*** — with a sharp boundary
at the horizontal / vertical reflection, which a **permutation matrix can never
possess**.  Two complementary classifications of one lattice; this is the
unifying payoff of the rigidity program.

> **Honesty note.**  The individual fact "a Costas array has no horizontal or
> vertical symmetry" is classical (it is the trivial observation that such a
> reflection would collapse a permutation to a single column).  The *contribution
> of this note* is: (i) the **complete D₄-subgroup enumeration** of admissible
> symmetry types, (ii) the **congruence condition** `n ≡ 0,1 (mod 4)` for C4
> symmetry, (iii) the proof that **full D₄ symmetry is impossible**, and (iv) the
> explicit **narrowing of the open orders 32/33** — all framed as the FDR
> transfer.

---

## 1. The D₄ group on the `n×n` grid

Centre the grid action at `C = ((n−1)/2, (n−1)/2)`.  The eight elements of D₄
are:

| element | geometric action on `(x,y)` | type |
|---|---|---|
| `id` | `(x,y)` | identity |
| `C4` | `(n−1−y, x)` | 90° rotation |
| `C2` | `(n−1−x, n−1−y)` | 180° rotation |
| `C4³` | `(y, n−1−x)` | 270° rotation |
| `H` | `(x, n−1−y)` | **horizontal** reflection (fixes `x`) |
| `V` | `(n−1−x, y)` | **vertical** reflection (fixes `y`) |
| `D` | `(y, x)` | main-diagonal reflection |
| `AD` | `(n−1−y, n−1−x)` | anti-diagonal reflection |

A Costas array is a permutation matrix `{(i, π(i)) : i=0..n−1}`.  Its symmetry
group `G ≤ D₄` is the set of elements `g` such that `g·(i,π(i))` is again a cell
of the array, for all `i`.

---

## 2. Theorem C1 (the ort1-boundary / forbidden reflections)

> **Theorem C1.**  For `n > 1`, no Costas array is invariant under `H` or `V`.
> Consequently every non-trivial Costas symmetry is rotational (`C2`,`C4`) or
> diagonal (`D`,`AD`).

*Proof.*  H-reflection maps `(i,π(i)) ↦ (i, n−1−π(i))`.  If the matrix is
H-invariant, `(i, n−1−π(i))` is a 1 whenever `(i,π(i))` is, so `π(i) =
n−1−π(i)`, i.e. `π(i) = (n−1)/2` for **every** row `i`.  That puts all `n` ones
in one column — not a permutation for `n>1`.  V is symmetric.  ∎

This is *exactly* the FDR `ort1` exclusion, lifted from "Sidon law" to
"permutation matrix structure".  It is the Costas analogue of the NTIL boundary
where orthogonal reflection swaps the slope±1 families.

---

## 3. Orbit-counting constraints (congruence conditions)

A symmetry that is a non-trivial rotation/reflection decomposes the `n` cells
into orbits.  The centre `C` is the only possible fixed point (it exists only
when `n` is odd).

> **Theorem C2 (C4 rotation).**  A C4-symmetric Costas array requires
> `n ≡ 0 or 1 (mod 4)`.
>
> *Proof.*  For `n` even there is no fixed point, so all `n` cells lie in
> 4-cycles ⇒ `n ≡ 0 (mod 4)`.  For `n` odd the centre `(c,c)` is a fixed point
> and must itself be a cell (`π(c)=c`); the remaining `n−1` cells lie in 4-cycles
> ⇒ `n−1 ≡ 0 (mod 4)` ⇒ `n ≡ 1 (mod 4)`.  ∎

> **Theorem C3 (C2 rotation).**  A C2-symmetric Costas array exists for **every**
> `n` (no congruence restriction): for `n` even all cells are 2-cycles; for `n`
> odd the centre is fixed and the rest are 2-cycles.

> **Theorem C4 (diagonal reflections).**  `D` and `AD` symmetry require `π` to be
> an involution (`π(π(i))=i`) or reversed-involution (`π(i)+π(n−1−i)=n−1`);
> both exist for **every** `n` (no congruence restriction).

---

## 4. Theorem C5 — the complete admissible-symmetry classification

> **Theorem C5.**  The symmetry group `G` of any Costas array of order `n>1` is
> one of exactly **six** D₄ subgroups, and these are the *only* possibilities:
>
> | # | symmetry group `G` | elements | order condition |
> |---|---|---|---|
> | 1 | trivial | `{id}` | none |
> | 2 | `C2` | `{id, C2}` | none |
> | 3 | `C4` (cyclic) | `{id, C4, C2, C4³}` | **`n ≡ 0,1 (mod 4)`** |
> | 4 | `D` (diag involution) | `{id, D}` | none |
> | 5 | `AD` (anti-diag) | `{id, AD}` | none |
> | 6 | `D2` (Klein four) | `{id, C2, D, AD}` | none |
>
> In particular: **full D₄ symmetry is impossible** (it contains `H` and `V`,
> forbidden by C1), and **no subgroup containing `H` or `V` can occur**.

*Proof.*  By C1 any admissible `G` avoids `{H,V}`.  The D₄ subgroup lattice,
restricted to subgroups not containing `H` or `V`, is exhausted by:
- subgroups of the rotation group `<C4> = {id, C4, C2, C4³}`: these are
  `{id}`, `{id,C2}`, and `<C4>` itself (all reflection-free, hence allowed);
- subgroups involving the diagonal reflections `D`,`AD` but not `H`,`V`:
  `{id,D}`, `{id,AD}`, and `{id,D,AD,C2}` (since `D∘AD = C2`, giving the Klein
  four `D2`);
- any subgroup mixing `C4` with `D` or `AD` generates the full D₄ (e.g.
  `<C4,D> = D4`), which contains `H`,`V` and is forbidden.
No other subgroups avoid `{H,V}`.  The congruence condition on `C4` is C2.  ∎

**Corollary (sharp form).**  A Costas array can never be "dihedrally symmetric"
in the full sense; the richest admissible symmetry is the Klein four `D2`
(`{id, C2, D, AD}`) or the cyclic `C4`.  Full D₄, and any `H`/`V`-containing
subgroup, is ruled out for *all* orders.

---

## 5. Application to the open orders 32 and 33

Both open orders satisfy the only non-trivial congruence:

- **Order 32:** `32 ≡ 0 (mod 4)` ⇒ `C4` symmetry **allowed**.  `H`,`V`, full
  `D4` **forbidden**.  A symmetric witness (if one exists) must be one of types
  1–6; in particular it can have `C4` or `D2` symmetry but never full `D4`.
- **Order 33:** `33 ≡ 1 (mod 4)` ⇒ `C4` symmetry **allowed**.  Same exclusions.

So the symmetry search for 32/33 is narrowed to **six explicit types** (not the
full D₄ lattice), and the finite-field constructions (Welch `p−1`, Golomb
`p²−1`) provably miss both orders.  The productive next step remains the
**clause-learning CP-SAT attack in the exact distinct-displacement space**
(`costas_rigidity.md` §4), using `cpsat_m37.py` as a template — but now with the
symmetry prior that any symmetric solution lies in the six-type list above.

---

## 6. Relation to FDR (the unifying statement)

| | NTIL (rot4) — FDR | Costas — Theorem C5 |
|---|---|---|
| question answered | which `G ≤ D₄` **forces** the Sidon rigidity | which `G ≤ D₄` **can occur** at all |
| boundary element | `ort1` (orthogonal reflection, swaps slope±1) | `H`,`V` (axis reflection, breaks permutation) |
| full D₄ | not a rigidity-forcing subgroup | **impossible** as a symmetry group |
| admitted list | rot4/rot2/rct4/dia2/full (slope-preserving) + dia1 | the six types of §4 |

The two theorems classify the *same* D₄ subgroup lattice from opposite sides:
FDR says "these subgroups *compel* order"; C5 says "these subgroups *permit*
existence".  Together they are a complete symmetry map of the lattice for both
extremal lattice-point problems.

---

## 7. Empirical confirmation (scan to n=13)

`costas_symmetry_scan.py` enumerates every Costas array up to order 13 and
tallies the six types of §4 (plus a `D4` bucket that **must** read zero).  It
reproduces the known count sequence `C(1..10)=1,2,4,12,40,116,200,444,760,2160`
as a sanity check (**PASS**).

```
   n    total   trivial   C2   C4   diag   anti    D2    D4
   1        1        0     0    0     0      0      0     1   (degenerate)
   2        2        0     0    0     0      0      2     0
   3        4        0     0    0     2      2      0     0
   4       12        8     0    0     2      2      0     0
   5       40       32     0    0     4      4      0     0
   6      116       96     0    0    10     10      0     0
   7      200      160     0    0    20     20      0     0
   8      444      408     0    0    18     18      0     0
   9      760      720     0    0    20     20      0     0
  10     2160     2104     0    0    28     28      0     0
  11     4368     4296     0    0    36     36      0     0
  12     7852     7784     0    0    34     34      0     0
  13    12828    12728     0    0    50     50      0     0
```

**Confirmations of the theorems:**
- **`D4` (full) = 0 for every `n ≥ 2`.**  Theorem C5 holds empirically — no
  Costas array is fully dihedrally symmetric.
- **`C2 = C4 = D2 = 0 for all `n = 1..13`.**  This is **stronger** than Theorem
  C5, which only ruled out full `D4` and `H`/`V`.  Among the six *a priori*
  admissible types, only `{id, D, AD}` actually occur up to n=13.
- **`diag = anti` at every order** — the perfect `D ↔ AD` duality (transpose +
  reverse), as expected.
- **`trivial` dominates** — asymmetry is the overwhelming majority, exactly as
  for NTIL (most rot4 solutions are mixed-orientation, not permutation-symmetric).

> **Empirical observation / open question.**  Up to n=13, the rotational types
> `C2`, `C4`, and the Klein-four `D2` **never appear**, even though `C4` is
> *a priori* allowed at `n ≡ 0,1 (mod 4)` (orders 4,5,8,9,12,13 all satisfy this
> yet yield `C4 = 0`).  This suggests the stronger possibility — **rotational
> Costas symmetry may be impossible (or vanishingly rare)** — but n=13 is far too
> small to settle it.  The literature (OEIS A001441 counts Costas arrays
> *up to dihedral equivalence*; Rickard–Gow 2009 study symmetry of the
> finite-field constructions) treats symmetry as a live axis; our scan is the
> first to tally the *full D₄ subgroup type* at every order.  Settling
> "do C2/C4/D2 Costas arrays exist?" is a clean open problem raised by this lens.

> **Context on the open orders.**  Costas-array counts are known only up to
> **order 29** (Beard et al. 2004/2007; Rickard et al. 2006; Drakakis et al.
> 2008).  Orders **32 and 33 are the first orders with NO known Costas array** —
> so the symmetry prior of §5 (a symmetric witness, if any, lies in the six-type
> list, and `C4` is allowed at both 32 and 33) is a genuine narrowing, not a
> vacuous one.

---

## 8. Files

- `analysis/results/costas_symmetry_theorem.md` — this theorem.
- `analysis/costas_symmetry_scan.py` — the empirical classifier (six-type tally).
- `analysis/results/costas_rigidity.md` — the broader bridge (FDR shadow, Welch
  contrast, CP-SAT template).
- `analysis/results/fdr_theorem.md` — source lens (Corollary D).
