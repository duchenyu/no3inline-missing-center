#!/usr/bin/env python3
"""
Step 2: Quantify the compound C4 constraint.
What fraction of 2-regular bipartite graphs survive the hypergraph filter?
"""
import os, math, json, random
from collections import defaultdict

def random_2regular(N, seed=42):
    """Generate a random 2-regular bipartite graph on N×N.
    Each row selects 2 distinct columns, each column appears in exactly 2 rows.
    Uses the pairing model: shuffle 2N row-half-edges and 2N col-half-edges.
    """
    rng = random.Random(seed)
    max_attempts = 100
    for attempt in range(max_attempts):
        # Create a permutation of 2N elements (row-half-edges -> col-half-edges)
        row_half_edges = []
        for r in range(N):
            row_half_edges.extend([r, r])
        col_half_edges = list(range(N)) * 2
        rng.shuffle(col_half_edges)
        
        # Build matrix
        cells = defaultdict(set)
        for row_idx, col in zip(row_half_edges, col_half_edges):
            cells[row_idx].add(col)
            if len(cells[row_idx]) > 2:
                break
        else:
            # Check column counts
            col_counts = defaultdict(int)
            for r, cols in cells.items():
                for c in cols:
                    col_counts[c] += 1
            if all(v == 2 for v in col_counts.values()) and all(len(v) == 2 for v in cells.values()):
                return cells
    return None

# Check collinearity for C4
def check_c4_collinear(domain_cells, N, n):
    """Check if the selected domain cells produce any collinear triple."""
    pts = []
    for (r, c) in domain_cells:
        # C4 orbit
        orbit = [(r,c), (c, n-1-r), (n-1-r, n-1-c), (n-1-c, r)]
        pts.extend(orbit)
    # Check all triples (sample if too large)
    total = len(pts)
    for i in range(total):
        for j in range(i+1, total):
            for k in range(j+1, total):
                x1,y1 = pts[i]; x2,y2 = pts[j]; x3,y3 = pts[k]
                if (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1):
                    return True  # Found collinear triple
    return False

def estimate_survival(N, trials=2000):
    """Estimate fraction of 2-regular graphs that survive hypergraph."""
    n = 2 * N
    survived = 0
    for t in range(trials):
        cells = random_2regular(N, seed=t*N+42)
        if cells is None:
            continue
        domain = []
        for r in sorted(cells.keys()):
            for c in sorted(cells[r]):
                domain.append((r, c))
        if not check_c4_collinear(domain, N, n):
            survived += 1
    return survived / trials

print("=" * 60)
print("C4 Compound Constraint: Survival Rate Estimation")
print("=" * 60)
print(f"\nEstimating: P(2-regular bipartite graph | hypergraph independence)")
print(f"(Random 2-regular → check collinearity)")
print()

# Quick estimate for small N (where it's tractable)
for N in [4, 5, 6, 7, 8]:
    sr = estimate_survival(N, trials=500)
    n = 2 * N
    total_2reg = math.factorial(2*N) // (2**N * math.factorial(N))
    log_total = N * math.log(N) if N > 0 else 0
    expected_sols = sr * total_2reg if sr > 0 else 0
    print(f"N={N:>2} (n={n:>3}): survival={sr:.4f} ({sr*100:.2f}%)")
    if sr > 0:
        print(f"  total 2-reg ~ {total_2reg:.1e}, expected C4 sols ~ {expected_sols:.1e}")
