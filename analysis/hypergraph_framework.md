# Hypergraph Theoretical Framework for No-Three-In-Line

> A programmatic framework for studying the orbit-collinearity hypergraph
> and its independence number α(Hₙ), with connections to the missing-center problem.

---

## 1. Three Hypergraph Models

The No-Three-In-Line problem can be reformulated as an **independent-set problem in a 3-uniform hypergraph** at three levels of abstraction.

### Model 1: Direction Hypergraph Hₙ^dir (C₂ Orbits)

**Vertices**: Reduced direction vectors (a,b) ∈ ℤ², gcd(a,b)=1, from the grid center to each lattice point in the n×n grid. The direction is normalized to the canonical half-plane (a>0 or a=0,b>0).

Number of vertices: V₁ = n²/2 (all C₂ orbits) for even n.

**Hyperedges**: A triple of directions {dᵢ, dⱼ, dₖ} forms a hyperedge iff there exist points (x₁,y₁), (x₂,y₂), (x₃,y₃), each belonging to the respective C₂ orbit, such that the three points are collinear AND not collinear through the grid center.

This is the **off-center collinearity hypergraph** — center-line triples are excluded because they are ruled out by Lemma 1 (C₂ theorem): distinct directions from center → no center-line collinear triple among the C₂ orbit points.

**Solution correspondence**: A 2n-point no-three-in-line solution corresponds to an **independent set** of size n in Hₙ^dir.

This is the model implemented in `danger_hypergraph.py`.

### Model 2: C₄ Orbit Hypergraph Hₙ^orb

**Vertices**: C₄ orbits in the fundamental domain [0,N)×[0,N) for even n=2N. Each orbit is 4 points under 90° rotation: (x,y)→(y,n-1-x)→(n-1-x,n-1-y)→(n-1-y,x).

Number of vertices: V₂ = N² = n²/4.

**Hyperedges**: A triple of C₄ orbits {oᵢ, oⱼ, oₖ} forms a hyperedge iff the 12 points (4×3) contain at least one collinear triple.

**Solution correspondence**: A C₄-symmetric 2n-point no-three-in-line solution corresponds to selecting N orbits (one per row of the fundamental domain) that form an **independent set** in Hₙ^orb. The row constraint adds a matching structure.

### Model 3: Ring Hypergraph Hₙ^ring

**Vertices**: Distance rings R(r) = {points with squared distance d = (2x-n+1)²+(2y-n+1)² = r}.

**Hyperedges**: A triple of rings (R₁, R₂, R₃) forms a hyperedge iff any selection of one point from each ring is guaranteed to contain a collinear triple — i.e., the rings are "inevitably collinear."

**Solution correspondence**: A missing-center solution corresponds to selecting at most 2 points from each ring (i.e., an independent set in Hₙ^ring with capacity constraint per vertex).

---

## 2. Known Properties (Empirical, n=12,16,20)

From `danger_hypergraph.py`:

### Sparsity

| n | Vertices | C(V,3) | Hyperedges | Edge Density |
|---|----------|--------|------------|-------------|
| 12 | 72 | 59,640 | 691 | 1.159% |
| 16 | 128 | 341,376 | 2,746 | 0.804% |
| 20 | 200 | 1,313,400 | 6,325 | 0.482% |
| 24 | 288 | 3,939,936 | 14,456 | 0.367% |
| 28 | 392 | 9,962,680 | 30,077 | 0.302% |
| 32 | 512 | 22,238,720 | 47,836 | 0.215% |

Edge density **decreases with n** as approximately **6.8 · n^(−0.67)** (power-law fit, R²>0.99). This suggests Hₙ becomes sparser as n grows—a favorable property for container-type arguments. At n=76, the estimated edge density would be ~0.08%.

### Degree Distribution (Heavy-Tailed)

The danger-degree is heavily concentrated on the main diagonal direction (1,1) and its symmetric counterpart (1,-1):

| n | (1,1) degree | (1,-1) degree | (3,1) degree | (1,3) degree | Total danger | (1,1) share |
|---|------------|-------------|-------------|-------------|-------------|-----------|
| 12 | 743 | 650 | 53 | 48 | 3,176 | 23.4% |
| 16 | 2,493 | 2,251 | 295 | 207 | 12,218 | 20.4% |
| 20 | 6,209 | 5,694 | 403 | 305 | 38,064 | 16.3% |
| 24 | 13,113 | 12,189 | 1,208 | 668 | 96,777 | 13.5% |
| 28 | 24,626 | 23,123 | 2,883 | 1,333 | 190,203 | 12.9% |
| 32 | 42,158 | 39,842 | 3,383 | 2,720 | 333,295 | 12.6% |

> ⚠️ **CORRECTION (2026-07-09).** The "(1,1) dominance" figures above were produced
> with the buggy `collinear3` (only the first 3 of 6 orbit points checked), so they
> measure center-line antipodal collinearity, not the real 3-orbit constraint. The
> "≥89% D₆ dominance" claim is **retracted**: with the correct genuine-hyperedge
> definition, the D₆ share *decreases* from ~63% (n=12) to ~28% (n=32) while
> high-slope triples dominate (~72% at n=32). See `analysis/d6_dominance_correction.md`.

The (1,1) dominance decreases from 23% to 13% as n grows, but remains the single most dangerous direction by an order of magnitude.

### Independent Sets

- All known rot4 solutions are **independent sets** in Hₙ^dir. Verified for n=12..32 with zero exceptions.
- Known solutions have **significantly lower mean degree** than random n-subsets:

