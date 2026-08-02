class Solution:
    def stoneGame(self, piles: List[int]) -> bool:
        n = len(piles)
        f = [[0] * n for _ in range(n)]

        for length in range(1, n + 1):
            for i in range(n + 1 - length):
                j = i + length - 1
                if i == j:
                    f[i][j] = piles[i]
                else:
                    f[i][j] = max(piles[i] - f[i + 1][j], piles[j] - f[i][j - 1])

        return f[0][n - 1] > 0
