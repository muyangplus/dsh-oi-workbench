#include <bits/stdc++.h>
using namespace std;

const long long MOD = 998244353;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k;
    cin >> n >> k;
    int maxK = n * (n - 1) / 2;
    if (k > maxK) {
        cout << 0 << '\n';
        return 0;
    }
    vector<long long> dp(maxK + 1, 0), pref(maxK + 1, 0);
    dp[0] = 1;
    for (int i = 1; i <= n; ++i) {
        vector<long long> ndp(maxK + 1, 0);
        pref[0] = dp[0];
        for (int j = 1; j <= maxK; ++j) pref[j] = (pref[j - 1] + dp[j]) % MOD;
        for (int j = 0; j <= maxK; ++j) {
            int L = max(0, j - (i - 1));
            long long val = pref[j] - (L ? pref[L - 1] : 0);
            ndp[j] = (val % MOD + MOD) % MOD;
        }
        dp.swap(ndp);
    }
    cout << dp[k] % MOD << '\n';
    return 0;
}
