# time_manager.py (Version 0.1.0 - Combined and comprehensive)

import utime # Use utime for consistency with localtime, mktime, etc.
import ntptime # For NTP synchronization
import machine # For machine.reset() if needed, or other machine-specific ops
import gc      # For garbage collection

class TimeManager:
    """
    Manages time-related operations, including NTP synchronization,
    automatic British Summer Time (BST) calculation,
    date formatting, and custom time formats like 'rickdate'.
    Assumes the system's RTC is set to UTC by NTP.
    """
    def __init__(self, ntp_server, display_manager_instance=None):
        self.ntp_server = ntp_server
        self.last_sync_time = 0
        self.NTP_RESYNC_INTERVAL_SECONDS = 3600 * 24 # Resync every 24 hours (can be adjusted)
        self.display_manager = display_manager_instance # For logging messages to display

    def _log(self, message):
        """Internal helper to log messages to display (if available) and console."""
        if self.display_manager:
            self.display_manager.add_log_message(message)

    def sync_ntp_time(self):
        """Synchronizes the Pico W's RTC with NTP (UTC time)."""
        try:
            self._log(f"Setting NTP server to {self.ntp_server}")
            ntptime.host = self.ntp_server
            ntptime.settime() # This sets the RTC to UTC time from NTP
            self.last_sync_time = utime.time() # Store UTC timestamp of last sync
            self._log("RTC synchronized with NTP (UTC).")
            return True
        except Exception as e:
            self._log(f"Failed to sync RTC with NTP: {e}")
            return False

    def check_and_sync_ntp(self):
        """Checks if NTP resync is needed and performs it."""
        if utime.time() - self.last_sync_time >= self.NTP_RESYNC_INTERVAL_SECONDS:
            self._log("NTP resync interval reached. Resyncing...")
            self.sync_ntp_time()
            gc.collect() # Clean up memory after sync

    def to_base36(self, num):
        """Converts an integer to a base-36 string."""
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if num == 0:
            return "0"
        base36 = []
        while num:
            num, i = divmod(num, 36)
            base36.append(alphabet[i])
        return "".join(reversed(base36))

    def is_bst(self, year, month, day, weekday):
        """
        Determines if a given UTC date falls within British Summer Time (BST).
        BST starts last Sunday in March, ends last Sunday in October.
        weekday: 0=Monday, ..., 6=Sunday (MicroPython convention)
        """
        # Calculate last Sunday in March (UTC for transitions)
        # Find the weekday of March 31st (utime.localtime's weekday is 0=Monday, 6=Sunday)
        march_31_weekday = utime.localtime(utime.mktime((year, 3, 31, 0, 0, 0, 0, 0)))[6]
        # Calculate day of last Sunday in March
        # (31 - ((day_of_week_31st - target_day_of_week) % 7))
        # Target day of week for Sunday is 6
        last_sunday_march_day = 31 - ((march_31_weekday - 6) % 7)
        
        # Calculate last Sunday in October (UTC for transitions)
        # Find the weekday of October 31st
        oct_31_weekday = utime.localtime(utime.mktime((year, 10, 31, 0, 0, 0, 0, 0)))[6]
        # Calculate day of last Sunday in October
        last_sunday_oct_day = 31 - ((oct_31_weekday - 6) % 7)
        
        # Check if within BST period
        # Between April (month 4) and September (month 9) inclusive is always BST
        if month > 3 and month < 10:
            return True
        # March: On or after last Sunday in March
        elif month == 3 and day >= last_sunday_march_day:
            return True
        # October: Before last Sunday in October
        elif month == 10 and day < last_sunday_oct_day:
            return True
        
        return False

    def get_london_localtime(self):
        """
        Returns the current local time for London (UTC+0 for GMT or UTC+1 for BST).
        Assumes RTC is set to UTC by sync_ntp_time.
        Returns a tuple: (local_time_struct_tuple, offset_seconds).
        """
        utc_time_tuple = utime.localtime(utime.time()) # Get current UTC time from RTC
        year, month, day, hour, minute, second, weekday, yearday = utc_time_tuple

        is_bst_active = self.is_bst(year, month, day, weekday)
        offset_seconds = 3600 if is_bst_active else 0

        # Apply the offset to the UTC timestamp
        utc_seconds = utime.mktime(utc_time_tuple)
        local_seconds = utc_seconds + offset_seconds
        
        # Convert adjusted timestamp back to struct_time tuple
        local_time_tuple = utime.localtime(local_seconds)
        
        return local_time_tuple, offset_seconds

    def get_formatted_datetime(self, time_tuple: tuple) -> tuple:
        """
        Formats a utime.struct_time tuple into a specific set of strings.
        Returns: (formatted_date_str, formatted_time_str, full_str)
        Example: ("July 10, 2024", "15:30", "2024-07-10 15:30:45")
        """
        year, month, day, hour, minute, second, weekday, yearday = time_tuple

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_name = day_names[weekday] # This is available but not returned by name here

        month_names = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        month_name = month_names[month - 1]

        formatted_date = f"{month_name} {day}, {year}"
        formatted_time = f"{hour:02d}:{minute:02d}"

        full_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            year, month, day, hour, minute, second
        )
        return formatted_date, formatted_time, full_str


    def get_rickdate_format(self, time_tuple: tuple) -> str:
        """
        Generates a 'rickdate' formatted string (YYYYMMDD as base36, last 3 chars).
        """
        year, month, day, _, _, _, _, _ = time_tuple

        year_b36 = self.to_base36(year).upper()
        month_b36 = self.to_base36(month).upper()
        day_b36 = self.to_base36(day).upper()
        
        full_rickdate = f"{year_b36}{month_b36}{day_b36}"
        return full_rickdate[-3:]

    def get_week_number(self, time_tuple: tuple) -> int:
        """
        Calculates the ISO 8601 week number (Monday as first day of week).
        Week 1 is the first week containing January 4th.
        """
        year = time_tuple[0]
        weekday_mp = time_tuple[6] # 0=Mon, ..., 6=Sun
        yearday = time_tuple[7]    # 1-366

        iso_weekday = weekday_mp + 1 # 1=Mon, ..., 7=Sun
        
        # Calculate the day of the year for the Thursday of the current week.
        doy_thursday = yearday - iso_weekday + 4

        if doy_thursday < 1:
            # Date is in the last week of the previous ISO year.
            prev_year = year - 1
            prev_year_dec28_tuple = (prev_year, 12, 28, 0, 0, 0, 0, 0)
            prev_year_dec28_yearday = utime.localtime(utime.mktime(prev_year_dec28_tuple))[7]
            prev_year_dec28_weekday_mp = utime.localtime(utime.mktime(prev_year_dec28_tuple))[6]
            prev_year_dec28_iso_weekday = prev_year_dec28_weekday_mp + 1
            
            prev_year_doy_thursday = prev_year_dec28_yearday - prev_year_dec28_iso_weekday + 4
            return (prev_year_doy_thursday - 1) // 7 + 1

        is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
        days_in_current_year = 366 if is_leap else 365

        if doy_thursday > days_in_current_year:
            # Date is in the first week of the next ISO year.
            return 1
        
        return (doy_thursday - 1) // 7 + 1