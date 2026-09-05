#include <iostream>
#include <cstring>
#include <algorithm>
#include <map>
using namespace std;

typedef long long ll;

const int N = 2e5 + 10;
ll arr[N];

void solve() {
    int n;
    cin >> n;
    for (int i = 0; i < n; i++) cin >> arr[i];

    ll res = 0, T = 0;
    map<ll, int> cnt;
    bool flag = true;

    auto settle = [&]() {
        if (flag) {
            res += cnt[0];
            flag = false;
        }
        else {
            int M = 0;
            for (auto &[k, v]: cnt) M = max(M, v);
            res += M + (cnt[0] == M);
        }
        T = 0;
        cnt.clear();
    };

    for (int i = 0; i < n; i++) {
        if (arr[i] == 0) settle();
        else {
            T += arr[i];
            cnt[T]++;
        }
    }
    settle();

    cout << res << endl;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;

    while (t--) solve();

    return 0;
}
