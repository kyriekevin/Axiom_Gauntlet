class Solution:
    def predictTheWinner(self, nums: List[int]) -> bool:
        n = len(nums)
        f = [[0] * n for _ in range(n)]

        for lens in range(1, n + 1):
            for i in range(0, n - lens + 1):
                j = i + lens - 1
                if lens == 1:
                    f[i][j] = nums[i]
                else:
                    f[i][j] = max(nums[i] - f[i + 1][j], nums[j] - f[i][j - 1])

        return f[0][n - 1] >= 0
