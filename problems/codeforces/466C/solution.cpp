#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

typedef long long ll;

const int N = 5e5 + 10;
ll g[N];
int n;

int main() {
    cin >> n;

    ll tot = 0;
    for (int i = 0; i < n; i++) {
        cin >> g[i];
        tot += g[i];
    }

    if (n < 3 || tot % 3 != 0) {
        cout << 0 << endl;
        return 0;
    }

    ll target = tot / 3, pre_sum = 0, cnt = 0, res = 0;
    for (int i = 0; i < n - 1; i++) {
        pre_sum += g[i];

        if (i >= 1 && pre_sum == 2 * target)
            res += cnt;

        if (pre_sum == target)
            cnt++;
    }

    cout << res << endl;

    return 0;
}
