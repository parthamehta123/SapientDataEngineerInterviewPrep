def merge_sorted(a, b):
    i = 0
    j = 0
    result = []

    # Compare elements from both arrays
    while i < len(a) and j < len(b):

        if a[i] <= b[j]:
            result.append(a[i])
            i += 1

        else:
            result.append(b[j])
            j += 1

    # Add remaining elements from a
    while i < len(a):
        result.append(a[i])
        i += 1

    # Add remaining elements from b
    while j < len(b):
        result.append(b[j])
        j += 1

    return result


if __name__ == "__main__":
    a = [1, 3, 5]
    b = [2, 4, 6]

    print(merge_sorted(a, b))