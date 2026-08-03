#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

const int N = 1e5 + 10;
int a[N];
int n;

void quick_sort(int start, int end) {
    if (start >= end) return;

    int x = a[start + end >> 1], l = start - 1, r = end + 1;

    while (l < r) {
        while (a[++l] < x);
        while (a[--r] > x);
        if (l < r) swap(a[l], a[r]);
    }

    quick_sort(start, r);
    quick_sort(r + 1, end);
}

int main() {
    cin >> n;

    for (int i = 0; i < n; i++) cin >> a[i];
    quick_sort(0, n - 1);
    for (int i = 0; i < n; i++) cout << a[i] << " ";

    return 0;
}

