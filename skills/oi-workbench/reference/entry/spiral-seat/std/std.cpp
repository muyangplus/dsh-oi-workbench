#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long n, m, k;
    cin >> n >> m >> k;
    long long top = 1, bottom = n, left = 1, right = m;
    while (true) {
        long long h = bottom - top + 1;
        long long w = right - left + 1;
        if (h == 1) {
            cout << top << ' ' << left + k - 1 << '\n';
            return 0;
        }
        if (w == 1) {
            cout << top + k - 1 << ' ' << left << '\n';
            return 0;
        }
        long long per = 2 * (w + h) - 4;
        if (k <= w) {
            cout << top << ' ' << left + k - 1 << '\n';
            return 0;
        }
        k -= w;
        if (k <= h - 1) {
            cout << top + k << ' ' << right << '\n';
            return 0;
        }
        k -= h - 1;
        if (k <= w - 1) {
            cout << bottom << ' ' << right - k << '\n';
            return 0;
        }
        k -= w - 1;
        if (k <= h - 2) {
            cout << bottom - k << ' ' << left << '\n';
            return 0;
        }
        k -= h - 2;
        top++; bottom--; left++; right--;
    }
    return 0;
}
