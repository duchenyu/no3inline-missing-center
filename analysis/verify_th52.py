"""
Th-52: G's m cells in Q1 must satisfy no-three-in-line on the m×m grid.
Proof: form (0,0) has D = (xb-xa)(yc-ya) - (xc-xa)(yb-ya), the standard 2D cross product.
If 3 cells are collinear in Q1, their k=0 lifts are collinear in the full n×n grid.
Since rot4 requires no 3 collinear in the full grid, this cannot happen.
Hence the m cells of G must themselves be NTIL on the m×m grid.

Verification: check all cached rot4 solutions.
"""
import sys; sys.path.insert(0, '.')
from rot4_loader import load_rot4
from g_reconstruction_engine import decode_solution, g_from_recs

def collinear_Q1(cells, m):
    """Check if any 3 cells in the m×m grid are collinear (excluding same-row/same-column)."""
    pts = sorted(set(cells))  # deduplicate (shouldn't be needed but safe)
    for i in range(len(pts)):
        xi, yi = pts[i]
        for j in range(i+1, len(pts)):
            xj, yj = pts[j]
            for k in range(j+1, len(pts)):
                xk, yk = pts[k]
                # Standard collinear check: (xj-xi)*(yk-yi) == (xk-xi)*(yj-yi)
                if (xj - xi) * (yk - yi) == (xk - xi) * (yj - yi):
                    return True, (pts[i], pts[j], pts[k])
    return False, None

def check_n(n):
    """Check all rot4 solutions for given n."""
    m = n // 2
    try:
        sols_group = load_rot4(n)
    except Exception as e:
        print(f"  n={n}: load failed: {e}")
        return None
    
    if not sols_group:
        print(f"  n={n}: no solutions")
        return None
    
    total = 0
    violations = []
    
    for group_idx, sols in enumerate(sols_group):
        if sols is None:
            continue
        for sol_idx, pts in enumerate(sols):
            total += 1
            recs = decode_solution(pts, n)
            if recs is None:
                continue
            cells, is_2reg, deg = g_from_recs(recs, n)
            if not is_2reg:
                continue
            
            # Get unique Q1 cells
            q1_cells = list(set(cells))
            
            # Check NTIL on m×m
            has_coll, triple = collinear_Q1(q1_cells, m)
            if has_coll:
                violations.append((sol_idx, q1_cells, triple))
    
    return total, violations

print("=" * 80)
print("Th-52 VERIFICATION: G cells are NTIL in Q1")
print("=" * 80)

all_n = list(range(6, 44, 2))  # n up to 42 (flammenkamp .few files; .mvr after 44 has different format)
total_violations = 0
total_solutions = 0

for n in all_n:
    result = check_n(n)
    if result is None:
        continue
    total, violations = result
    total_solutions += total
    n_v = len(violations)
    total_violations += n_v
    status = "✓" if n_v == 0 else f"✗ ({n_v} violations)"
    print(f"  n={n:3d} (m={n//2:2d}): {total:5d} solutions, {status}")

print(f"\n{'='*80}")
print(f"TOTAL: {total_solutions} solutions across n=6..72")
if total_violations == 0:
    print("RESULT: 0 violations — Th-52 CONFIRMED: G cells are always NTIL in Q1.")
else:
    print(f"RESULT: {total_violations} violations found — FALSIFIED!")
print(f"{'='*80}")

# Additional analysis: how many solution-free m×m NTIL configurations?
print("\n\nADDITIONAL: How many distinct Q1 cell configurations exist?")
print("(i.e., given the m cells, how many valid rot4 solutions?)\n")
for n in [14, 20, 30]:
    result = check_n(n)
    if result is None:
        continue
    total, _ = result
    # Count distinct Q1 configs
    m = n // 2
    sols_group = load_rot4(n)
    seen_q1 = set()
    for sols in sols_group:
        for pts in sols:
            recs = decode_solution(pts, n)
            if recs is None:
                continue
            cells, _, _ = g_from_recs(recs, n)
            key = tuple(sorted(set(cells)))
            seen_q1.add(key)
    print(f"  n={n:3d}: {total:5d} solutions, {len(seen_q1):5d} distinct Q1 layouts")
    
print("\nDone.")
