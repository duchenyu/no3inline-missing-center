# Structural characterisation of even‑n no‑three‑in‑line solutions
### Lemma‑1 reduction · conflict hypergraph · GPU exact solver
*(working note, 2026‑07‑08 — honest scope labels throughout)*

---

## 0.  Scope / honesty preamble

We distinguish three kinds of claim and label them consistently:

| label | meaning |
|-------|---------|
| **PROVEN** | follows by elementary argument (lemmas below). |
| **EMPIRICAL** | observed across the cached Flammenkamp solutions; a *characterisation*, not a proof. Sample sizes vary; see caveats. |
| **COMPUTATIONAL EVIDENCE** | produced by an exact search on this machine. Confirms existence for the tested `n`; does **not** prove it for all `n`. |

The open problem is `D(n) = 2n` for every even `n`. The upper bound `D(n) ≤ 2n` is elementary
(≤2 points per row). What is open is the **lower bound** — an explicit 2n‑point construction for
every even `n`. This note advances the *understanding* of that obstacle; it does **not** claim a proof.

---

## 1.  Lemma 1 reduction — the precise remaining obstacle  (**PROVEN**)

For even `n`, let `C = ((n−1)/2,(n−1)/2)` be the grid centre and `R₁₈₀(r,c)=(n−1−r,n−1−c)`.

**Lemma 1 (C₂ theorem).** *If a 2n‑point no‑three‑in‑line solution `S` is `R₁₈₀`‑invariant, then
`S` decomposes into exactly `n` `R₁₈₀`‑orbits, each determining a line through `C`, and these `n`
central lines are pairwise distinct.*

The proof is in `lemmas_c2_ring.md` (involution + no‑three‑collinear ⇒ no two orbits share a
central line). **Consequence:** for the `R₁₈₀`‑invariant case the *centre‑line* collinearity is
**fully solved** — it is exhausted by the single condition "the `n` central directions are
distinct". The *only* remaining obstacle is **off‑centre** collinearity among the 2n points.

So the construction problem reduces to:

> **(★) Orbit‑selection problem.** Choose `n` `R₁₈₀`‑orbits with pairwise distinct central
> directions such that no three of the 2n points lie on a line *not* through `C`.

This is the exact form in which we now study the obstacle (Sections 3–4). It is precisely the
"Lemma‑1 reduction" requested.

**Empirical backing of Lemma 1.** Across every sampled `R₁₈₀`‑invariant solution in the
Flammenkamp cache (classes `rot2`, `rot4`, `dia2`, `n ≡ 0 (mod 4)`, `n = 12..72`) the
distinct‑direction condition holds **100%** (e.g. `rot4`: 4/4, 13/13, …, 10441/10441, 1/1). No
counterexample exists in the data.

---

## 2.  Why pairwise (2‑uniform) conflict is the wrong model  (**EMPIRICAL**)

An early hypothesis: maybe two "bad" orbits already create an off‑centre collinear triple, so a
*graph* (pairwise conflict) would suffice. `direction_d_conflict_graph.py` tested this:

* On the full `n²` grid the pairwise (orbit‑vs‑orbit) conflict graph is extremely sparse.
* On the `rot2` orbit graph, near‑zero pair conflicts were found, yet the corresponding
  SAT instance is **UNSAT** for `n = 31`.

**Conclusion:** the obstruction is *higher‑order*. Two orbits almost never collide by themselves;
a forbidden configuration needs **three** orbits. The correct model is therefore a **3‑uniform
hypergraph**, not a graph. This is the honest reason the earlier graph/spectral attempts stalled.

---

## 3.  The danger hypergraph  (**EMPIRICAL**, `danger_hypergraph.py`)

Build the orbit space for even `n` and a 3‑uniform hypergraph `H_n`:
* vertices = `R₁₈₀`‑orbits (one per central direction);
* a triple of orbits is a **forbidden hyperedge** iff its 6 points contain an off‑centre
  collinear triple.

A solution of problem (★) is exactly an **independent set of size `n`** in `H_n`.

| n | orbits | orbit‑triples | forbidden triples | % forbidden | max danger‑degree (dir) | sol mean‑danger | random mean‑danger |
|---|--------|---------------|-------------------|------------|--------------------------|-----------------|--------------------|
| 12 | 72  | 59,640    | 691   | 1.16% | 743  (1,1)   | 99.3  | 118.5 |
| 16 | 128 | 341,376   | 2,746 | 0.80% | 2,493 (1,1)  | 177.5 | 320.4 |
| 20 | 200 | 1,313,400 | 6,325 | 0.48% | 6,209 (1,1)  | 313.8 | 631.4 |

