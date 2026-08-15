class Solution:
    def missingInteger(self, nums: List[int]) -> int:
        tot = nums[0]
        for a, b in pairwise(nums):
            if b == a + 1:
                tot += b
            else:
                break

        st = set(nums)
        while tot in st:
            tot += 1

        return tot

