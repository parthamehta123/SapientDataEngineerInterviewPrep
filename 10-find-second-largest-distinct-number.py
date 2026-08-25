def second_largest(nums):
    largest = None
    second = None

    for num in nums:
        if largest is None or num > largest:
            if num != largest:
                second = largest
                largest = num

        elif num != largest and (
            second is None or num > second
        ):
            second = num

    return second


if __name__ == "__main__":
    nums = [10, 20, 20, 30, 40]

    print(second_largest(nums))