def move_zeros(nums):
    write = 0

    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1

    return nums


if __name__ == "__main__":
    nums = [0, 1, 0, 3, 12]

    print(move_zeros(nums))