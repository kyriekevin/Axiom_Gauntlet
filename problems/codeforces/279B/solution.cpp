#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

const int N = 1e5 + 10;
int g[N];

int main() {
    int n;
    long long t;
    cin >> n >> t;
    for (int i = 0; i < n; i++) cin >> g[i];

    long long s = 0;
    int res = 0;

    for (int l = 0, r = 0; r < n; r++) {
        s += g[r];
        while (s > t) s -= g[l++];
        res = max(res, r - l + 1);
    }

    cout << res << endl;

    return 0;
}
