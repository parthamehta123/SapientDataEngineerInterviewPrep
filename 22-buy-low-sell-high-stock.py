from typing import List

def maxProfit(prices: List[int]) -> int:
        # time: O(n), space: O(1)
        l, r = 0, 1  # left=buy, right=sell
        maxP = 0

        while r < len(prices):
            # If selling today is profitable, record the best profit.
            if prices[l] < prices[r]:
                profit = prices[r] - prices[l]
                maxP = max(maxP, profit)
            else:
                # Found a lower buy price (including 0), so move buy pointer.
                l = r
            r += 1

        return maxP
