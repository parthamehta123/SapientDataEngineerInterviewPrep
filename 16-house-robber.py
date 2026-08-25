class Solution:
    def rob(self, nums: list[int]) -> int:
        prev1 = 0  # max money robbed up to previous house
        prev2 = 0  # max money robbed up to two houses ago
        
        for num in nums:
            # At each house, choose between robbing current + two houses ago, 
            # or skipping current house and keeping previous max
            current = max(prev1, prev2 + num)
            prev2 = prev1
            prev1 = current
            
        return prev1

if __name__ == "__main__":
    nums = [2, 7, 9, 3, 1]
    solution = Solution()
    print(solution.rob(nums))