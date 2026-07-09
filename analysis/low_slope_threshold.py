#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
低斜率空性：精确阈值扫描 (用 hypergraph_low_slope.py 的*正确*定义)

定义 (见 hypergraph_low_slope.py)：
  超边 = 三个低斜率 C2-轨道 d1,d2,d3, 取点 P_i, 使得
    (1) P1,P2,P3 共线(离心);
    (2) 连线方向 ld = reduced(P2-P1) 也属于低斜率集合 LOW_SET;
    (3) ld != dir_of(P1) (跳过过心线, Lemma 1)。
  此处"空" = 不存在这样的超边。

逐 n 穷举(对所有网格点/轨道) -> 对特定 n 是严格证明(非采样)。
本脚本扫描 n=4..80, 找最先出现超边的 n* (即空性成立的精确上界)。
"""
import math, os
from collections import defaultdict

LOW_DIRS = [(1,0),(0,1),(2,1),(1,2),(2,-1),(1,-2),(3,2),(2,3),(3,-2),(2,-3)]
LOW_SET = set(LOW_DIRS)

def dir_of(pt, n):
    a = 2*pt[0] - (n-1); b = 2*pt[1] - (n-1)
    g = math.gcd(a,b) or 1; a,b = a//g, b//g
    if a < 0 or (a == 0 and b < 0): a,b = -a,-b
    return (a,b)

def r180(pt, n):
    return (n-1-pt[0], n-1-pt[1])

def reduced(dx, dy):
    g = math.gcd(dx, dy) or 1
    return (dx//g, dy//g) if g else (dx, dy)

def check_n(n, stop_at=1):
    dir_pts = defaultdict(set)
    seen = set()
    for r in range(n):
        for c in range(n):
            p = (r,c)
            if p in seen: continue
            q = r180(p,n); seen.add(p); seen.add(q)
            d = dir_of(p,n)
            if d in LOW_SET:
                dir_pts[d].add(p); dir_pts[d].add(q)
    violations = []
    for i, d1 in enumerate(LOW_DIRS):
        pts1 = list(dir_pts.get(d1, []))
        for j in range(i, len(LOW_DIRS)):
            d2 = LOW_DIRS[j]
            pts2 = list(dir_pts.get(d2, []))
            if d1 == d2 and len(pts1) < 4: continue
            for a in range(len(pts1)):
                p1 = pts1[a]
                for b in range(len(pts2)):
                    p2 = pts2[b]
                    if p1 == p2: continue
                    if d1 == d2 and r180(p1,n) == p2: continue
                    dx_dy = (p2[0]-p1[0], p2[1]-p1[1])
                    ld = reduced(*dx_dy)
                    if ld == dir_of(p1, n): continue
                    if ld not in LOW_SET: continue
                    for direction in [1, -1]:
                        for t in range(direction, direction*(n+1), direction):
                            x = p1[0] + t * ld[0]
                            y = p1[1] + t * ld[1]
                            if not (0 <= x < n and 0 <= y < n): break
                            pt3 = (x,y)
                            d3 = dir_of(pt3, n)
                            if d3 in LOW_SET:
                                r1 = r180(p1,n); r2 = r180(p2,n)
                                if pt3 == p1 or pt3 == p2 or pt3 == r1 or pt3 == r2: continue
                                violations.append((d1,d2,d3,p1,p2,pt3,ld))
                                if len(violations) >= stop_at:
                                    return False, violations
    return True, violations

if __name__ == "__main__":
    NMAX = 80
    first_fail = None
    empties = []
    example = None
    for n in range(4, NMAX+1):
        ok, viol = check_n(n, stop_at=1)
        if ok:
            empties.append(n)
        else:
            if first_fail is None:
                first_fail = n
                example = viol[0]
            print(f"  n={n}: ❌ FOUND  example={viol[0]}")
            break
    print(f"\n空性成立的最大 n (扫描至 {NMAX}): ", end="")
    if first_fail is None:
        print(f"全部 n<= {NMAX} 均空 (至少到 {NMAX})")
        print(f"  已验证空: n = {empties[0]}..{empties[-1]} 共 {len(empties)} 个")
    else:
        print(f"n < {first_fail} 全空; 首次出现超边在 n={first_fail}")
        print(f"  空性上界阈值 n* = {first_fail-1}")
        if example:
            print(f"  首个反例: {example}")
    # 写结论
    out = {
        "nmax": NMAX,
        "first_fail": first_fail,
        "empty_count": len(empties),
        "empty_min": empties[0] if empties else None,
        "empty_max": empties[-1] if empties else None,
        "example": list(example) if example else None,
    }
    path = os.path.join(os.path.dirname(__file__), "low_slope_threshold.json")
    with open(path, "w") as f:
        import json; json.dump(out, f, indent=2)
    print(f"\n[written] {path}")
