#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
    vector<int> p(n);
    iota(p.begin(), p.end(), 1);
    int ans = 0;
    do {
        int inv = 0;
        for (int i = 0; i < n; ++i)
            for (int j = i + 1; j < n; ++j)
                if (p[i] > p[j]) ++inv;
        if (inv == k) ++ans;
    } while (next_permutation(p.begin(), p.end()));
    cout << ans << '\n';
    return 0;
}
