// brute.cpp —— 朴素绝对正确：每次排序取最小两堆，O(n^2 log n)，仅用于小数据对拍
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<long long> a(n);
    for (auto &x : a) cin >> x;
    long long ans = 0;
    while (a.size() > 1) {
        sort(a.begin(), a.end());
        long long s = a[0] + a[1];
        ans += s;
        a[0] = s;
        a.erase(a.begin() + 1);
    }
    cout << ans << '\n';
    return 0;
}
