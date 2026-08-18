#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m, k;
    cin >> n >> m >> k;
    vector<vector<int>> a(n + 1, vector<int>(m + 1, 0));
    int top = 1, bottom = n, left = 1, right = m, cur = 1;
    while (top <= bottom && left <= right) {
        for (int c = left; c <= right; ++c) a[top][c] = cur++;
        for (int r = top + 1; r <= bottom; ++r) a[r][right] = cur++;
        if (top < bottom)
            for (int c = right - 1; c >= left; --c) a[bottom][c] = cur++;
        if (left < right)
            for (int r = bottom - 1; r > top; --r) a[r][left] = cur++;
        top++; bottom--; left++; right--;
    }
    for (int r = 1; r <= n; ++r)
        for (int c = 1; c <= m; ++c)
            if (a[r][c] == k) {
                cout << r << ' ' << c << '\n';
                return 0;
            }
    return 0;
}