| n | Solution Mean Danger | Random Mean Danger | Ratio |
|---|--------------------|-------------------|-------|
| 12 | 99.3 | 116.9 | 0.85 |
| 16 | 177.5 | 342.3 | 0.52 |
| 20 | 313.8 | 678.0 | 0.46 |
| 24 | 280.3 | 1161.4 | 0.24 |
| 28 | 1147.2 | 2117.3 | 0.54 |
| 32 | 1342.7 | 3089.2 | 0.44 |

Solutions consistently have ~40-60% lower mean danger than random subsets, confirming that solutions actively avoid high-danger directions.

---

## 3. Theoretical Tools

### 3.1 Hypergraph Turán Problem

The fundamental question: what is the maximum size of an independent set in Hₙ?

Equivalently, what is the Turán number ex₃(n²/2, Hₙ) — the maximum number of hyperedges in an n²/2-vertex 3-uniform hypergraph that contains no "dangerous" triple?

If we can prove that α(Hₙ) < c·n for some c < 2, this would provide a theoretical upper bound on the number of points in a no-three-in-line configuration.

**Why this is hard**: Hₙ is not a "nice" hypergraph from a standard family (e.g., it's not a Steiner system, not a random hypergraph, not a geometric hypergraph in the usual sense). Its structure is dictated by the arithmetic of lattice point collinearity.

### 3.2 Container Method (Balogh–Morris–Samotij)

The container method is designed for **sparse hypergraphs** with good "supersaturation" properties. Key requirements:

1. **Sparsity**: ✅ Edge density ≤ 1.2% and decreasing with n.
2. **Supersaturation**: ❓ Unknown. Does a set of size k ≫ α(Hₙ) necessarily contain many hyperedges? This would need to be established.
3. **Co-degree regularity**: ❓ The co-degree (number of hyperedges containing a given pair of vertices) likely varies wildly due to the (1,1) concentration.

**If** container method applies, we could bound both α(Hₙ) and the number of maximal independent sets — giving a theoretical count of solutions.

### 3.3 Probabilistic Method / LLL

Each direction has a "danger" value — the number of hyperedges containing it. For random n-subsets, the expected number of hyperedges in the induced subgraph is:

E[|E(Hₙ[random n-set])|] = C(n,3) · (edge density)

For n=20: C(20,3)=1140, edge density=0.48% → expected ~5.5 hyperedges per random set.

The Lovász Local Lemma could potentially guarantee existence of n-subsets with zero hyperedges for certain n, if the dependencies are manageable.

### 3.4 Linear Algebra / Spectral Methods

If we represent Hₙ as a 3-tensor A where A_{ijk} = 1 if {i,j,k} is a hyperedge, then finding an independent set of size n is equivalent to finding a 0-1 vector x with |x|₁ = n and ⟨A, x⊗x⊗x⟩ = 0.

This is a **tensor optimization** problem. Spectral methods for hypergraphs (e.g., generalized eigenvalues) might provide upper bounds on α(Hₙ).

### 3.5 Number Theory: Sum-of-Two-Squares Connection

The danger-degree of direction (a,b) is related to the number of integer lattice points on lines with slope b/a that pass through the grid. For a primitive direction (a,b), the number of collinear triples involving that direction depends on:

- The number of lattice points on lines with slope b/a within the n×n grid
- The "multiplicity" of solutions to linear equations ax + by = c

This connects to:
- **Dirichlet's divisor problem** (counting lattice points on lines)
- **Fourier analysis on ℤ²** (structure of collinearity)
- **Quadratic forms** (the sum-of-two-squares representation r₂(d))

### 3.6 Connection to Missing-Center

A missing-center solution is an independent set in Hₙ with the additional constraint that no distance ring Rᵢ has ≥3 points.

In the direction hypergraph model, this is equivalent to selecting directions such that no set of 3 directions has the same squared distance from center:

If 3 directions (a₁,b₁), (a₂,b₂), (a₃,b₃) satisfy a₁²+b₁² = a₂²+b₂² = a₃²+b₃², they may (or may not) be a hyperedge. The missing-center constraint adds **a coarsening** of the hypergraph where we group directions by their squared norm.

**Theoretical question**: For what n does there exist an n-independent-set that also avoids having ≥3 directions with the same norm?

This is reminiscent of the **Erdős–Ginzburg–Ziv** type problems or **zero-sum** problems in additive combinatorics.

---

## 4. Open Problems (Immediate Next Steps)

### P1. Extend the empirical data
- Compute Hₙ for n=24,28,32 to confirm sparsity trend and degree distribution.
- Verify that the (1,1) dominance continues.
- Measure co-degree distribution.

### P2. Characterize hyperedge structure
- Prove a formula for the number of hyperedges containing direction (a,b) in terms of number-theoretic functions.
- Determine whether hyperedges can be characterized by a simple algebraic condition.

### P3. Bound the independence number
- Can we prove α(Hₙ^dir) ≤ n for all n≥something?
- Or conversely, find n where α(Hₙ^dir) < n?

### P4. Container theorem
- Does Hₙ satisfy the conditions for the container method?
- If so, bound the number of solutions.

### P5. Missing-center specific
- What is the maximum size of a set of directions with all pairwise-distinct norms?
- How does this interact with the hypergraph independent set condition?

---

## 5. References

1. Balogh, Morris, Samotij. "The method of hypergraph containers." ICM 2018.
2. Saxton, Thomason. "Hypergraph containers." Inventiones 2015.
3. Erdős–Ginzburg–Ziv theorem and generalizations.
4. Guy–Kelly (1968), Ellmann (2004) on the No-Three-In-Line asymptotics.
5. Prellberg (2026+) CP-SAT results.
6. Heule (2026) SAT results for n=65-72.
