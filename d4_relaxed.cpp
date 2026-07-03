// ============================================================
// No-Three-In-Line - Direction 4: No row constraint
// Place 2n points on n x n grid, any arrangement, no 3 collinear
// Cell-by-cell backtracking with forbid_accum
// ============================================================
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <chrono>
using namespace std;

int N;
int TARGET;
int pts_r[512], pts_c[512];  // placed points
int n_pts = 0;
int col_cnt[64];
uint64_t forbid[64];           // per-row forbidden masks
int64_t cx_times2, cy_times2;
int dist_lookup[4096];

long long total_sol = 0;
long long missing_sol = 0;

inline int get_dist(int c, int r) {
    return dist_lookup[r * N + c];
}

// Add blocking from cross-row pair (r1,c1)-(r2,c2) [r1!=r2]
static inline void add_block(int r1, int c1, int r2, int c2) {
    if (r1 == r2) return;  // same row, horizontal line — no blocking
    if (r1 > r2) { int t=r1; r1=r2; r2=t; t=c1; c1=c2; c2=t; }
    int dr = r2 - r1;
    int dc = c2 - c1;
    for (int tr = r2 + 1; tr < N; tr++) {
        int num = dc * (tr - r1);
        if (num % dr == 0) {
            int col = c1 + num / dr;
            if (col >= 0 && col < N)
                forbid[tr] |= (1ULL << col);
        }
    }
}

void backtrack(int cell_idx) {
    if (n_pts == TARGET) {
        // Found a solution — check center
        total_sol++;
        int dc[4096] = {0};
        bool has3 = false;
        for (int i = 0; i < n_pts; i++) {
            int d = get_dist(pts_c[i], pts_r[i]);
            if (++dc[d] >= 3) { has3 = true; break; }
        }
        if (!has3) missing_sol++;
        return;
    }
    
    if (cell_idx >= N * N) return;
    
    // Prune: not enough remaining cells
    int remaining = N * N - cell_idx;
    if (n_pts + remaining < TARGET) return;
    
    int r = cell_idx / N;
    int c = cell_idx % N;
    
    // ========== Option 1: Skip this cell ==========
    backtrack(cell_idx + 1);
    
    // ========== Option 2: Place point here ==========
    if (!(forbid[r] & (1ULL << c)) && col_cnt[c] < 2) {
        // Save state
        uint64_t saved[64];
        memcpy(saved, forbid, sizeof(forbid));
        
        // Place point
        pts_r[n_pts] = r;
        pts_c[n_pts] = c;
        n_pts++;
        col_cnt[c]++;
        
        // Update forbid with pairs formed by this point and all existing points
        for (int i = 0; i < n_pts - 1; i++)
            add_block(pts_r[i], pts_c[i], r, c);
        
        backtrack(cell_idx + 1);
        
        // Restore
        n_pts--;
        col_cnt[c]--;
        memcpy(forbid, saved, sizeof(forbid));
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Usage: d4_relaxed.exe <n>\n");
        printf("  Enumerates all No-Three-In-Line solutions with 2n points, no row constraint\n");
        return 1;
    }
    N = atoi(argv[1]);
    TARGET = 2 * N;

    if (N % 2 == 0) { cx_times2 = N - 1; cy_times2 = N - 1; }
    else { cx_times2 = 2 * (N / 2); cy_times2 = cx_times2; }

    for (int r = 0; r < N; r++)
        for (int c = 0; c < N; c++) {
            int64_t dx = 2LL * c - cx_times2;
            int64_t dy = 2LL * r - cy_times2;
            dist_lookup[r * N + c] = (int)(dx * dx + dy * dy);
        }

    printf("========================================\n");
    printf(" No-Three-In-Line D4 (no row constraint)\n");
    printf(" n=%d  2n=%d  grid=%dx%d\n", N, TARGET, N, N);
    printf(" Total cells: %d\n", N * N);
    printf("========================================\n");

    auto t0 = chrono::high_resolution_clock::now();
    backtrack(0);
    auto t1 = chrono::high_resolution_clock::now();
    double sec = chrono::duration<double>(t1 - t0).count();

    printf("\n=========== RESULTS ===========\n");
    printf("  Total solutions : %lld\n", total_sol);
    printf("  With center     : %lld\n", total_sol - missing_sol);
    printf("  Missing center  : %lld\n", missing_sol);
    printf("  Time elapsed    : %.3f s\n", sec);
    printf("===============================\n");

    return 0;
}
