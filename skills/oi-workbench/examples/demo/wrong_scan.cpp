// wrong_scan.cpp —— 复杂度层错解：每轮线性扫描找最小两堆，O(n^2)。
// 能过 Subtask 1/2（n<=5000），在 Subtask 3（n=1e5）必须 TLE。
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    long long ans = 0;
    while (a.size() > 1) {
        int p = 0;
        for (int i = 1; i < (int)a.size(); i++)
            if (a[i] < a[p]) p = i;
        long long v = a[p];
        a.erase(a.begin() + p);
        int q = 0;
        for (int i = 1; i < (int)a.size(); i++)
            if (a[i] < a[q]) q = i;
        long long w = a[q];
        a.erase(a.begin() + q);
        ans += v + w;
        a.push_back(v + w);
    }
    cout << ans << '\n';
    return 0;
}
