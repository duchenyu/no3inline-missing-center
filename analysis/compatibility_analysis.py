#!/usr/bin/env python3
"""
C4 compatibility graph and 2-regular graph bottleneck analysis.

Investigate why n=76 is difficult: since hypergraph constraint is weak,
the real bottleneck must be the C4 row-matching / 2-regular graph constraint.

Key questions:
1. For existing C4 solutions (n=12..56), what direction-compatibility patterns exist?
2. How does direction selection interact with the row-column matching?
3. Is there a structural barrier that emerges at n ≈ 76?
"""

import os, math, json, sys
from collections import defaultdict, Counter

ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}
CACHE = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis\flammenkamp_cache'

def dir_of(pt, n):
    """Reduced direction from even-n grid center C = ((n-1)/2, (n-1)/2)."""
    cx = cy = (n - 1) / 2.0
    a = pt[0] - cx
    b = pt[1] - cy
    # Scale to integers: 2a, 2b are integers since n is even
    ai = int(round(2 * a))
    bi = int(round(2 * b))
    if ai == 0 and bi == 0:
        return (0, 0)
    g = math.gcd(ai, bi) or 1
    ai //= g; bi //= g
    if ai < 0 or (ai == 0 and bi < 0):
        ai, bi = -ai, -bi
    return (ai, bi)


def decode_solution(line, n):
    """Decode a Flammenkamp-format solution, return list of (r,c) points in full grid."""
    line = line.rstrip()
    if not line:
        return None
    pre = line[0]
    body = line[1:] if pre in '.:/-ocx+*' else line
    if len(body) < 2 * n:
        return None
    pts = []
    for r in range(n):
        c1 = VAL.get(body[2*r])
        c2 = VAL.get(body[2*r+1])
        if c1 is None or c2 is None or c1 >= n or c2 >= n:
            return None
        pts.append((r, c1))
        pts.append((r, c2))
    return pts


def analyze_c4_solution(pts, n):
    """Extract direction usage and row-matching structure from a C4 solution.
    
    A C4 solution on even n×n grid has:
    - 2n points total
    - C4 symmetry: if (r,c) in solution then (c,n-1-r), (n-1-r,n-1-c), (n-1-c,r) in solution
    
    Under C4, the orbit of a point (r,c) partitions into:
    - If r ≠ c and r ≠ n-1-c and c ≠ n-1-r: orbit size 4
    - If r = c or r = n-1-c: orbit size could be 2
    
    We extract:
    - Directions used (one per orbit, via C2 reduction)
    - Row-column degree distribution
    - Structural invariants
    """
    seen = set()
    directions = []
    orbits = []
    
    for p in pts:
        if p in seen:
            continue
        # C4 orbit
        r, c = p
        orbit = [(r, c),
                 (c, n-1-r),
                 (n-1-r, n-1-c),
                 (n-1-c, r)]
        # Deduplicate within orbit
        unique_pts = list(dict.fromkeys(orbit))
        for op in unique_pts:
            seen.add(op)
        
        # Use C2 direction (from center to p)
        d = dir_of(p, n)
        directions.append(d)
        orbits.append((min(unique_pts), len(unique_pts)))
    
    return {
        'directions': directions,
        'num_orbits': len(directions),
        'orbit_sizes': [s for _, s in orbits],
    }


def load_rot4_solutions(n):
    """Load all rot4 solutions for given n from cache."""
    sols = []
    for ext in ['', '.few']:
        p = os.path.join(CACHE, f'n{n}_rot4{ext}')
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    c = decode_solution(line, n)
                    if c:
                        sols.append(c)
    return sols


def count_column_degrees(pts, n):
    """In the full grid, count how many points per column."""
    col_cnt = defaultdict(int)
    for r, c in pts:
        col_cnt[c] += 1
    return col_cnt


def row_matching_structure(pts, n):
    """Extract the row-matching structure.
    
    In C4, each row r in [0,n) has exactly 2 points.
    The matching pairs (cols of each row) define a 2-regular graph.
    
    Also: column degree must be 2 for all columns (by 2-per-row + C4 symmetry).
    """
    # Per-row columns
    row_cols = defaultdict(list)
    for r, c in pts:
        row_cols[r].append(c)
    
    # Verify each row has exactly 2
    for r, cols in row_cols.items():
        assert len(cols) == 2, f"Row {r} has {len(cols)} cols: {cols}"
    
    # Column degrees
    col_deg = Counter(c for cols in row_cols.values() for c in cols)
    
    return {
        'row_pairs': dict(row_cols),
        'col_degs': dict(col_deg),
        'col_deg_dist': dict(Counter(col_deg.values())),
    }


