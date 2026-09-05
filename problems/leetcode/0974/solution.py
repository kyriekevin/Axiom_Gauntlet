class Solution:
    def subarraysDivByK(self, nums: List[int], k: int) -> int:
        cnt = [0] * k
        cnt[0] = 1

        res = pre_sum = 0

        for num in nums:
            pre_sum = (pre_sum + num) % k
            res += cnt[pre_sum]
            cnt[pre_sum] += 1

        return res

