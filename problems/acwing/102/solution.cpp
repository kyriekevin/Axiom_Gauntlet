#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

const int N = 1e5 + 10;
int g[N];
double s[N];
int n, m;

bool check(double avg) {
    for (int i = 1; i <= n; i++) s[i] = s[i - 1] + g[i] - avg;
    double mins = 0;
    for (int i = m, j = 0; i <= n; i++, j++) {
        mins = min(mins, s[j]);
        if (s[i] >= mins) return true;
    }
    return false;
}

int main() {
    cin >> n >> m;
    for (int i = 1; i <= n; i++) cin >> g[i];

    double l = 0, r = 2000;
    while (r - l >= 1e-5) {
        double mid = (l + r) / 2;
        if (check(mid)) l = mid;
        else r = mid;
    }

    cout << (int) (1000 * r) << endl;

    return 0;
}
