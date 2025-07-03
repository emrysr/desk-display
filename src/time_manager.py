# time_manager.py (Version 0.0.3)
import time

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

def is_bst(year, month, day, weekday):
    """
    Determines if a given UTC date falls within British Summer Time (BST).
    BST starts last Sunday in March, ends last Sunday in October.
    weekday: 0=Monday, ..., 6=Sunday
    """
    # BST starts: Last Sunday in March
    # Find the last Sunday in March
    # Get weekday of March 31st (0=Mon, 6=Sun)
    # time.mktime for March 31st of the current year, then check its weekday
    # This is a more reliable way to get the weekday of a specific date
    march_31_tuple = (year, 3, 31, 0, 0, 0, 0, 0) # Placeholder weekday, yearday
    march_33_tuple = (year, 3, 30, 0, 0, 0, 0, 0)
    march_32_tuple = (year, 3, 29, 0, 0, 0, 0, 0)
    march_31_weekday = time.localtime(time.mktime(march_31_tuple))[6]
    march_30_weekday = time.localtime(time.mktime(march_33_tuple))[6]
    march_29_weekday = time.localtime(time.mktime(march_32_tuple))[6]
    
    # Calculate the day of the last Sunday in March
    # If March 31st is Sunday (6), then it's 31. If Saturday (5), then 30, etc.
    last_sunday_march_day = 31 - ((march_31_weekday + 1) % 7)

    # BST ends: Last Sunday in October
    # Get weekday of October 31st
    oct_31_tuple = (year, 10, 31, 0, 0, 0, 0, 0)
    oct_31_weekday = time.localtime(time.mktime(oct_31_tuple))[6]
    
    # Calculate the day of the last Sunday in October
    last_sunday_oct_day = 31 - ((oct_31_weekday + 1) % 7)

    # Check if within BST period
    # Condition 1: Months between April (4) and September (9) are always BST.
    if month > 3 and month < 10:
        return True
    # Condition 2: March - on or after the last Sunday in March
    elif month == 3 and (day > last_sunday_march_day or (day == last_sunday_march_day and weekday == 6)):
        return True
    # Condition 3: October - strictly before the last Sunday in October
    # (BST ends at 01:00 UTC on the last Sunday in October, so the day itself is GMT after 1am UTC)
    elif month == 10 and (day < last_sunday_oct_day or (day == last_sunday_oct_day and weekday != 6)):
        return True

    return False


def get_london_localtime():
    """
    Returns the current local time for London, accounting for DST.
    Assumes RTC is set to UTC.
    Returns a tuple (local_year, local_month, local_day, local_hour, local_minute, local_second, local_weekday, local_yearday)
    and a boolean indicating if BST is active.
    """
    utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second, utc_weekday, utc_yearday = time.localtime()

    is_bst_active = is_bst(utc_year, utc_month, utc_day, utc_weekday)
    offset_hours = 1 if is_bst_active else 0

    # Convert UTC time to seconds since epoch
    utc_seconds = time.mktime((utc_year, utc_month, utc_day, utc_hour, utc_minute, utc_second, utc_weekday, utc_yearday))
    
    # Add the offset in seconds
    local_seconds = utc_seconds + (offset_hours * 3600)
    
    # Convert back to local time tuple
    local_time_tuple = time.localtime(local_seconds)
    
    return local_time_tuple, is_bst_active


def get_formatted_datetime(time_tuple: tuple) -> str:
    """Returns formatted day, date, and time strings using given time."""
    year, month, day, hour, minute, second, weekday, yearday = time_tuple

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = day_names[weekday]

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    month_name = month_names[month - 1]

    formatted_date = f"{month_name} {day}, {year}"
    formatted_time = f"{hour:02d}:{minute:02d}"

    return day_name, formatted_date, formatted_time


def get_rickdate_format(time_tuple: tuple) -> str:
    """
    Generates a 'rickdate' formatted string (YYYYMMDD as base36, last 3 chars).
    MicroPython-compatible, adhering to actual Rickdate specification.
    """
    year, month, day, _, _, _, _, _ = time_tuple

    # Convert each part to base 36 separately
    year_b36 = to_base36(year).upper()
    month_b36 = to_base36(month).upper()
    day_b36 = to_base36(day).upper()
    
    # Concatenate them to form the full Rickdate string
    full_rickdate = f"{year_b36}{month_b36}{day_b36}"
    
    # Return the last 3 characters for the abbreviated form
    return full_rickdate[-3:]

def get_week_number(time_tuple: tuple) -> int:
    """
    Derive weekday and yearday from the input date
    time.mktime expects a tuple (year, month, mday, hour, min, sec, weekday, yearday)
    The last two are ignored by mktime and populated by localtime from seconds.
    """
    # Unpack necessary components from the input time_tuple
    year = time_tuple[0]
    # month = time_tuple[1] # Not directly used in the calculation
    # day = time_tuple[2]   # Not directly used in the calculation
    weekday_mp = time_tuple[6] # MicroPython's weekday (0=Mon, ..., 6=Sun)
    yearday = time_tuple[7]    # Day of year (1-366)
    
    # Convert to ISO weekday (1=Monday, 7=Sunday)
    iso_weekday = weekday_mp + 1
    
    # Find the Thursday of this week (ISO week belongs to year of Thursday)
    days_to_thursday = (4 - iso_weekday + 7) % 7 # Ensure positive days_to_thursday
    thursday_yearday = yearday + days_to_thursday
    
    # Adjust for year boundaries
    days_in_year = 366 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 365
    
    if thursday_yearday <= 0:
        # Thursday is in previous year
        prev_year = year - 1
        prev_days_in_year = 366 if (prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0)) else 365
        thursday_yearday += prev_days_in_year
    elif thursday_yearday > days_in_year:
        # Thursday is in next year
        thursday_yearday -= days_in_year
    
    # Calculate week number
    week_number = (thursday_yearday - 1) // 7 + 1
    
    return week_number

