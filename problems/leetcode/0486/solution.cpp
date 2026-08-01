class Solution {
public:
    bool predictTheWinner(vector<int>& nums) {
        int n = nums.size();
        vector<vector<int>> f(n, vector<int>(n));

        for (int lens = 1; lens <= n; lens++) {
            for (int i = 0; i + lens  - 1 < n; i++) {
                int j = i + lens - 1;
                if (i == j) f[i][j] = nums[i];
                else f[i][j] = max(nums[i] - f[i + 1][j], nums[j] - f[i][j - 1]);
            }
        }

        return f[0][n - 1] >= 0;
    }
};
