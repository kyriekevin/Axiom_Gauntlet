class Solution:
    def findRepeatDocument(self, nums: List[int]) -> int:
        n = len(nums)
        for x in nums:
            if x < 0 or x > n:
                return -1

        for i in range(n):
            while nums[i] != i:
                if nums[i] == nums[nums[i]]:
                    return nums[i]

                target_idx = nums[i]
                nums[i], nums[target_idx] = nums[target_idx], nums[i]

        return -1