def direction_table(n_max=56):
    """Build direction usage table across all C4 solutions."""
    print(f"{'n':>3}  {'sols':>6}  {'dirs/sol':>9}  {'heavy_avg':>9}  {'heavy_max':>9}  {'growth':>8}")
    print("-" * 55)
    
    growth_rates = []
    prev_count = None
    
    HEAVY = {(1,1), (1,-1), (3,1), (1,3), (3,-1), (1,-3)}
    
    results = []
    
    for n in range(6, n_max + 1, 2):
        sols = load_rot4_solutions(n)
        if not sols:
            continue
        
        all_heavy_counts = []
        all_dir_counts = []
        
        for pts in sols:
            info = analyze_c4_solution(pts, n)
            all_dir_counts.append(info['num_orbits'])
            heavy_count = sum(1 for d in info['directions'] if d in HEAVY)
            all_heavy_counts.append(heavy_count)
        
        avg_heavy = sum(all_heavy_counts) / len(all_heavy_counts)
        max_heavy = max(all_heavy_counts)
        avg_dirs = sum(all_dir_counts) / len(all_dir_counts)
        
        # Growth rate
        growth = ""
        if prev_count is not None and prev_count > 0:
            rate = len(sols) / prev_count
            growth = f"{rate:>7.3f}x"
            growth_rates.append(rate)
        
        print(f"{n:>3}  {len(sols):>6,}  {avg_dirs:>8.1f}  {avg_heavy:>8.2f}  {max_heavy:>8}  {growth}")
        
        results.append({
            'n': n,
            'num_solutions': len(sols),
            'avg_dirs_per_sol': avg_dirs,
            'avg_heavy': avg_heavy,
            'max_heavy': max_heavy,
        })
        prev_count = len(sols)
    
    if growth_rates:
        print(f"\nAverage growth rate (per +2 step): {sum(growth_rates)/len(growth_rates):.3f}x")
    
    return results


def row_matching_analysis(n_max=56):
    """Analyze row-matching patterns. Key question: how does the 2-regular graph 
    structure evolve with n?"""
    print(f"\n=== Row Matching Structure Analysis ===")
    print(f"{'n':>3}  {'sols':>6}  {'col_deg_2':>9}  {'col_deg_1':>9}  {'col_deg_3+':>9}  {'pairs_repeat':>12}")
    print("-" * 55)
    
    for n in range(6, n_max + 1, 2):
        sols = load_rot4_solutions(n)
        if not sols:
            continue
        
        col_deg2_ok = 0
        col_deg1 = 0
        col_deg3plus = 0
        repeat_pairs = 0
        
        for pts in sols:
            rm = row_matching_structure(pts, n)
            deg_dist = rm['col_deg_dist']
            col_deg2_ok += deg_dist.get(2, 0)
            col_deg1 += deg_dist.get(1, 0)
            col_deg3plus += sum(v for k, v in deg_dist.items() if k >= 3)
            
            # Check if any row has duplicate column pairs (same pair in different rows)
            pairs_seen = set()
            for r, cols in rm['row_pairs'].items():
                pair = tuple(sorted(cols))
                if pair in pairs_seen:
                    repeat_pairs += 1
                pairs_seen.add(pair)
        
        total_sols = len(sols)
        avg_deg2 = col_deg2_ok / total_sols
        avg_deg1 = col_deg1 / total_sols
        avg_deg3 = col_deg3plus / total_sols
        avg_repeat = repeat_pairs / total_sols
        
        print(f"{n:>3}  {total_sols:>6}  {avg_deg2:>8.1f}  {avg_deg1:>8.1f}  {avg_deg3:>8.1f}  {avg_repeat:>11.2f}")


def direction_compatibility_analysis(n_max=56):
    """Analyze the compatibility between directions.
    
    For each pair of directions (d1, d2), check if they co-occur in solutions
    more or less often than expected by chance.
    """
    print(f"\n=== Direction Compatibility Patterns ===")
    
    HEAVY = {(1,1), (1,-1), (3,1), (1,3), (3,-1), (1,-3)}
    
    for n in [16, 24, 32, 40, 48, 56]:
        sols = load_rot4_solutions(n)
        if len(sols) < 3:
            continue
        
        # Count co-occurrence of each heavy direction pair
        cooccur = defaultdict(int)
        heavy_counts = defaultdict(int)
        total = len(sols)
        
        for pts in sols:
            info = analyze_c4_solution(pts, n)
            dirs_used = set(info['directions'])
            heavy_used = [d for d in dirs_used if d in HEAVY]
            
            for d in heavy_used:
                heavy_counts[d] += 1
            
            for i, d1 in enumerate(heavy_used):
                for d2 in heavy_used[i+1:]:
                    pair = tuple(sorted([d1, d2]))
                    cooccur[pair] += 1
        
        print(f"\nn={n} ({total} solutions):")
        print(f"  Heavy direction frequencies:")
        for d in sorted(HEAVY):
            freq = heavy_counts.get(d, 0)
            pct = freq / total * 100
            print(f"    {str(d):>8}: {freq:>4}/{total} ({pct:>5.1f}%)")
        
        print(f"  Heavy direction co-occurrence (pairwise):")
        for pair in sorted(cooccur.keys()):
            cnt = cooccur[pair]
            d1, d2 = pair
            p1 = heavy_counts.get(d1, 0) / total
            p2 = heavy_counts.get(d2, 0) / total
            expected = p1 * p2 * total
            ratio = cnt / expected if expected > 0 else 0
            emoji = "🟢" if ratio > 1.2 else ("🔴" if ratio < 0.8 else "⚪")
            print(f"    {str(d1):>8} + {str(d2):>8}: {cnt:>4} (exp={expected:.1f}, ratio={ratio:.2f}) {emoji}")