Observations (all **EMPIRICAL**):

1. **Forbidden triples are rare and become rarer with `n`** (1.16% → 0.80% → 0.48%). Most orbit
   triples are harmless. The obstacle is *sparse* but *structured*, not a dense wall.
2. **Danger is extremely concentrated.** The single direction `(1,1)` (main diagonal) has
   danger‑degree 743 → 2493 → 6209 — it dominates the hypergraph. `(1,−1)` (anti‑diagonal) is a
   close second. Low‑slope / small‑integer directions are the dangerous ones; large coprime
   directions are nearly safe individually (though they still participate in triples).
3. **Solutions actively avoid danger.** The mean danger‑degree of a real solution's chosen
   directions is *below* that of a random `n`‑subset of directions (99 vs 118; 177 vs 320; 314 vs
   631). Real solutions are not random — they steer away from the dangerous diagonal directions.
4. **Sanity:** every loaded solution is an independent set in `H_n` (4/4, 13/13, 16/16). The
   hypergraph model is faithful.

---

## 4.  Directional structure of `n ≡ 0 (mod 4)` rot4 solutions  (**EMPIRICAL**, `struct_n0mod4.py`)

For the `rot4` class (C₄ symmetry) we additionally have **90° closure** (Lemma‑1 orbits come in
`θ, θ+π/2` pairs, exactly `(a,b) ↔ (b,−a)` in integer vectors). We verify it and profile the
direction multiset.

**4a. Lemma 1 + 90° closure — verified 100% for every sampled `rot4` solution**
(`n = 12,16,20,24,28,32,36,40,44,56,60,64,68,72`; plain cache up to 56, `.few` compact cache
60–72):

* orbit count per solution = exactly `n` (Lemma 1 predicts `n`);
* distinct‑direction check passes for **all** sampled solutions (e.g. 10441/10441 at n=56, 1/1 at n=72);
* 90°‑closure check passes for **all** sampled solutions.

This is the strongest empirical regularity we have: within the `rot4` class the Lemma‑1 structure
is not just possible, it is universal in the sample.

**4b. Direction availability is NOT the bottleneck.** "Forbidden directions" (directions used by
zero sampled solutions) shrink as the sample grows:

| n | #solutions cached | forbidden‑direction % |
|---|-------------------|------------------------|
| 12 | 4   | 37.9% |
| 28 | 58  | 3.9%  |
| 36 | 281 | 0.4%  |
| 44 | 1016| 0.0%  |
| 56 | 10441 | 0.0% |
| 60 | 32 (.few)  | 30.0% |
| 68 | 2  (.few)  | 93.2% |
| 72 | 1  (.few)  | 96.6% |

**Sampling caveat (important).** The high "forbidden %" at `n = 60,64,68,72` is an artefact of the
`.few` compact cache, which stores only 1–32 solutions for those large `n`. With a *full* sample
(e.g. n=44 with 1016 solutions, n=56 with 10441) essentially **every** direction is used by at
least one solution. So direction *availability* does not explain the difficulty; the difficulty is
the *joint* off‑centre constraint (Section 3).

**4c. Angular uniformity.** Real solutions spread their directions more evenly than a random
direction set: the std‑dev of angular gaps between consecutive directions is **below** the random
baseline for every `n` tested (e.g. n=12: 0.199 vs 0.211; n=44: 0.061 vs 0.071). Equivalently,
solutions avoid near‑parallel central lines. (A "paired‑random" null model that enforces 90°
closure shows *even larger* gaps, confirming solutions are more uniform than closure alone forces.)

---

## 5.  What is proven vs what is evidence  (honest boundary)

**PROVEN**
* `D(n) ≤ 2n` (elementary).
* Lemma 1: for `R₁₈₀`‑invariant solutions, centre‑line collinearity ⇔ distinct central directions
  (fully solved); the remaining obstacle is off‑centre collinearity (problem ★).
* Lemma 2: `rot4` ring populations are multiples of 4 (⇒ rot4 solutions are never missing‑centre).
* Lemma 3: 4‑colouring (every line meets ≤2 colours); colour balance for rot4/rct4.
* Hypergraph model (§3) is faithful: all sampled solutions are independent sets.

