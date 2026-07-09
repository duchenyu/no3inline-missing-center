#!/usr/bin/env python3
"""
Deep structural analysis of the direction hypergraph H_n^dir.

Questions addressed:
1. Co-degree distribution: for pairs of directions, how many hyperedges contain both?
2. Hyperedge type classification: D (involves (1,1)), L (low-slope only), S (high-slope)
3. "Safe set" analysis: how many directions have danger = 0?
4. Structural bound: what's the maximum independent set size we can guarantee?
"""
import os, math, random, json
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|"
VAL = {c: i for i, c in enumerate(ALPH)}
TARGETS = [12, 16, 20, 24, 28, 32]

# Directions we classify as "heavy" based on empirical data
HEAVY_DIRS = {(1,1), (1,-1), (3,1), (1,3), (3,-1), (1,-3)}

def build_orbits(n):
    """All R180-orbits, each as (dir, (p, q))."""
    seen = set(); orbits = []
    for r in range(n):
        for c in range(n):
            p = (r, c)
            if p in seen:
                continue
            q = (n - 1 - p[0], n - 1 - p[1])
            seen.add(p); seen.add(q)
            a = 2 * p[0] - (n - 1); b = 2 * p[1] - (n - 1)
            g = math.gcd(a, b) or 1
            a, b = a // g, b // g
            if a < 0 or (a == 0 and b < 0):
                a, b = -a, -b
            orbits.append(((a,b), (p, q)))
    return orbits

# DEPRECATED: this script's original collinear3 iterated only range(3) over the
# 6-point list, i.e. it checked only (p_i,q_i,p_j) and ignored (q_j,p_k,q_k).
# That bug made every detected "hyperedge" a center-line antipodal collinearity,
# which is why it reported ">=89% D6 dominance" (see d6_dominance_correction.md).
# The fixed version below checks ALL C(6,3)=20 triples, but NOTE: even so the
# "loose" hyperedge (any 3 of 6 points collinear) over-counts bystander triples.
# The correct constraint notion is the GENUINE hyperedge (3 distinct orbits each
# contributing a point to a common grid line) -- computed in
# d6_dominance_rigorous.py. Prefer that.
def collinear3(pts):
    n = len(pts)
    for a in range(n):
        x1, y1 = pts[a]
        for b in range(a + 1, n):
            x2, y2 = pts[b]
            for c in range(b + 1, n):
                x3, y3 = pts[c]
                if (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1):
                    return True
    return False

