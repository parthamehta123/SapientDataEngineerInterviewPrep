def encode_rle(s: str) -> str:
    if not s:
        return ""
        
    result = []
    count = 1
    
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            # This happens when the current character is different from the previous one
            result.append(f"{s[i - 1]}{count}")
            count = 1
            
    # Append the final run. This is necessary because the last run won't be added in the loop. Its because the loop only 
    # adds a run when it encounters a different character, so the last run will be left out.
    result.append(f"{s[-1]}{count}")
    return "".join(result)

if __name__ == "__main__":
    s = "aaabbc"
    encoded = encode_rle(s)
    print(encoded)  # Output: "a3b2c1"