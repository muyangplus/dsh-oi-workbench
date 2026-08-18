#include <bits/stdc++.h>
using namespace std;

const long long MOD = 998244353;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, d;
    cin >> n >> d;
    vector<long long> dp(d + 1, 0), ndp(d + 1, 0);
    dp[0] = 1;
    for (int len = 0; len < 2 * n; ++len) {
        fill(ndp.begin(), ndp.end(), 0);
        for (int dep = 0; dep <= d; ++dep) {
            if (!dp[dep]) continue;
            if (dep + 1 <= d) {
                ndp[dep + 1] = (ndp[dep + 1] + dp[dep]) % MOD;
            }
            if (dep > 0) {
                ndp[dep - 1] = (ndp[dep - 1] + dp[dep]) % MOD;
            }
        }
        dp.swap(ndp);
    }
    cout << dp[0] % MOD << '\n';
    return 0;
}
