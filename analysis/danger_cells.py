"""计算 C4 对称下每个基本域单元格的 danger score（包含该格的共线三元组数）。
输出排名 + 累计覆盖率，用于指导 seed_initial 预滤波策略。

用法: python danger_cells.py <n> [--top K]
 
C4 基本域: [0,N)×[0,N), N=n/2
完整棋盘: 2N×2N, 每个轨道 4 个旋转态
"""
import sys
import argparse
from collections import defaultdict
import itertools

def c4_orbits(N):
    """返回每个轨道 (r,c) 在完整棋盘的 4 个旋转点。"""
    orbits = {}
    for r in range(N):
        for c in range(N):
            # 4 次 C4 旋转，绕中心 (N-0.5, N-0.5)
            orbits[(r,c)] = [
                (r, c),                                    # rot0
                (c, 2*N-1-r),                              # rot90
                (2*N-1-r, 2*N-1-c),                        # rot180
                (2*N-1-c, r),                              # rot270
            ]
    return orbits

def collinear(p1, p2, p3):
    """三点共线判别（整数叉积，无误判）。"""
    x1,y1 = p1; x2,y2 = p2; x3,y3 = p3
    return (x2-x1)*(y3-y1) == (y2-y1)*(x3-x1)

def compute_danger(n):
    N = n // 2
    orbits = c4_orbits(N)     # {(r,c): [4 rotated pts]}
    cells = list(orbits.keys())
    danger = defaultdict(int)
    total_triples = 0
    collinear_triples = 0

    for idx, (i, j, k) in enumerate(itertools.combinations(cells, 3)):
        total_triples += 1
        tri_collinear = False
        for ri in range(4):
            p1 = orbits[i][ri]
            for rj in range(4):
                p2 = orbits[j][rj]
                for rk in range(4):
                    p3 = orbits[k][rk]
                    if collinear(p1, p2, p3):
                        tri_collinear = True
                        break
                if tri_collinear: break
            if tri_collinear: break
        if tri_collinear:
            collinear_triples += 1
            danger[i] += 1
            danger[j] += 1
            danger[k] += 1

    # 按危险度降序排列
    ranked = sorted(danger.items(), key=lambda x: -x[1])
    cumulative = 0
    result = []
    for rank, (cell, score) in enumerate(ranked, 1):
        cumulative += score
        result.append((rank, cell, score, cumulative))
    return {
        "n": n, "N": N, "cells": len(cells),
        "total_triples": total_triples,
        "collinear_triples": collinear_triples,
        "ranked": result,
        "total_danger": cumulative,
    }

def main():
    parser = argparse.ArgumentParser(description="C4 danger cell ranking")
    parser.add_argument("n", type=int, help="Grid size (even)")
    parser.add_argument("--top", type=int, default=None, help="Show top K cells")
    args = parser.parse_args()

    if args.n % 2 != 0:
        print("n must be even (C4 symmetry only for even n)", file=sys.stderr)
        sys.exit(1)

    data = compute_danger(args.n)

    print(f"n={data['n']} (N={data['N']}), basic domain: {data['cells']} cells")
    print(f"Orbit triples: {data['total_triples']:,}")
    print(f"Collinear triples: {data['collinear_triples']:,} ({100*data['collinear_triples']/data['total_triples']:.2f}%)")
    print(f"Total danger units: {data['total_danger']:,}")
    print()

    top = args.top or len(data['ranked'])
    top = min(top, len(data['ranked']))
    print(f"{'Rank':>4}  {'Cell (r,c)':>12}  {'Score':>8}  {'Cumul%':>7}")
    print("-"*45)
    for rank, cell, score, cumul in data['ranked'][:top]:
        pct = 100 * cumul / data['total_danger']
        print(f"{rank:>4}  ({cell[0]:>3},{cell[1]:>3})    {score:>8}  {pct:>6.1f}%")

    # 输出 top-K 阈值建议
    if args.top is None:
        print()
        thresholds = [int(data['cells']*p) for p in [0.01, 0.02, 0.05, 0.10, 0.20, 0.30]]
        thresholds = [t for t in thresholds if t > 0]
        print("--- Threshold suggestions ---")
        for t in thresholds:
            t = min(t, len(data['ranked']))
            cumul = data['ranked'][t-1][3]
            pct = 100 * cumul / data['total_danger']
            print(f"  Top {t:>3} cells ({100*t/data['cells']:.0f}% of domain): cover {pct:.1f}% of total danger")

if __name__ == "__main__":
    main()
