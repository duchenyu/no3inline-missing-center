#!/usr/bin/env python3
"""
Extract ring assignment from RLE solutions and test the ring-guided solver.
Usage:
    python prep_ring_assignment.py <n> <rle_file>  # extract from RLE
    python prep_ring_assignment.py <n> --generate   # generate candidate assignments
"""

import sys
from collections import defaultdict
import os

# Import parser from analyze_rle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_rle import parse_rle

def check_missing_center(pts, n):
    """Check if grid center is NOT a circumcenter of any triple."""
    from collections import Counter
    if n % 2 == 0:
        cx2, cy2 = n - 1, n - 1
    else:
        c = 2 * (n // 2)
        cx2, cy2 = c, c
    dist_counts = Counter()
    for x, y in pts:
        dx = 2 * x - cx2
        dy = 2 * y - cy2
        d = dx * dx + dy * dy
        dist_counts[d] += 1
    max_share = max(dist_counts.values())
    return max_share <= 2

def collinear(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2) == 0

def build_rings(n):
    cx2 = cy2 = n - 1
    rings = defaultdict(list)
    for r in range(n):
        for c in range(n):
            d = (2*c - cx2)**2 + (2*r - cy2)**2
            rings[d].append((r, c))
    return dict(sorted(rings.items()))

def verify_solution(pts, n):
    """Full verification."""
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            for k in range(j+1, len(pts)):
                if collinear(pts[i], pts[j], pts[k]):
                    return False, f"Collinear: {pts[i]}, {pts[j]}, {pts[k]}"
    from collections import Counter
    row_cnt = Counter(p[1] for p in pts)
    col_cnt = Counter(p[0] for p in pts)
    if any(v != 2 for v in row_cnt.values()):
        return False, f"Row counts: {dict(row_cnt)}"
    if any(v != 2 for v in col_cnt.values()):
        return False, f"Col counts: {dict(col_cnt)}"
    return True, "OK"

def extract_assignment(pts, n):
    """Extract ring assignment {d: count} from a solution."""
    rings = build_rings(n)
    cx2 = cy2 = n - 1
    counts = defaultdict(int)
    for x, y in pts:
        d = (2*x - cx2)**2 + (2*y - cy2)**2
        counts[d] += 1
    return dict(counts)

def write_assignment_file(assignment, filename, n):
    with open(filename, 'w') as f:
        f.write(f"# Ring assignment for n={n}\n")
        for d, c in sorted(assignment.items()):
            if c > 0:
                f.write(f"{d} {c}\n")
    print(f"  Written to {filename}")
    print(f"  Total points: {sum(assignment.values())} (need {2*n})")

def analyze_rle_missing_assignments(rle_file, n):
    with open(rle_file) as f:
        text = f.read()
    
    sols = parse_rle(text, n)
    print(f"Parsed {len(sols)} solutions from {rle_file}")
    
    missing = []
    for pts in sols:
        if check_missing_center(pts, n):
            missing.append(pts)
    
    print(f"Found {len(missing)} missing-center solutions")
    
    rings = build_rings(n)
    use_count = defaultdict(int)
    skip_sets = []
    
    for pts in missing:
        assig = extract_assignment(pts, n)
        skipped = [d for d in rings if assig.get(d, 0) == 0]
        skip_sets.append(set(skipped))
        for d, c in assig.items():
            if c > 0:
                use_count[d] += 1
    
    total = len(missing)
    if skip_sets:
        common_skipped = set.intersection(*skip_sets) if skip_sets else set()
        print(f"\n  Rings skipped in ALL ({len(common_skipped)}):")
        for d in sorted(common_skipped):
            print(f"    d={d:4d}: {rings[d]}")
        
        universal = [d for d, c in use_count.items() if c == total]
        print(f"\n  Rings used in ALL ({len(universal)}):")
        for d in sorted(universal):
            print(f"    d={d:4d}: {rings[d]}")
        
        print(f"\n  Ring usage across all {total} solutions:")
        for d in sorted(rings.keys()):
            pct = use_count.get(d, 0) / total * 100
            print(f"    d={d:4d}: {use_count.get(d, 0):3d}/{total} ({pct:5.1f}%)")
    
    if missing:
        print(f"\n  First missing-center solution:")
        for x, y in sorted(missing[0], key=lambda p: (p[1], p[0])):
            cx2 = cy2 = n - 1
            d = (2*x - cx2)**2 + (2*y - cy2)**2
            print(f"    (col={x}, row={y}) d={d}")
        
        assig = extract_assignment(missing[0], n)
        print(f"\n  Its ring assignment:")
        for d, c in sorted(assig.items()):
            print(f"    d={d:4d}: {c} pt(s)")
        
        ok, msg = verify_solution(missing[0], n)
        print(f"\n  Verification: {msg}")
    
    return missing[0] if missing else None

def generate_candidate_assignments(n, max_skip=6):
    rings = build_rings(n)
    ring_list = list(rings.keys())
    caps = {d: len(pts) for d, pts in rings.items()}
    
    print(f"\nGenerating ring assignments for n={n} (max_skip={max_skip}):")
    print(f"  Rings: {len(ring_list)}, Target: {2*n} pts")
    
    candidates = []
    
    for skip_count in range(0, min(max_skip + 1, len(ring_list))):
        skipped = set(ring_list[:skip_count])
        used = [d for d in ring_list if d not in skipped]
        
        for x in range(len(used) + 1):
            y = 2*n - 2*x
            if y < 0:
                continue
            if x + y > len(used):
                continue
            
            assig = defaultdict(int)
            for i, d in enumerate(used):
                if i < x:
                    assig[d] = 2 if 2 <= caps[d] else 1
                elif i < x + y:
                    assig[d] = 1
            
            if sum(assig.values()) == 2 * n:
                candidates.append((skip_count, dict(assig)))
    
    print(f"  Found {len(candidates)} candidate assignments")
    return candidates


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python prep_ring_assignment.py <n> <rle_file>")
        print("  python prep_ring_assignment.py <n> --generate")
        sys.exit(1)
    
    n = int(sys.argv[1])
    
    if len(sys.argv) >= 3 and sys.argv[2] == '--generate':
        candidates = generate_candidate_assignments(n)
        if candidates:
            skip_count, assig = candidates[0]
            outfile = f"ring_assignment_n{n}_skip{skip_count}.txt"
            write_assignment_file(assig, outfile, n)
    elif len(sys.argv) >= 3:
        rle_file = sys.argv[2]
        sol = analyze_rle_missing_assignments(rle_file, n)
        if sol:
            assig = extract_assignment(sol, n)
            outfile = f"ring_assignment_n{n}_from_rle.txt"
            write_assignment_file(assig, outfile, n)
