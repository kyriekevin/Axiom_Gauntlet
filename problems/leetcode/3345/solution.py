class Solution:
    def smallestNumber(self, n: int, t: int) -> int:
        def check(num: int) -> bool:
            s = 1
            while num > 0:
                s *= num % 10
                num //= 10
                if s == 0:
                    break
            return s % t == 0

        while not check(n):
            n += 1

        return n

