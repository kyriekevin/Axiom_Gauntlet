#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

int main() {
    int n;
    cin >> n;

    int odd = 0, even = 0;
    int odd_idx = -1, even_idx = -1;
    for (int i = 1; i <= n; i++) {
        int x;
        cin >> x;
        if (x % 2) {
            odd++;
            if (odd == 1) odd_idx = i;
        }
        else {
            even++;
            if (even == 1) even_idx = i;
        }
    }

    if (odd == 1) cout << odd_idx << endl;
    else cout << even_idx << endl;

    return 0;
}
