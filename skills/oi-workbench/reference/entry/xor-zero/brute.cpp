#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> a(n);
    for (auto& x : a) cin >> x;
    long long ans = 0;
    for (int l = 0; l < n; ++l) {
        int x = 0;
        for (int r = l; r < n; ++r) {
            x ^= a[r];
            if (x == 0) ++ans;
        }
    }
    cout << ans << '\n';
    return 0;
}
