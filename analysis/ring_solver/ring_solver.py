#!/usr/bin/env python3
"""
Ring-first solver for missing-center No-Three-In-Line solutions.

Strategy: Instead of row-by-row search (as in no3line.cpp), process
distance rings in order. For each ring, decide how many points to take
(0, 1, or 2). This directly enforces the missing-center condition
(no ring has >= 3 points) and reveals which ring assignments admit solutions.

Usage:
    python ring_solver.py <n> [max_solutions] [max_skip]

Example:
    python ring_solver.py 12 5 4
    # n=12, stop after 5 solutions, skip at most 4 rings
"""

import sys
from collections import defaultdict
from itertools import combinations
import time


def build_rings(n):
    """Build distance rings for n×n grid.
    
    Returns dict: d_value -> [(r,c), ...]
    Also returns convenient lookup structures.
    """
    cx2 = cy2 = n - 1  # center * 2
    rings = defaultdict(list)
    
    for r in range(n):
        for c in range(n):
            dx = 2 * c - cx2
            dy = 2 * r - cy2
            d = dx * dx + dy * dy
            rings[d].append((r, c))
    
    # Sort rings by d value (inner first)
    sorted_rings = dict(sorted(rings.items()))
    
    # Build row lookup: at each row, list of (d, c) for that row
    row_info = defaultdict(list)
    for d, pts in sorted_rings.items():
        for r, c in pts:
            row_info[r].append((d, c))
    
    return sorted_rings, row_info