def analyze_structure(n):
    """Deep structural analysis of H_n^dir."""
    orbits = build_orbits(n)
    m = len(orbits)
    pts_of = [o[1] for o in orbits]
    dirs_of = [o[0] for o in orbits]
    
    # 1. Compute danger (per direction) and co-degree (per pair)
    danger = Counter()
    codegree = Counter()  # (i,j) -> count of k such that {i,j,k} is hyperedge
    
    hypertypes = {"D": 0, "L": 0, "S": 0}  # D=heavy-diag involved, L=low only, S=high
    
    for i in range(m):
        p_i = pts_of[i]
        for j in range(i + 1, m):
            p_j = pts_of[j]
            pts_ij = p_i + p_j
            pair_bad = 0
            for k in range(j + 1, m):
                six = pts_ij + pts_of[k]
                if collinear3(six):
                    pair_bad += 1
                    danger[dirs_of[i]] += 1
                    danger[dirs_of[j]] += 1
                    danger[dirs_of[k]] += 1
                    # Classify
                    dset = {dirs_of[i], dirs_of[j], dirs_of[k]}
                    if dset & HEAVY_DIRS:
                        hypertypes["D"] += 1
                    elif all((abs(d[0]) <= 3 and abs(d[1]) <= 3) for d in dset):
                        hypertypes["L"] += 1
                    else:
                        hypertypes["S"] += 1
            if pair_bad > 0:
                codegree[(i,j)] = pair_bad
    
    # 2. Count safe directions (danger = 0)
    safe = [d for d, c in danger.items() if c == 0]
    safe_set_size = len(safe)
    
    # 3. Heavy direction analysis
    heavy_present = {d: danger.get(d, 0) for d in HEAVY_DIRS & set(danger.keys())}
    
    # 4. Danger distribution (deciles)
    if danger:
        degs = sorted(danger.values())
        deciles = {
            "min": degs[0],
            "p25": degs[len(degs)//4],
            "p50": degs[len(degs)//2],
            "p75": degs[3*len(degs)//4],
            "p90": degs[9*len(degs)//10],
            "max": degs[-1],
            "mean": sum(degs)/len(degs),
        }
    else:
        deciles = {}
    
    # 5. Codegree distribution
    cg_vals = list(codegree.values())
    cg_stats = {}
    if cg_vals:
        cg_stats = {
            "min": min(cg_vals),
            "max": max(cg_vals),
            "mean": sum(cg_vals)/len(cg_vals),
            "nonzero_pairs": len(cg_vals),
            "total_pairs": m*(m-1)//2,
            "pair_density": len(cg_vals) / (m*(m-1)//2),
        }
    
    # 6. Barely-constrained question: what's max independent set size
    #    if we only look at the top-K dangerous directions?
    # We can't compute α exactly (NP-hard), but we can estimate
    # by finding how many safe directions exist
    
    return {
        "n": n,
        "m": m,
        "total_hyperedges": sum(danger.values()) // 3,
        "hypertypes": hypertypes,
        "safe_directions": safe_set_size,
        "safe_fraction": safe_set_size / m if m > 0 else 0,
        "heavy_danger": {str(k): v for k, v in heavy_present.items()},
        "danger_distribution": deciles,
        "codegree": cg_stats,
    }


def main():
    results = []
    for n in TARGETS:
        print(f"\n{'='*60}")
        print(f"n={n}")
        r = analyze_structure(n)
        results.append(r)
        
        print(f"  Total hyperedges: {r['total_hyperedges']}")
        print(f"  Types: D={r['hypertypes']['D']} L={r['hypertypes']['L']} S={r['hypertypes']['S']}")
        print(f"  D-fraction of total: {r['hypertypes']['D']/r['total_hyperedges']*100:.1f}%")
        print(f"  Safe directions: {r['safe_directions']}/{r['m']} ({r['safe_fraction']*100:.1f}%)")
        print(f"  Heavy dirs danger: {r['heavy_danger']}")
        dd = r['danger_distribution']
        print(f"  Danger: p50={dd.get('p50')} p90={dd.get('p90')} mean={dd.get('mean'):.0f} max={dd.get('max')}")
        cg = r['codegree']
        print(f"  Codegree: nonzero_pairs={cg.get('nonzero_pairs')} max={cg.get('max')} mean={cg.get('mean'):.1f}")
        print(f"  Pair density: {cg.get('pair_density', 0)*100:.3f}%")
    
    # Summary table
    print(f"\n{'='*80}")
    print(f"{'n':>4}  {'V':>5}  {'|E|':>7}  {'D-type%':>8}  {'Safe%':>7}  {'p50':>5}  {'p90':>5}  {'max':>6}  {'cg%':>7}")
    print("-"*80)
    for r in results:
        dd = r['danger_distribution']
        cg = r['codegree']
        print(f"{r['n']:>4}  {r['m']:>5}  {r['total_hyperedges']:>7}  "
              f"{r['hypertypes']['D']/r['total_hyperedges']*100:>7.1f}  "
              f"{r['safe_fraction']*100:>6.2f}  "
              f"{dd.get('p50','?'):>5}  {dd.get('p90','?'):>5}  {dd.get('max','?'):>6}  "
              f"{cg.get('pair_density',0)*100:>6.3f}")
    
    # Save
    path = os.path.join(HERE, "hypergraph_structure.json")
    with open(path, "w") as f:
        json.dump({"results": results}, f, indent=2, default=str)
    print(f"\n[written] {path}")

if __name__ == "__main__":
    main()
