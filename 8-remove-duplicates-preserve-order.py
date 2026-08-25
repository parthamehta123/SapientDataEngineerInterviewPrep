def remove_duplicates(nums):
    seen = set()
    result = []

    for num in nums:
        if num not in seen:
            seen.add(num)
            result.append(num)

    return result


if __name__ == "__main__":
    nums = [1, 2, 2, 3, 1, 4]

    print(remove_duplicates(nums))