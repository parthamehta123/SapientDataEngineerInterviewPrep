def find_duplicates(nums):
    seen = set()
    duplicates = set()

    for num in nums:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)

    return list(duplicates)


if __name__ == "__main__":
    nums = [1, 2, 3, 2, 4, 5, 1]

    print(find_duplicates(nums))