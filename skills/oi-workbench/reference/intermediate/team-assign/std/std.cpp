#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<array<int, 3>> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i][0] >> a[i][1] >> a[i][2];
    int half = n / 2;
    const long long NEG = -(1LL << 60);
    vector<vector<long long>> dp(half + 1, vector<long long>(half + 1, NEG));
    dp[0][0] = 0;
    for (int i = 0; i < n; ++i) {
        vector<vector<long long>> ndp(half + 1, vector<long long>(half + 1, NEG));
        for (int x = 0; x <= half; ++x) {
            for (int y = 0; y <= half; ++y) {
                long long cur = dp[x][y];
                if (cur == NEG) continue;
                int z = i - x - y;
                if (z < 0 || z > half) continue;
                if (x + 1 <= half)
                    ndp[x + 1][y] = max(ndp[x + 1][y], cur + a[i][0]);
                if (y + 1 <= half)
                    ndp[x][y + 1] = max(ndp[x][y + 1], cur + a[i][1]);
                if (z + 1 <= half)
                    ndp[x][y] = max(ndp[x][y], cur + a[i][2]);
            }
        }
        dp.swap(ndp);
    }
    long long ans = 0;
    for (int x = 0; x <= half; ++x)
        for (int y = 0; y <= half; ++y)
            if (n - x - y <= half)
                ans = max(ans, dp[x][y]);
    cout << ans << '\n';
    return 0;
}