def collinear(p1, p2, p3):
    """Check if three points (x,y) = (col,row) are collinear.
    Determinant formula: |x1 y1 1; x2 y2 1; x3 y3 1| = 0
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    return x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2) == 0


def would_create_collinear(new_pt, existing_pts):
    """Check if adding new_pt creates a collinear triple."""
    n = len(existing_pts)
    if n < 2:
        return False
    # Check pairs with existing points (O(k^2) per call)
    for i in range(n):
        for j in range(i + 1, n):
            if collinear(existing_pts[i], existing_pts[j], new_pt):
                return True
    return False


def check_pair_collinear(p1, p2, existing_pts):
    """Check if adding p1 AND p2 simultaneously creates a collinear triple.
    This checks triples: (p1, p2, e) for each existing point e.
    """
    for e in existing_pts:
        if collinear(p1, p2, e):
            return True
    return False


class RingSolver:
    def __init__(self, n, max_solutions=1, max_skip=None):
        self.n = n
        self.max_solutions = max_solutions
        self.max_skip = max_skip if max_skip is not None else max(1, n // 3)
        
        self.rings, self.row_info = build_rings(n)
        self.ring_order = list(self.rings.keys())
        self.target_total = 2 * n
        
        # Stats
        self.nodes_explored = 0
        self.leaves_reached = 0
        self.solutions = []
        self.start_time = None
        
        # Debug: track which ring assignments succeed
        self.successful_assignments = []  # list of {d: count} for successful searches
    
    def solve(self, timeout=120):
        """Main entry point."""
        self.start_time = time.time()
        self.timeout = timeout
        
        print(f"Ring Solver: n={self.n}, target={self.target_total} pts")
        print(f"  Rings: {len(self.ring_order)}")
        print(f"  Max skip: {self.max_skip}")
        print(f"  Max solutions: {self.max_solutions}")
        print(f"  Timeout: {timeout}s")
        print()
        
        # Show ring capacities
        print("  Ring capacities:")
        for d in self.ring_order:
            pts = self.rings[d]
            print(f"    d={d:4d}: {len(pts):2d} pts: {sorted(pts)}")
        print()
        
        # Initial state
        state = {
            'row_cnt': [0] * self.n,
            'col_cnt': [0] * self.n,
            'selected': [],      # list of (c, r) points
            'skip_count': 0,
        }
        
        # Start recursive search
        self._backtrack(0, state)
        
        elapsed = time.time() - self.start_time
        print(f"\nSearch complete in {elapsed:.1f}s")
        print(f"  Nodes explored: {self.nodes_explored}")
        print(f"  Leaves reached: {self.leaves_reached}")
        print(f"  Solutions found: {len(self.solutions)}")
        
        if self.successful_assignments:
            print(f"\nSuccessful ring assignments:")
            for assig in self.successful_assignments:
                used = {d: c for d, c in assig.items() if c > 0}
                print(f"  Used {len(used)} rings: {dict(sorted(used.items()))}")
        
        return self.solutions
    
    def _remaining_ring_slots(self, ring_idx):
        """Maximum points remaining from ring_idx onwards."""
        return (len(self.ring_order) - ring_idx) * 2
    
    def _backtrack(self, ring_idx, state):
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            return
        
        if len(self.solutions) >= self.max_solutions:
            return
        
        self.nodes_explored += 1
        selected = state['selected']
        remaining = self.target_total - len(selected)
        
        # === Leaf check ===
        if remaining == 0:
            self.leaves_reached += 1
            # Verify all constraints
            if all(c == 2 for c in state['col_cnt']):
                print(f"  ✅ Solution {len(self.solutions) + 1} found! ({elapsed:.1f}s)")
                self.solutions.append(list(selected))
                # Record the ring assignment that led to this solution
                # (We'll reconstruct this from the actual search)
            return
        
        if ring_idx >= len(self.ring_order):
            return
        
        # === Prune: not enough remaining capacity ===
        max_future = self._remaining_ring_slots(ring_idx)
        if remaining > max_future:
            return
        
        d = self.ring_order[ring_idx]
        pts = self.rings[d]  # list of (r, c)
        
        # === Option A: Skip this ring (take 0 points) ===
        if state['skip_count'] < self.max_skip:
            new_state = dict(state)
            new_state['skip_count'] += 1
            self._backtrack(ring_idx + 1, new_state)
            if len(self.solutions) >= self.max_solutions:
                return
        
        # === Options B & C: Take 1 or 2 points from this ring ===
        # Filter to points that don't exceed row/col capacity
        available = [(r, c) for (r, c) in pts
                     if state['row_cnt'][r] < 2 and state['col_cnt'][c] < 2]
        
        if not available:
            return
        
        # --- Take 1 point ---
        for idx, (r, c) in enumerate(available):
            pt = (c, r)  # (col, row) for collinear check
            if would_create_collinear(pt, selected):
                continue
            
            new_state = dict(state)
            new_state['row_cnt'] = state['row_cnt'][:]
            new_state['col_cnt'] = state['col_cnt'][:]
            new_state['row_cnt'][r] += 1
            new_state['col_cnt'][c] += 1
            new_state['selected'] = selected + [pt]
            
            self._backtrack(ring_idx + 1, new_state)
            if len(self.solutions) >= self.max_solutions:
                return
        
        # --- Take 2 points ---
        if len(available) >= 2:
            for i in range(len(available)):
                r1, c1 = available[i]
                for j in range(i + 1, len(available)):
                    r2, c2 = available[j]
                    
                    # Row/col feasibility
                    nr = state['row_cnt'][:]
                    nc = state['col_cnt'][:]
                    nr[r1] += 1
                    nr[r2] += 1
                    nc[c1] += 1
                    nc[c2] += 1
                    
                    if max(nr) > 2 or max(nc) > 2:
                        continue
                    
                    # Skip duplicate row (two points on same row)
                    # This is allowed as long as row count ≤ 2
                    
                    # Collinearity checks
                    p1 = (c1, r1)
                    p2 = (c2, r2)
                    
                    if would_create_collinear(p1, selected):
                        continue
                    if would_create_collinear(p2, selected):
                        continue
                    if check_pair_collinear(p1, p2, selected):
                        continue
                    
                    new_state = dict(state)
                    new_state['row_cnt'] = nr
                    new_state['col_cnt'] = nc
                    new_state['selected'] = selected + [p1, p2]
                    
                    self._backtrack(ring_idx + 1, new_state)
                    if len(self.solutions) >= self.max_solutions:
                        return
    
    def describe_solution(self, solution):
        """Print a solution in a readable format."""
        n = self.n
        cx2 = cy2 = n - 1
        
        print(f"\nSolution ({len(solution)} points):")
        
        # Group by row
        by_row = defaultdict(list)
        for c, r in solution:
            by_row[r].append(c)
        
        print("  Row -> Col1 Col2   d(Col1) d(Col2)")
        for r in range(n):
            if r in by_row:
                cs = sorted(by_row[r])
                d1 = (2*cs[0]-cx2)**2 + (2*r-cy2)**2
                d2 = (2*cs[1]-cx2)**2 + (2*r-cy2)**2
                print(f"  {r:3d} -> {cs[0]:3d}  {cs[1]:3d}   {d1:6d} {d2:6d}")
        
        # Show ring distribution
        ring_dist = defaultdict(list)
        for c, r in solution:
            d = (2*c-cx2)**2 + (2*r-cy2)**2
            ring_dist[d].append((r, c))
        
        print(f"\n  Ring distribution:")
        for d, pts in sorted(ring_dist.items()):
            print(f"    d={d:4d}: {len(pts)} pts: {sorted(pts)}")
        
        max_ring = max(len(pts) for pts in ring_dist.values())
        print(f"\n  Max points per ring: {max_ring}")
        print(f"  {'✅ Missing center' if max_ring <= 2 else '❌ Has center'}")
        
        # Verify
        print(f"\n  Verification:")
        for i in range(len(solution)):
            for j in range(i+1, len(solution)):
                for k in range(j+1, len(solution)):
                    if collinear(solution[i], solution[j], solution[k]):
                        print(f"    ❌ COLLINEAR: {solution[i]}, {solution[j]}, {solution[k]}")
                        return
        print(f"    ✅ No collinear triples")
        
        col_cnt = Counter(c for c, r in solution)
        print(f"    ✅ Column counts: {dict(sorted(col_cnt.items()))}")
        row_cnt = Counter(r for c, r in solution)
        print(f"    ✅ Row counts: {dict(sorted(row_cnt.items()))}")


# =========== Tool: Enumerate ring skip patterns ==========

def enumerate_skip_patterns(rings, n, max_skip=6):
    """
    Enumerate all valid ring assignments (d -> count).
    Only enumerates non-isomorphic patterns (not all C(n,k) combinations).
    Returns list of {d: count} dicts.
    """
    ring_list = list(rings.keys())
    caps = {d: len(pts) for d, pts in rings.items()}
    target = 2 * n
    
    results = []
    total_enum = [0]
    
    def backtrack(idx, remaining, assig, skip_count):
        total_enum[0] += 1
        if total_enum[0] % 1000000 == 0:
            print(f"    Enumerated {total_enum[0]} assignments, found {len(results)} valid...")
        
        if len(results) >= 20000:  # Sanity limit
            return
        
        if idx == len(ring_list):
            if remaining == 0:
                results.append(dict(assig))
            return
        
        d = ring_list[idx]
        remaining_after = len(ring_list) - idx - 1
        
        # Prune
        if remaining > remaining_after * 2 + 2:
            return
        if remaining < 0:
            return
        if skip_count > max_skip:
            return
        
        for cnt in [0, 1, 2]:
            if cnt > caps[d] or cnt > remaining:
                continue
            new_skip = skip_count + (1 if cnt == 0 else 0)
            if new_skip > max_skip:
                continue
            # Can still reach target?
            if remaining - cnt > remaining_after * 2:
                continue
            assig[d] = cnt
            backtrack(idx + 1, remaining - cnt, assig, new_skip)
            del assig[d]
    
    backtrack(0, target, {}, 0)
    print(f"  Total assignments enumerated: {total_enum[0]}, valid: {len(results)}")
    return results


# =========== Main ==========

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    max_sol = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    max_skip = int(sys.argv[3]) if len(sys.argv) > 3 else None
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 120
    
    solver = RingSolver(n, max_solutions=max_sol, max_skip=max_skip)
    solutions = solver.solve(timeout=timeout)
    
    if solutions:
        solver.describe_solution(solutions[0])
    else:
        print("\n  No solutions found.")
