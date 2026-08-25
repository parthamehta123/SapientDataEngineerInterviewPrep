# def reverse_string(s):
#     return s[::-1]

def reverse_string(s):
    chars = list(s)

    left = 0
    right = len(chars) - 1

    while left < right:
        chars[left], chars[right] = chars[right], chars[left]

        left += 1
        right -= 1

    return "".join(chars)

if __name__ == "__main__":
    s = "sapient"
    print(reverse_string(s))