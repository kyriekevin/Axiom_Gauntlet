class Solution:
    def minimumDeletions(self, nums: List[int]) -> int:
        max_idx = nums.index(max(nums))
        min_idx = nums.index(min(nums))
        n = len(nums)

        cand1 = min(max_idx + 1, n - max_idx) + min(min_idx + 1, n - min_idx)
        cand2 = max(max_idx, min_idx) + 1
        cand3 = n - min(min_idx, max_idx)

        return min(cand1, min(cand2, cand3))
