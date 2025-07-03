# Simulation of the get_rickdate_format() function

def to_base36(num):
    """Converts an integer to a base-36 string."""
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return "0"
    base36 = []
    while num:
        num, i = divmod(num, 36)
        base36.append(alphabet[i])
    return "".join(reversed(base36))

def get_rickdate(current_time_tuple):
    """
    Returns the 'rickdate' formatted string (YYYYMMDD as base36, last 3 chars).
    Takes a time tuple (year, month, day, ...) as input.
    """
    year, month, day, _, _, _, _, _ = current_time_tuple

    # Convert each part to base 36 separately
    year_b36 = to_base36(year).upper()
    month_b36 = to_base36(month).upper()
    day_b36 = to_base36(day).upper()
    
    # Concatenate them to form the full Rickdate string
    full_rickdate = f"{year_b36}{month_b36}{day_b36}"
    
    # Return the last 3 characters for the abbreviated form
    return full_rickdate[-3:]

# --- Simulate current date/time ---
# Simulating time.localtime() for Sunday, June 29, 2025
# (year, month, mday, hour, minute, second, weekday, yearday)
# weekday: 0=Monday, 6=Sunday
# simulated_time_tuple = (2025, 6, 29, 23, 0, 0, 6, 180) # Sunday, June 29, 2025, 23:00:00

# Get the rickdate
# rickdate_result = get_rickdate_format_simulated(simulated_time_tuple)

# print(f"Simulated Date (YYYY-MM-DD): {simulated_time_tuple[0]}-{simulated_time_tuple[1]:02d}-{simulated_time_tuple[2]:02d}")
# print(f"Calculated Rickdate (last 3 chars): {rickdate_result}")

# Let's break it down for this specific date:
# Year 2025 in base 36:
# 2025 // 36 = 56 remainder 9
# 56 // 36 = 1 remainder 20 (U in base36)
# 1 // 36 = 0 remainder 1
# So 2025 (base 10) is 1U9 (base 36)

# Month 6 (June) in base 36:
# 6 (base 10) is 6 (base 36)

# Day 29 in base 36:
# 29 (base 10) is T (base 36)

# Full Rickdate: 1U96T
# Last 3 characters: 96T