// Count collinear orbit-triples for n=74 (m=37) under C4 symmetry.
// A C4 orbit is parametrized by (i,j) in [0,m-1]^2. Its 4 grid points on the
// n x n grid (n=2m) are:
//   (i, j), (j, n-1-i), (n-1-i, n-1-j), (n-1-j, i)
// We enumerate the 342 distinct C4 orbits (fundamental domain, excluding the
// degenerate center), then count how many triples of distinct orbits contain a
// collinear triple of grid points (one point from each orbit: 4*4*4 = 64 combos).
#include <bits/stdc++.h>
using namespace std;

int main() {
    const int m = 37, n = 2 * m;
    // fundamental domain: (i,j) with 0<=i,j<m, not a rotated copy, not center
    vector<array<int,2>> orb;
    for (int i = 0; i < m; i++)
        for (int j = 0; j < m; j++) {
            if (i == m-1-i && j == m-1-j) continue; // center (degenerate)
            // canonical representative = lexicographically smallest under C4
            int a = i, b = j;
            auto rot = [&](int x, int y) { return array<int,2>{m-1-y, x}; };
            array<int,2> r = rot(a,b); if (r < array<int,2>{a,b}) { a=r[0]; b=r[1]; }
            r = rot(a,b);            if (r < array<int,2>{a,b}) { a=r[0]; b=r[1]; }
            r = rot(a,b);            if (r < array<int,2>{a,b}) { a=r[0]; b=r[1]; }
            if (a == i && b == j) orb.push_back({i,j});
        }
    int K = orb.size();
    printf("distinct C4 orbits (m=%d): %d\n", m, K);
    printf("C(K,3) = %.3e\n", (double)K*(K-1)*(K-2)/6.0);

    // precompute 4 points per orbit
    vector<array<array<int,2>,4>> pts(K);
    for (int o = 0; o < K; o++) {
        int i = orb[o][0], j = orb[o][1];
        pts[o][0] = {i, j};
        pts[o][1] = {j, n-1-i};
        pts[o][2] = {n-1-i, n-1-j};
        pts[o][3] = {n-1-j, i};
    }

    long long total = 0, collinear = 0;
    auto bad = [&](int A, int B, int C) {
        // check all 4*4*4 choices of one point from each orbit
        for (int a = 0; a < 4; a++)
            for (int b = 0; b < 4; b++)
                for (int c = 0; c < 4; c++) {
                    int x1=pts[A][a][0], y1=pts[A][a][1];
                    int x2=pts[B][b][0], y2=pts[B][b][1];
                    int x3=pts[C][c][0], y3=pts[C][c][1];
                    if ((long long)(x2-x1)*(y3-y1) == (long long)(x3-x1)*(y2-y1))
                        return true;
                }
        return false;
    };

    for (int A = 0; A < K; A++)
        for (int B = A+1; B < K; B++)
            for (int C = B+1; C < K; C++) {
                total++;
                if (bad(A,B,C)) collinear++;
            }
    printf("total orbit-triples checked: %lld\n", total);
    printf("collinear orbit-triples: %lld (%.4f%%)\n", collinear, 100.0*collinear/total);
    long long per_graph = (long long)37*36*35/6;
    printf("C(37,3) = %lld ; expected collinear in a random 2-regular graph = %.1f\n",
           per_graph, per_graph * (double)collinear/total);
    return 0;
}
