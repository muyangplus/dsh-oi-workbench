#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<string> s(n);
    for (int i = 0; i < n; ++i) cin >> s[i];
    sort(s.begin(), s.end(), [](const string& a, const string& b) {
        return a + b > b + a;
    });
    string ans;
    for (auto& x : s) ans += x;
    cout << ans << '\n';
    return 0;
}
