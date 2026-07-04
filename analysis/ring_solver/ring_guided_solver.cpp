/**
 * ring_guided_solver.cpp
 * 
 * Hybrid solver: accepts a pre-specified distance-ring assignment
 * (which rings get 0/1/2 points), then uses row-by-row forbid_accum
 * search to find a valid placement respecting that assignment.
 *
 * Usage:
 *   ring_guided_solver <n> <mode> [ring_file]
 *
 * mode 0: enumerate ALL ring assignments with pruning, try each
 * mode 1: read a single ring assignment from file/stdin, try it
 *
 * Ring file format (mode 1):
 *   Line 1: "n <N>"
 *   Each subsequent line: "<d> <count>"  where count = 0, 1, or 2
 *
 * Compile: g++ -O3 -march=native -std=c++17 -static ring_guided_solver.cpp -o ring_guided_solver
 */

#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <vector>
#include <chrono>
#include <thread>
#include <atomic>
#include <mutex>
#include <unordered_map>
#include <string>
#include <set>
#include <map>
using namespace std;

int N;
int MODE;
int64_t cx2, cy2;

// ===== Distance ring system =====
struct RingInfo {
    int d;                    // squared distance
    vector<pair<int,int>> pts; // (r,c) points on this ring
    int capacity;             // = len(pts)
};

vector<RingInfo> rings_by_d;  // sorted by d
unordered_map<int,int> d_to_idx;  // d -> index in rings_by_d

// Precompute distance for each grid cell
vector<int> dist_lookup;  // [r*N + c]

int get_dist(int c, int r) {
    return dist_lookup[r * N + c];
}

// Column ordering within each ring for fast lookup
// ring_cols_at_row[ring_idx][r] = bitmask of columns in this ring at row r
vector<vector<uint64_t>> ring_cols_at_row;

void build_rings() {
    cx2 = cy2 = N - 1;
    dist_lookup.resize(N * N);
    
    unordered_map<int, vector<pair<int,int>>> ring_map;
    
    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            int64_t dx = 2LL * c - cx2;
            int64_t dy = 2LL * r - cy2;
            int d = (int)(dx * dx + dy * dy);
            dist_lookup[r * N + c] = d;
            ring_map[d].push_back({r, c});
        }
    }
    
    // Sort by d
    vector<int> ds;
    for (auto &kv : ring_map)
        ds.push_back(kv.first);
    sort(ds.begin(), ds.end());
    
    for (int d : ds) {
        RingInfo ri;
        ri.d = d;
        ri.pts = ring_map[d];
        ri.capacity = (int)ri.pts.size();
        d_to_idx[d] = (int)rings_by_d.size();
        rings_by_d.push_back(ri);
    }
    
    // Build ring_cols_at_row
    ring_cols_at_row.resize(rings_by_d.size());
    for (int ri = 0; ri < (int)rings_by_d.size(); ri++) {
        ring_cols_at_row[ri].resize(N, 0);
        for (auto &pt : rings_by_d[ri].pts) {
            int r = pt.first, c = pt.second;
            ring_cols_at_row[ri][r] |= (1ULL << c);
        }
    }
}

// ===== Ring assignment =====
// assignment[d_idx] = target count (0, 1, or 2)
vector<int> ring_assignment;  // index by d_idx

// Remaining capacity per ring during search
struct RingTracker {
    vector<int> remaining;  // remaining points to place in each ring
    int total_remaining;     // total points remaining to place
    
    void init(const vector<int> &assig) {
        remaining = assig;
        total_remaining = 0;
        for (int v : remaining) total_remaining += v;
    }
    
    bool can_place(int d_idx) const {
        return remaining[d_idx] > 0;
    }
    
    void place(int d_idx) {
        remaining[d_idx]--;
        total_remaining--;
    }
    
    void unplace(int d_idx) {
        remaining[d_idx]++;
        total_remaining++;
    }
};

// ===== Collinearity accumulator (same as no3line.cpp) =====
static inline void add_block(uint64_t *forbid, int r1, int c1, int r2, int c2) {
    int dr = r2 - r1;
    int dc = c2 - c1;
    if (dr == 0) return; // same row points never cause collinearity (only 2 per row)
    for (int tr = r2 + 1; tr < N; tr++) {
        int num = dc * (tr - r1);
        if (num % dr == 0) {
            int col = c1 + num / dr;
            if (col >= 0 && col < N)
                forbid[tr] |= (1ULL << col);
        }
    }
}

