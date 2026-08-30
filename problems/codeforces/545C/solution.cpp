#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

typedef long long ll;

const int N = 1e5 + 10;
ll x[N], h[N];

int main() {
    int n;
    cin >> n;

    for (int i = 0; i < n ;i++) {
        cin >> x[i] >> h[i];
    }

    if (n <= 2) {
        cout << n << endl;
        return 0;
    }

    int res = 2;
    ll last_right = x[0];

    for (int i = 1; i < n - 1; i++) {
        if (x[i] - h[i] > last_right) {
            res++;
            last_right = x[i];
        }
        else if (x[i] + h[i] < x[i + 1]) {
            res++;
            last_right = x[i] + h[i];
        }
        else last_right = x[i];
    }

    cout << res << endl;

    return 0;
}
