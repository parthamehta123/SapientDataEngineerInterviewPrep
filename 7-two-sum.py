def two_sum(nums, target):
    seen = {}

    for i, num in enumerate(nums):
        complement = target - num

        if complement in seen:
            return [seen[complement], i]

        seen[num] = i

    return []


if __name__ == "__main__":
    nums = [2, 7, 11, 15]

    print(two_sum(nums, 9))