static inline void update_block(uint64_t *forbid, const int row_cols[][2], int new_row) {
    int c1 = row_cols[new_row][0];
    int c2 = row_cols[new_row][1];
    for (int r = 0; r < new_row; r++) {
        int rc1 = row_cols[r][0];
        int rc2 = row_cols[r][1];
        add_block(forbid, r, rc1, new_row, c1);
        add_block(forbid, r, rc2, new_row, c1);
        add_block(forbid, r, rc1, new_row, c2);
        add_block(forbid, r, rc2, new_row, c2);
    }
}

// ===== Search state =====
struct SearchState {
    int row_cols[32][2];
    int col_counts[32];
    uint64_t forbid[32];
    RingTracker ring_tracker;
    long long local_solutions;
};

// ===== Mode 1: Search with a specific ring assignment =====
void bt_search(SearchState &s, int row, long long max_solutions,
               const vector<vector<uint64_t>> &row_ring_cols) {
    if ((long long)s.local_solutions >= max_solutions)
        return;
    
    if (row == N) {
        // Check all columns used exactly twice
        for (int c = 0; c < N; c++)
            if (s.col_counts[c] != 2) return;
        // All constraints satisfied
        s.local_solutions++;
        return;
    }
    
    // Precompute available columns for this row
    // A column is available if it belongs to a ring with remaining capacity
    // AND is not in forbid[row]
    // AND has col_count < 2
    
    uint64_t forbid_mask = s.forbid[row];
    uint64_t avail_mask = 0;
    for (int ri = 0; ri < (int)rings_by_d.size(); ri++) {
        if (s.ring_tracker.remaining[ri] > 0) {
            avail_mask |= ring_cols_at_row[ri][row];
        }
    }
    
    // Remove forbidden columns and columns already full
    avail_mask &= ~forbid_mask;
    for (int c = 0; c < N; c++) {
        if (s.col_counts[c] >= 2)
            avail_mask &= ~(1ULL << c);
    }
    
    // Extract available column indices
    vector<int> avail_cols;
    for (int c = 0; c < N; c++)
        if (avail_mask & (1ULL << c))
            avail_cols.push_back(c);
    
    int na = (int)avail_cols.size();
    
    // Try all valid column pairs
    for (int i = 0; i < na; i++) {
        int c1 = avail_cols[i];
        int d1 = get_dist(c1, row);
        int ri1 = d_to_idx[d1];
        
        if (s.ring_tracker.remaining[ri1] <= 0) continue;
        
        // Temporarily place c1
        s.ring_tracker.place(ri1);
        s.col_counts[c1]++;
        
        uint64_t saved_forbid[32];
        memcpy(saved_forbid, s.forbid, sizeof(saved_forbid));
        
        for (int j = i + 1; j < na; j++) {
            int c2 = avail_cols[j];
            int d2 = get_dist(c2, row);
            int ri2 = d_to_idx[d2];
            
            if (s.ring_tracker.remaining[ri2] <= 0) continue;
            
            // Can't have both points on same row being the same column
            if (c1 == c2) continue;
            
            // Check row/col constraints
            if (s.col_counts[c2] >= 2) continue;
            
            // Reserve c2
            s.ring_tracker.place(ri2);
            s.col_counts[c2]++;
            
            // Check forbid for c1 and c2
            // (c2 was already checked against existing forbid, but we also need
            //  to check the line through c1-c2 against future rows)
            
            s.row_cols[row][0] = c1;
            s.row_cols[row][1] = c2;
            
            // Update forbid matrix (excluding this row's own c1-c2 pair)
            memcpy(s.forbid, saved_forbid, sizeof(saved_forbid));
            update_block(s.forbid, s.row_cols, row);
            
            bt_search(s, row + 1, max_solutions, row_ring_cols);
            
            if ((long long)s.local_solutions >= max_solutions) {
                s.col_counts[c2]--;
                s.ring_tracker.unplace(ri2);
                s.col_counts[c1]--;
                s.ring_tracker.unplace(ri1);
                return;
            }
            
            s.col_counts[c2]--;
            s.ring_tracker.unplace(ri2);
        }
        
        memcpy(s.forbid, saved_forbid, sizeof(saved_forbid));
        s.col_counts[c1]--;
        s.ring_tracker.unplace(ri1);
    }
}

// ===== Parse ring assignment from text =====
bool parse_ring_assignment(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) return false;
    
    ring_assignment.assign(rings_by_d.size(), 0);
    
    char line[256];
    int total = 0;
    while (fgets(line, sizeof(line), f)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        int d, cnt;
        if (sscanf(line, "%d %d", &d, &cnt) == 2) {
            if (d_to_idx.find(d) != d_to_idx.end()) {
                int idx = d_to_idx[d];
                ring_assignment[idx] = cnt;
                total += cnt;
            }
        }
    }
    fclose(f);
    
    return total == 2 * N;
}

