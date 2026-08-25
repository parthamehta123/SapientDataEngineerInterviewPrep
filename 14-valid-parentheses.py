class Solution:
    def isValid(self, s: str) -> bool:
        # Map closing brackets to their corresponding opening brackets
        bracket_map = {")": "(", "}": "{", "]": "["}
        stack = []
        
        for char in s:
            # If it's a closing bracket
            if char in bracket_map:
                # Pop the top element if stack isn't empty, else use a dummy value
                top_element = stack.pop() if stack else '#'
                
                # If the mapping doesn't match the popped element, it's invalid
                if bracket_map[char] != top_element:
                    return False
            else:
                # It's an opening bracket, push it onto the stack
                stack.append(char)
                
        # If the stack is empty, all brackets were matched correctly
        return not stack

if __name__ == "__main__":
    solution = Solution()
    test_cases = [
        ("()", True),
        ("()[]{}", True),
        ("(]", False),
        ("([)]", False),
        ("{[]}", True),
        ("", True),
        ("(", False),
        (")", False),
        ("{[()()]}", True),
        ("{[(])}", False),
        ("])", False),
    ]

    for s, expected in test_cases:
        result = solution.isValid(s)
        print(f"isValid('{s}') = {result}, expected = {expected}, {'PASS' if result == expected else 'FAIL'}")