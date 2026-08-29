class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        n = len(nums)
        s = [0] * (n + 1)
        for i, x in enumerate(nums):
            s[i + 1] = s[i] + x

        cnt = defaultdict(int)
        res = 0
        for s_i in s:
            res += cnt[s_i - k]
            cnt[s_i] += 1

        return res

