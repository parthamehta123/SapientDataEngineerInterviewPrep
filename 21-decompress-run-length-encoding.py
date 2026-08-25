# Decompress a run-length encoded list.
# Write a function that takes a list of integers representing a run-length encoded list and returns the decompressed list.
# The input list contains pairs of integers, where the first integer in each pair represents the frequency of the second integer. 
# For example, the input list [1, 2, 3, 4] represents 1 occurrence of 2 followed by 3 occurrences of 4.
def decompressRLElist(nums: list[int]) -> list[int]:
    result = []
    # Step by 2 to process [freq, val] pairs
    for i in range(0, len(nums), 2):
        freq = nums[i]
        val = nums[i + 1]
        result.extend([val] * freq)
    return result

if __name__ == "__main__":
    nums = [1, 2, 3, 4]
    print(decompressRLElist(nums))  # Output: [2, 4, 4, 4]