**EMPIRICAL (characterisation, not proof)**
* Lemma‑1 distinct‑direction structure is universal within sampled `rot4`/`rot2`/`dia2` data.
* Off‑centre obstruction is sparse, higher‑order, and concentrated in low‑slope (diagonal)
  directions; solutions avoid it by angular uniformity.
* Direction *availability* is not the limiting factor (small‑sample caveat noted).

**OPEN / UNPROVEN**
* `D(n) = 2n` for **all** even `n`. Computational evidence exists up to `n = 72`
  (Heule / Flammenkamp). Our GPU solver (§6) adds independent exact confirmation at `n ≤ 12`.

---

## 6.  GPU exact solver  (`analysis/gpu_smoke/n3line_gpu.cu`)

**Design.** Exact 2n‑point backtracking (≤2 points per row). At each row a CUDA kernel marks, in
parallel, which column‑pairs are still "safe" given the already‑placed points (it tests every
triple containing a newly placed point via exact integer cross‑product). The CPU performs the DFS
traversal; the GPU prunes each row's branching. A randomized‑restart mode reorders column‑pairs
per row (same exact search, different first solution) so a single run locates a solution at
larger `n` without exhausting a lexicographic dead region.

The search is **exact and complete** for a given `n`: by induction every 3‑point triple is tested
when its third member is placed, so any returned solution is guaranteed collinearity‑free, and a
full run (SOL_CAP unbounded) is an exhaustive enumeration.

**Toolchain.** CUDA 13.3 + VS2026 (VC 14.44) on an NVIDIA RTX 4070 SUPER (12 GB). Compiled under
PowerShell with native `$env:PATH/INCLUDE/LIB` (no `cmd.exe`).

**Validation (COMPUTATIONAL EVIDENCE).**

| n | result | nodes | gpu time | independent verification |
|---|--------|-------|----------|--------------------------|
| 4  | solution found | 14      | 0.03 s  | `verify_solution.py`: VALID (8 pts, 0 bad triples) |
| 8  | solution found | 21,914  | 1.35 s  | VALID |
| 12 | solution found | 236k–1.0M (seed‑dependent) | 18.6–81.7 s | VALID (24 pts, 2024 triples, 0 collinear) |

The n=12 solution was cross‑checked by an *independent* Python verifier
(`verify_solution.py`, exact integer arithmetic) — 0 collinear triples out of 2024.

**Honest limit.** The DFS is exponential in `n`. Pushing existence evidence to `n > 72` by brute
force is a Heule‑scale problem and is **not** feasible with this single‑machine DFS, GPU‑assisted
or not. Any solution found at larger `n` would be *computational evidence*, never a proof.

---

## 7.  Principled next step: orbit‑reduced GPU search

The solver in §6 searches the 2n‑point space directly. The Lemma‑1 reduction (§1) suggests a far
smaller, more principled search:

* **Search space = problem (★):** pick `n` orbits (vertices of `H_n`) forming an independent set
  of size `n`.
* The centre‑line constraint is *gone* (distinct directions enforced by construction).
* The GPU is better used here: the independent‑set / hypergraph‑clique search parallelises over
  candidate orbit subsets, and the danger‑degree concentration (§3) gives a strong
  smallest‑danger‑first heuristic that should prune dramatically better than row‑by‑row DFS.

This is the natural continuation of "Lemma‑1 reduction + conflict hypergraph" and the right
vehicle for attempting `n = 76` (next `n ≡ 0 (mod 4)`). It remains a *search*, hence at best
computational evidence — the open problem `D(n)=2n` stays open.

---

## File index

| file | role |
|------|------|
| `lemmas_c2_ring.md` | Proven Lemmas 1–3 + honest proof‑boundary discussion. |
| `struct_n0mod4.py` / `struct_n0mod4_report.txt` | Lemma‑1 + 90°‑closure verification and directional profiling for `n ≡ 0 (mod 4)` rot4. |
| `danger_hypergraph.py` / `danger_hypergraph_report.txt` | 3‑uniform danger hypergraph; forbidden‑triple stats; danger concentration. |
| `direction_d_conflict_graph.py` | Earlier graph model; shows obstruction is higher‑order (motivates §2/§3). |
| `gpu_smoke/n3line_gpu.cu` | CUDA‑accelerated exact 2n‑point solver (randomized‑restart mode). |
| `gpu_smoke/verify_solution.py` | Independent exact verifier for a found solution. |
| `gpu_smoke/n12_seed*.log` | Sample validated runs (n=12). |
