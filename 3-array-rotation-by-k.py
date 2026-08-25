# def rotate_right(nums, k):
#     if not nums:
#         return

#     n = len(nums)
#     k %= n  # Handle cases where k is greater than n

#     # # Reverse the entire array
#     # nums.reverse()

#     # # Reverse the first k elements
#     # nums[:k] = reversed(nums[:k])

#     # # Reverse the remaining n-k elements
#     # nums[k:] = reversed(nums[k:])

#     return nums[-k:] + nums[:-k]  # Rotate the array to the right by k positions

# if __name__ == "__main__":
#     arr = [1, 2, 3, 4, 5, 6, 7]
#     k = 3
#     rotate_right(arr, k)
#     print(arr)  # Output: [5, 6, 7, 1, 2, 3, 4]

def rotate_right(nums, k):
    if not nums:
        return

    n = len(nums)
    k %= n

    def reverse(left, right):
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]

            left += 1
            right -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)


if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5, 6, 7]

    rotate_right(nums, 3)

    print(nums)