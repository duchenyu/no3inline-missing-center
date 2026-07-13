# R8-G: Algebraic Orbit Analysis (Correction)

**Status:** Honest assessment — the algebraic orbit analysis provides only
constant-factor compression, NOT asymptotic reduction from O(m³) to O(m²).
The constructive CP-SAT encoder remains the only complete description of
the quadratic constraints for each specific m.

---

## 1. What the orbit approach actually achieves

Let G be an FDR group acting on the N×N board (N=2m). The per-line
constraint family

    Σ_{c∈F_G} w_{L,c}·sel[c] ≤ 2,   for each board line L

has O(m³) members. The orbit approach replaces this by an equivalent
set indexed by G-orbits of lines, with cardinality O(m²/|G|) — an
improvement by a factor of |G| (≤8).  This is **constant-factor**,
not asymptotic.

**Why the factor is at most |G|, not m:**

- A board line L is determined by a primitive direction (dx,dy) and an
  offset t (intercept).  The G-action permutes directions within their orbit
  and relates intercepts via the group.  For each direction orbit, the
  number of distinct offset G-orbits is O(m) — the intercept varies over
  O(m) values and G relates at most |G| of them.
- Since there are O(m²) distinct primitive directions (all coprime pairs
  (dx,dy) within the N×N grid), grouping them by G-orbits gives a factor
  of at most |G|.  The asymptotic count remains O(m²).

Thus the correct statement is:

> The per-line constraints collapse from O(m³) to O(m²/|G|), a constant-factor
> improvement.  For the strongest group (D4, |G|=8), this is ≈8×.
> For C4 (|G|=4), it is ≈4×.  For C2 (|G|=2), ≈2×.

This is useful for practical encoding but does NOT constitute a "closed
form" that eliminates the m-dependence.

---

## 2. The "28 conditions" — correct interpretation

The 16 X-forms + 12 S-forms (from the original R8 C4 analysis) are:

- **Per (c₁,c₂,c₃) type**, not per problem instance.  For each unordered
  triple of distinct fundamental-domain cells, the collinearity condition
  det(p−q, r−q) = 0 expands to a sum over the 4³ = 64 combinations of
  group actions.  Symmetry collapses these 64 to ≤28 distinct polynomial
  forms.  These forms are then instantiated for each actual triple
  (c₁,c₂,c₃) — giving C(m,3) instances of the pattern, each with 28
  possible conditions to check.

- The "28" is the **template count**, not the constraint count.  The
  actual number of quadratic equations is O(m³) in the worst case.

---

## 3. Direction orbits under D₄ subgroups

The full D₄ group acts on primitive direction vectors (dx,dy) with
gcd(|dx|,|dy|)=1.  Under D₄:

- D₄ (order 8): directions partition by {|dx|,|dy|} unordered pair.  For a
  given (|dx|,|dy|) with both nonzero, the 8 D₄ elements map the direction
  to (±dx,±dy), (±dy,±dx).  The number of distinct D₄-orbits grows with
  m — each coprime pair (a,b) with 0≤a,b≤m gives a distinct orbit.  There
  are Θ(m²) such pairs in the worst case.

- C4 (rotations only, order 4): direction orbits are (±dx,±dy) and
  (±dy,±dx) with the 4 rotations, giving roughly m²/4 orbits.

- C2 (180° rotation, order 2): direction orbits are (dx,dy) ↔ (−dx,−dy),
  roughly m²/2 orbits.

**Key point**: The number of direction orbits is always Θ(m²), never O(1)
or O(m).  The finite group only reduces the constant factor.

---

## 4. Honest summary

| Claim | Status |
|---|---|
| "O(m³) → O(m²/|G|)" | ✅ Constant-factor (|G|) compression, not asymptotic |
| "28 conditions — finite set independent of m" | ❌ 28 is the **template** count, not the constraint count. The actual number of constraints is O(m³). |
| "D₄ direction orbits = 3 classes" | ❌ Only for slope families (horizontal/vertical/diagonal), not for all oblique directions. Oblique direction orbits are Θ(m²). |
| "Closed form replaces constructive encoder" | ❌ The constructive encoder remains the only complete description for each m. The orbit analysis explains *why* the encoder is correct but does not replace it. |

The real value of the orbit analysis is:
1. **Proof of correctness**: Every board line's constraint belongs to a
   G-orbit; the encoder covers all orbits → the encoder is complete.
2. **Constant-factor speedup**: Grouping by orbits reduces the encoder's
   generation time by ×|G|.
3. **Structural insight**: Shows why C4 (|G|=4) needs more constraint
   types per cell triple than D4 (|G|=8), but all are O(m³) in total.
