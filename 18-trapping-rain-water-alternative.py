def trap_water_per_bar(height):
    if not height:
        return []
    
    n = len(height)
    left_max = [0] * n
    right_max = [0] * n
    water_at_bar = [0] * n
    
    # Fill left_max array
    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])
        
    # Fill right_max array
    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])
        
    # Calculate water trapped at each bar
    for i in range(n):
        water_level = min(left_max[i], right_max[i])
        water_at_bar[i] = max(0, water_level - height[i])
        
    return water_at_bar

# Example usage:
elevation = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
print(trap_water_per_bar(elevation))
# Output: [0, 0, 1, 0, 1, 2, 1, 0, 0, 1, 0, 0]
