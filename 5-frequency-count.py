def frequency_count(nums):
    freq = {}

    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    return freq


if __name__ == "__main__":
    nums = [1, 2, 2, 3, 3, 3]

    print(frequency_count(nums))