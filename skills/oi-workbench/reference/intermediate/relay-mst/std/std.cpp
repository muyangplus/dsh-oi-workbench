#include <bits/stdc++.h>
using namespace std;

struct Edge {
    int u, v;
    long long w;
    bool operator<(const Edge& o) const { return w < o.w; }
};

struct DSU {
    vector<int> p;
    DSU(int n) : p(n) { iota(p.begin(), p.end(), 0); }
    int find(int x) { return p[x] == x ? x : p[x] = find(p[x]); }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        p[a] = b;
        return true;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k;
    cin >> n >> m >> k;
    vector<Edge> base(m);
    for (int i = 0; i < m; ++i) {
        cin >> base[i].u >> base[i].v >> base[i].w;
        --base[i].u; --base[i].v;
    }
    vector<long long> c(k);
    vector<vector<long long>> b(k, vector<long long>(n));
    for (int j = 0; j < k; ++j) {
        cin >> c[j];
        for (int i = 0; i < n; ++i) cin >> b[j][i];
    }
    const long long INF = (1LL << 62);
    long long ans = INF;
    for (int mask = 0; mask < (1 << k); ++mask) {
        vector<Edge> es = base;
        for (int j = 0; j < k; ++j) if (mask >> j & 1) {
            for (int i = 0; i < n; ++i)
                es.push_back({i, n + j, b[j][i]});
        }
        sort(es.begin(), es.end());
        DSU dsu(n + k);
        vector<char> used(k, 0);
        long long cost = 0;
        for (auto& e : es) {
            if (dsu.unite(e.u, e.v)) {
                cost += e.w;
                if (e.u >= n && !used[e.u - n]) {
                    used[e.u - n] = 1;
                    cost += c[e.u - n];
                }
                if (e.v >= n && !used[e.v - n]) {
                    used[e.v - n] = 1;
                    cost += c[e.v - n];
                }
            }
        }
        bool ok = true;
        for (int i = 1; i < n; ++i)
            if (dsu.find(0) != dsu.find(i)) { ok = false; break; }
        if (ok) ans = min(ans, cost);
    }
    cout << ans << '\n';
    return 0;
}
