#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    unordered_map<int, long long> cnt;
    cnt[0] = 1;
    int pref = 0;
    long long ans = 0;
    for (int i = 0; i < n; ++i) {
        int x;
        cin >> x;
        pref ^= x;
        ans += cnt[pref];
        cnt[pref]++;
    }
    cout << ans << '\n';
    return 0;
}
