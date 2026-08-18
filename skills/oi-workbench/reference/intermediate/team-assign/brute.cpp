#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<array<int, 3>> a(n);
    for (int i = 0; i < n; ++i) cin >> a[i][0] >> a[i][1] >> a[i][2];
    int half = n / 2;
    long long best = 0;
    int total = 1;
    for (int i = 0; i < n; ++i) total *= 3;
    for (int mask = 0; mask < total; ++mask) {
        int x = mask, cnt[3] = {0, 0, 0};
        long long sum = 0;
        for (int i = 0; i < n; ++i) {
            int g = x % 3;
            x /= 3;
            cnt[g]++;
            sum += a[i][g];
        }
        if (cnt[0] <= half && cnt[1] <= half && cnt[2] <= half)
            best = max(best, sum);
    }
    cout << best << '\n';
    return 0;
}