def domain_compatibility_analysis(n, N=None):
    """Analyze the compatibility between C4 domain cell pairs.
    
    Two domain cells (r1,c1) and (r2,c2) are 'compatible' if they do NOT
    create a collinear triple in the full grid.
    
    This builds the compatibility graph for the C4 solver's search space.
    """
    if N is None:
        N = n // 2
    
    cx = cy = (n - 1) / 2.0
    total_domain = N * N
    
    # For speed: check direction compatibility
    # Two orbits (with dirs d1, d2) are incompatible if there exists a third
    # point somewhere that makes all three collinear AND the third point
    # comes from a third orbit.
    
    # Actually, for the compatibility matrix, we want:
    #   Two domain cells (r1,c1), (r2,c2) are compatible iff 
    #   no point in orbit1 ∪ orbit2 is collinear with 
    #   any two points spanning orbit1 × orbit2
    
    # This is expensive for large N. Instead, use the direction-level analysis.
    # Two directions d1, d2 are compatible if no pair (p1 from orbit with dir d1,
    # p2 from orbit with dir d2) plus a third point from ANYWHERE creates collinearity.
    
    return None  # Placeholder - detailed analysis below


def predictive_model():
    """Build a predictive model for C4 solution count at n=76.
    
    Use data from n=10..56 to fit the growth curve.
    """
    print(f"\n=== C4 Solution Count Predictive Model ===")
    
    ns = list(range(6, 58, 2))
    counts = {}
    
    for n in ns:
        sols = load_rot4_solutions(n)
        if sols:
            counts[n] = len(sols)
    
    # Exponential fit: log(count) ~ a + b*n
    import math
    points = [(n, math.log(c)) for n, c in sorted(counts.items())]
    
    # Simple linear regression on log(count) ~ n
    n_vals = [p[0] for p in points]
    logc_vals = [p[1] for p in points]
    
    mean_n = sum(n_vals) / len(n_vals)
    mean_logc = sum(logc_vals) / len(logc_vals)
    
    num = sum((n - mean_n) * (lc - mean_logc) for n, lc in zip(n_vals, logc_vals))
    den = sum((n - mean_n)**2 for n in n_vals)
    
    b = num / den
    a = mean_logc - b * mean_n
    
    print(f"  log(C4_count) = {a:.4f} + {b:.4f} × n")
    print(f"  Growth factor per +2 step: {math.exp(2*b):.4f}x")
    
    # Predict for n=76
    n_pred = 76
    pred_log = a + b * n_pred
    pred_count = math.exp(pred_log)
    print(f"\n  Predicted C4 count at n=76: {pred_count:.1f}")
    print(f"  (log scale: {pred_log:.2f})")
    
    # Also compute per-n growth rates
    print(f"\n  Per-step growth rates (actual):")
    sorted_n = sorted(counts.keys())
    for i in range(1, len(sorted_n)):
        n_prev = sorted_n[i-1]
        n_curr = sorted_n[i]
        rate = counts[n_curr] / counts[n_prev]
        step = n_curr - n_prev
        per2 = rate ** (2/step)  # Normalize to per +2 step
        print(f"    {n_prev}→{n_curr}: {counts[n_prev]:,} → {counts[n_curr]:,} = {rate:.3f}x ({per2:.3f}x per +2)")
    
    # Growth rate trend (is it decreasing?)
    rates = []
    for i in range(1, len(sorted_n)):
        n_prev = sorted_n[i-1]
        n_curr = sorted_n[i]
        rate = counts[n_curr] / counts[n_prev]
        step = n_curr - n_prev
        per2 = rate ** (2/step)
        rates.append((n_curr, per2))
    
    # Fit growth rate as function of n
    if len(rates) >= 5:
        late_rates = rates[-5:]
        avg_late = sum(r for _, r in late_rates) / len(late_rates)
        print(f"\n  Recent avg growth rate (last 5): {avg_late:.3f}x per +2")
        
        # If trend continues at avg_late, what would n=76 have?
        last_n = sorted_n[-1]
        last_count = counts[last_n]
        steps_to_76 = (76 - last_n) // 2
        extrapolated = last_count * (avg_late ** steps_to_76)
        print(f"  Extrapolated n=76 from n={last_n} ({avg_late:.3f}x/step, {steps_to_76} steps): {extrapolated:.0f}")


if __name__ == '__main__':
    print("=" * 60)
    print("C4 Compatibility Graph & 2-Regular Graph Bottleneck")
    print("=" * 60)
    
    # 1. Direction usage table
    direction_table(56)
    
    # 2. Row matching structure
    row_matching_analysis(56)
    
    # 3. Direction compatibility
    direction_compatibility_analysis(56)
    
    # 4. Predictive model
    predictive_model()
