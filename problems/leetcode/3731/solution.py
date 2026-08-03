class Solution:
    def findMissingElements(self, nums: List[int]) -> List[int]:
        st = set(nums)
        minv, maxv = min(nums), max(nums)

        return [x for x in range(minv + 1, maxv) if x not in st]
