#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m, k;
    cin >> n >> m >> k;
    vector<tuple<int,int,long long>> edges;
    for (int i = 0; i < m; ++i) {
        int u, v; long long w;
        cin >> u >> v >> w;
        --u; --v;
        edges.push_back({u, v, w});
    }
    vector<long long> c(k);
    vector<vector<long long>> b(k, vector<long long>(n));
    for (int j = 0; j < k; ++j) {
        cin >> c[j];
        for (int i = 0; i < n; ++i) cin >> b[j][i];
    }
    const long long INF = (1LL << 60);
    long long ans = INF;
    for (int mask = 0; mask < (1 << k); ++mask) {
        int N = n + k;
        vector<vector<long long>> g(N, vector<long long>(N, INF));
        for (int i = 0; i < N; ++i) g[i][i] = 0;
        for (auto [u, v, w] : edges) g[u][v] = g[v][u] = min(g[u][v], w);
        for (int j = 0; j < k; ++j) if (mask >> j & 1) {
            for (int i = 0; i < n; ++i) {
                g[i][n + j] = g[n + j][i] = min(g[i][n + j], b[j][i]);
            }
        }
        vector<char> used(N, 0);
        vector<long long> dis(N, INF);
        vector<int> deg(N, 0);
        dis[0] = 0;
        long long cost = 0;
        for (int it = 0; it < n; ++it) {
            int u = -1;
            for (int i = 0; i < N; ++i)
                if (!used[i] && (u == -1 || dis[i] < dis[u])) u = i;
            if (u == -1) break;
            used[u] = 1;
            cost += dis[u];
            for (int v = 0; v < N; ++v)
                if (!used[v] && g[u][v] < dis[v]) {
                    dis[v] = g[u][v];
                }
        }
        bool ok = true;
        for (int i = 0; i < n; ++i) if (!used[i]) ok = false;
        if (!ok) continue;
        // add activation cost for relays with at least one incident chosen edge in Prim tree
        // Reconstruct by checking if any city-relay edge is used in the tree is complex;
        // approximate: if a relay is connected, it is in used set.
        for (int j = 0; j < k; ++j) if ((mask >> j & 1) && used[n + j]) cost += c[j];
        ans = min(ans, cost);
    }
    cout << ans << '\n';
    return 0;
}
