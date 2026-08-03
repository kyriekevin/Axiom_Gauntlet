class Solution:
    def stoneGameIII(self, stoneValue: List[int]) -> str:
        n = len(stoneValue)
        f = [-inf] * n + [0]

        for i in range(n - 1, -1, -1):
            s = 0
            for j in range(i, min(i + 3, n)):
                s += stoneValue[j]
                f[i] = max(f[i], s - f[j + 1])

        if f[0] == 0:
            return "Tie"
        else:
            return "Alice" if f[0] > 0 else "Bob"

