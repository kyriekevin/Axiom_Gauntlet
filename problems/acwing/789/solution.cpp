#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

const int N = 1e5 + 10;
int g[N];
int n, q;

int main() {
    cin >> n >> q;
    for (int i = 0; i < n; i++) cin >> g[i];

    while (q--) {
        int l = 0, r = n - 1, x;
        cin >> x;
        while (l < r) {
            int mid = l + r >> 1;
            if (g[mid] < x) l = mid + 1;
            else r = mid;
        }
        if (g[l] != x) cout << "-1 -1" << endl;
        else {
            cout << l << " ";
            r = n - 1;
            while (l < r) {
                int mid = l + r + 1 >> 1;
                if (g[mid] > x) r = mid - 1;
                else l = mid;
            }
            cout << l << endl;
        }
    }

    return 0;
}
