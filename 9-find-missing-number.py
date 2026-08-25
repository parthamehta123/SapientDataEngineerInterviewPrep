def missing_number(nums):
    n = len(nums) + 1

    expected = n * (n + 1) // 2
    actual = sum(nums)

    return expected - actual


if __name__ == "__main__":
    nums = [1, 2, 3, 5]

    print(missing_number(nums))