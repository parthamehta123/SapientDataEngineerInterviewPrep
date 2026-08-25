def compress(chars: list[str]) -> int:
    write = 0
    read = 0
    print(f"Start: chars={chars}")
    
    while read < len(chars):
        run_start = read
        curr_char = chars[read]
        count = 0
        
        # Count the length of the current run
        while read < len(chars) and chars[read] == curr_char:
            read += 1
            count += 1
        print(
            f"Run found: char='{curr_char}', start={run_start}, end={read - 1}, count={count}"
        )
            
        # Write the character
        chars[write] = curr_char
        write += 1
        print(f"Wrote char '{curr_char}' at index {write - 1}")
        
        # Write the count digits if greater than 1
        # This is done because we need to handle counts that are more than one digit (e.g., 12, 100)
        if count > 1:
            for digit in str(count):
                chars[write] = digit
                print(f"Wrote count digit '{digit}' at index {write}")
                write += 1
        print(f"Current compressed prefix: {chars[:write]}")
                
    print(f"Done: new_length={write}, compressed={chars[:write]}")
    return write

if __name__ == "__main__":
    chars = ["a", "a", "b", "b", "c", "c", "c"]
    new_length = compress(chars)
    print(new_length)  # Output: 6
    print(chars[:new_length])  # Output: ['a', '2', 'b', '2', 'c', '3']