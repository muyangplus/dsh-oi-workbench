#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<string> s(n);
    for (auto& x : s) cin >> x;
    sort(s.begin(), s.end());
    string best;
    do {
        string cur;
        for (auto& x : s) cur += x;
        if (cur > best) best = cur;
    } while (next_permutation(s.begin(), s.end()));
    cout << best << '\n';
    return 0;
}
