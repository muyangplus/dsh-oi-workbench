#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;
    long long ans = 0;
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j)
            for (int k = j + 1; k < n; ++k) {
                long long x = a[i], y = a[j], z = a[k];
                if (x + y > z && x + z > y && y + z > x) ++ans;
            }
    cout << ans << '\n';
    return 0;
}
