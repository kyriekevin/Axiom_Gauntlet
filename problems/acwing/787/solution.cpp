#include <iostream>
#include <cstring>
#include <algorithm>
using namespace std;

const int N = 1e5 + 10;
int g[N], tmp[N];
int n;

void merge_sort(int start, int end) {
    if (start >= end) return;

    int mid = start + end >> 1;
    merge_sort(start, mid);
    merge_sort(mid + 1, end);

    int i = start, j = mid + 1, k = 0;
    while (i <= mid && j <= end) {
        if (g[i] <= g[j]) tmp[k++] = g[i++];
        else tmp[k++] = g[j++];
    }

    while (i <= mid) tmp[k++] = g[i++];
    while (j <= end) tmp[k++] = g[j++];

    for (int i = start, j = 0; i <= end && j <= k; i++, j++)
        g[i] = tmp[j];
}

int main() {
    cin >> n;
    for (int i = 0; i < n; i++) cin >> g[i];
    merge_sort(0, n - 1);
    for (int i = 0; i < n; i++) cout << g[i] << " ";

    return 0;
}
