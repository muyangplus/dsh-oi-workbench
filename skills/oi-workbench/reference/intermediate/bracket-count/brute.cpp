#include <bits/stdc++.h>
using namespace std;

int n, d, ans;
string s;

void dfs(int pos, int open, int close, int dep) {
    if (pos == 2 * n) {
        if (open == n && close == n) ++ans;
        return;
    }
    if (open < n && dep + 1 <= d) {
        s.push_back('(');
        dfs(pos + 1, open + 1, close, dep + 1);
        s.pop_back();
    }
    if (close < n && dep > 0) {
        s.push_back(')');
        dfs(pos + 1, open, close + 1, dep - 1);
        s.pop_back();
    }
}

int main() {
    cin >> n >> d;
    dfs(0, 0, 0, 0);
    cout << ans << '\n';
    return 0;
}
