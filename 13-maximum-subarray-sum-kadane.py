def max_subarray(nums):
    current = nums[0]
    best = nums[0]

    for num in nums[1:]:
        current = max(
            num,
            current + num
        )

        best = max(
            best,
            current
        )

    return best


if __name__ == "__main__":
    nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

    print(max_subarray(nums))