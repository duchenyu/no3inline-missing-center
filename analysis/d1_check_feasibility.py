#!/usr/bin/env python3
"""
Check whether the rot2 direction-uniqueness constraint ALONE
(ignoring collinearity) is satisfiable at n=31.
If it is, the UNSAT is caused by collinearity.
If not, the matching itself is impossible.
"""
import os, math, random
from collections import defaultdict

def build_cells(m):
    """Enumerate all domain cells and their directions."""
    cells = {}  # (r,c) -> direction
    for r in range(m + 1):  # domain rows
        for c in range(2 * m + 1):  # domain columns
            if r == m and c == m:
                continue  # center cell
            a = r - m
            b = c - m
            g = abs(math.gcd(a, b)) or 1
            a1, b1 = a // g, b // g
            if a1 < 0 or (a1 == 0 and b1 < 0):
                a1, b1 = -a1, -b1
            cells[(r, c)] = (a1, b1)
    return cells

def greedy_matching(m):
    """Greedy bipartite matching for 2-per-row direction uniqueness."""
    cells = build_cells(m)
    
    # Group cells by row
    by_row = defaultdict(list)
    for (r, c), d in cells.items():
        if d == (0, 1):
            continue  # reserved for center row
        by_row[r].append((c, d))
    
    # Center row: must select direction (0,1)
    # Find a cell on center row with direction (0,1)
    center_cells = [(r, c) for (r, c), d in cells.items() if r == m and d == (0, 1)]
    if not center_cells:
        return None  # Should not happen
    
    assignment = {}  # row -> list of directions
    used_dirs = {(0, 1)}  # center row takes (0,1)
    
    # Assign center row
    assignment[m] = [(0, 1)]
    
    # Greedy: for each non-center row, try to find 2 unused directions
    for r in range(m):  # non-center rows
        chosen = []
        for c, d in by_row[r]:
            if d not in used_dirs and len(chosen) < 2:
                chosen.append(d)
                used_dirs.add(d)
        if len(chosen) < 2:
            return None  # Failed: not enough unique directions for this row
        assignment[r] = chosen
    
    return assignment

def backtrack_matching(m, max_attempts=100000):
    """Backtracking search for 2-per-row direction uniqueness matching."""
    cells = build_cells(m)
    directions = {}
    for (r, c), d in cells.items():
        if d == (0, 1):
            continue
        directions[(r, c)] = d
    
    # Shuffle for diversity
    rows = list(range(m))
    
    best_found = 0
    attempt = 0
    
    # Simple DFS with pruning
    def dfs(row_idx, assignment, used):
        nonlocal best_found, attempt
        if row_idx == m:
            return assignment  # All rows assigned!
        
        r = rows[row_idx]
        row_cells = [(r, c, d) for (r, c), d in directions.items() if r == r and d == (0, 1)]
        # Actually just get all cells for this row
        row_options = [(c, d) for (rr, c), d in directions.items() if rr == r]
        random.shuffle(row_options)
        
        for i, (c1, d1) in enumerate(row_options):
            if d1 in used:
                continue
            for j, (c2, d2) in enumerate(row_options):
                if j <= i or d2 in used or d1 == d2:
                    continue
                # Try this pair
                assignment[r] = [d1, d2]
                used.add(d1); used.add(d2)
                
                result = dfs(row_idx + 1, assignment, used)
                if result is not None:
                    return result
                
                used.remove(d1); used.remove(d2)
                del assignment[r]
                
                attempt += 1
                if attempt >= max_attempts:
                    return None
        
        return None
    
    for trial in range(10):
        random.shuffle(rows)
        result = dfs(0, {}, {(0, 1)})
        if result is not None:
            return result
    
    return None

def random_search(m, trials=50000):
    """Random search for a valid matching."""
    cells = build_cells(m)
    dirs_by_row = defaultdict(list)
    for (r, c), d in cells.items():
        if d != (0, 1):
            dirs_by_row[r].append(d)
    
    for t in range(trials):
        used = {(0, 1)}
        ok = True
        for r in range(m):
            row_dirs = dirs_by_row[r]
            random.shuffle(row_dirs)
            chosen = []
            for d in row_dirs:
                if d not in used:
                    chosen.append(d)
                    used.add(d)
                    if len(chosen) == 2:
                        break
            if len(chosen) < 2:
                ok = False
                break
        if ok:
            return True
    return False

print("=" * 60)
print("rot2 Direction-Uniqueness Feasibility Check")
print("=" * 60)

for m in [12, 13, 14, 15, 16, 17]:
    result = greedy_matching(m)
    if result:
        print(f"m={m:>3} (n={2*m+1:>3}): GREEDY ✅")
    else:
        # Try random search for harder cases
        rs = random_search(m, 200000)
        print(f"m={m:>3} (n={2*m+1:>3}): GREEDY ❌, RandomSearch={'✅' if rs else '❌'}")
        
        if not rs:
            # Try backtracking
            bt = backtrack_matching(m, 50000)
            print(f"  Backtrack: {'✅ Found!' if bt else '❌ Still not found'}")

# Detailed: show one matching for n=29
print(f"\n{'='*60}")
print("Example matching for n=29 (m=14):")
m = 14
a = greedy_matching(m)
if a:
    row_list = sorted(a.keys())
    for r in row_list:
        dirs = sorted(a[r])
        print(f"  Row {r:>2}: dirs = {dirs}")

print(f"\n{'='*60}")
print("Attempt for n=31 (m=15):")
# Show the first few rows to verify greedy fails
m = 15
cells = build_cells(m)
dirs_by_row = defaultdict(set)
for (r, c), d in cells.items():
    if d != (0, 1):
        dirs_by_row[r].add(d)
for r in sorted(dirs_by_row.keys()):
    if r < m:  # non-center
        print(f"  Row {r:>2}: {len(dirs_by_row[r])} unique directions")
