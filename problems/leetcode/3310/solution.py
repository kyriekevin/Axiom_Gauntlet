class Solution:
    def remainingMethods(self, n: int, k: int, invocations: List[List[int]]) -> List[int]:
        g = [[] for _ in range(n)]
        for x, y in invocations:
            g[x].append(y)

        s = set()
        def dfs(x: int) -> None:
            s.add(x)
            for y in g[x]:
                if y not in s:
                    dfs(y)

        dfs(k)

        for x, y in invocations:
            if x not in s and y in s:
                return list(range(n))

        return [node for node in range(n) if node not in s]