// ===== Derive ring assignment from a known solution =====
void derive_assignment_from(const int row_cols[][2], int n) {
    ring_assignment.assign(rings_by_d.size(), 0);
    for (int r = 0; r < n; r++) {
        int d1 = get_dist(row_cols[r][0], r);
        int d2 = get_dist(row_cols[r][1], r);
        ring_assignment[d_to_idx[d1]]++;
        ring_assignment[d_to_idx[d2]]++;
    }
}

// ===== Mode 0: Enumerate assignments (with max_skip pruning) =====
// This is the analytical mode - enumerate all valid ring assignments
// and count how many have valid placements

atomic<long long> total_enumerated(0);
atomic<long long> feasible_assignments(0);
mutex print_mutex;
int MAX_SKIP;

// ...mode 0 enumeration code...

// ===== Utility: Print ring assignment =====
void print_assignment(const vector<int> &assig) {
    printf("Ring assignment:\n");
    int total = 0;
    for (int ri = 0; ri < (int)rings_by_d.size(); ri++) {
        if (assig[ri] > 0) {
            printf("  d=%4d: %d pts (%d avail)\n", rings_by_d[ri].d, assig[ri], rings_by_d[ri].capacity);
            total += assig[ri];
        }
    }
    printf("  Total: %d points (need %d)\n", total, 2 * N);
    
    // Check if valid
    int skipped = 0;
    int used_half = 0;
    int used_full = 0;
    for (int ri = 0; ri < (int)rings_by_d.size(); ri++) {
        if (assig[ri] == 0) skipped++;
        else if (assig[ri] == 1) used_half++;
        else used_full++;
    }
    printf("  Rings: %d skipped, %d × 1pt, %d × 2pt\n", skipped, used_half, used_full);
}

// ===== Try assignment: see if it admits a solution =====
long long try_assignment(const vector<int> &assig, long long max_sol = 1) {
    SearchState s;
    memset(s.col_counts, 0, sizeof(s.col_counts));
    memset(s.forbid, 0, sizeof(s.forbid));
    s.local_solutions = 0;
    s.ring_tracker.init(assig);
    
    bt_search(s, 0, max_sol, ring_cols_at_row);
    
    return s.local_solutions;
}

// ===== Main =====
int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage:\n");
        printf("  %s <n> 0 [max_skip]                      # enumerate all assignments\n", argv[0]);
        printf("  %s <n> 1 <ring_file>                      # try a specific assignment\n", argv[0]);
        printf("  %s <n> 2 <rle_file>                       # derive from RLE solution\n", argv[0]);
        return 1;
    }
    
    N = atoi(argv[1]);
    MODE = atoi(argv[2]);
    
    build_rings();
    
    printf("Distance rings for n=%d (%d rings):\n", N, (int)rings_by_d.size());
    for (auto &ri : rings_by_d) {
        printf("  d=%4d: %d pts\n", ri.d, ri.capacity);
    }
    printf("\n");
    
    if (MODE == 1) {
        // Try a specific ring assignment
        if (argc < 4) {
            printf("Error: mode 1 requires a ring file\n");
            return 1;
        }
        
        if (!parse_ring_assignment(argv[3])) {
            printf("Error: failed to parse ring assignment file\n");
            return 1;
        }
        
        print_assignment(ring_assignment);
        printf("\nSearching for valid placement...\n");
        
        auto t0 = chrono::high_resolution_clock::now();
        long long found = try_assignment(ring_assignment, 1);
        auto t1 = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(t1 - t0).count();
        
        if (found > 0) {
            printf("✅ Found a valid placement! (%.3fs)\n", elapsed);
        } else {
            printf("❌ No valid placement exists for this assignment (%.3fs)\n", elapsed);
        }
    }
    else if (MODE == 2) {
        // Derive from RLE solution and try it
        // Read RLE file, extract solution, compute its ring assignment,
        // then use that assignment to guide search
        if (argc < 4) {
            printf("Error: mode 2 requires an RLE file\n");
            return 1;
        }
        
        const char *rle_file = argv[3];
        
        // Read the RLE file
        FILE *f = fopen(rle_file, "r");
        if (!f) { printf("Error: cannot open %s\n", rle_file); return 1; }
        
        char line[4096];
        fgets(line, sizeof(line), f);  // header
        int n_vals;
        // Format: "n <RLE>"
        // We need to decode RLE to get solution
        fclose(f);
        
        printf("RLE parsing not yet implemented in this mode. Use analyze_rle.py instead.\n");
        return 1;
    }
    
    return 0;
}
