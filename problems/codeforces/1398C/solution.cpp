#include <iostream>
#include <cstring>
#include <algorithm>
#include <map>
using namespace std;

typedef long long ll;

void solve() {
    int n;
    cin >> n;
    string s;
    cin >> s;

    map<int, int> cnt;
    cnt[0] = 1;

    ll res = 0;
    int pref = 0;

    for (int i = 1; i <= n; i++) {
        pref += (s[i - 1] - '0');
        res += cnt[pref - i];
        cnt[pref - i] ++;
    }

    cout << res << endl;
}

int main() {
    int t;
    cin >> t;
    while (t--) {
        solve();
    }

    return 0;
}

