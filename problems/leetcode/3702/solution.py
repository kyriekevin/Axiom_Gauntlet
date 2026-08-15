class Solution:
    def longestSubsequence(self, nums: List[int]) -> int:
        n = len(nums)
        tot_xor = 0
        all_zero = True

        for x in nums:
            tot_xor ^= x
            if x > 0:
                all_zero = False

        if tot_xor > 0:
            return n
        return 0 if all_zero else n - 1

