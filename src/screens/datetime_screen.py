# screens/datetime_screen.py (Version 0.1.2 - Rick Date Integrated)

import utime

# No longer need _calculate_days_since_epoch as it's handled by TimeManager

def render(display_manager, time_manager):
    """
    Renders the main date/time/week/rickdate screen content.

    Args:
        display_manager: An instance of DisplayManager for drawing operations.
        time_manager: An instance of TimeManager for getting time data.
    """
    display = display_manager.display # Get the PicoGraphics display object for easier access

    if not display: # Check if display object itself is None after init
        display_manager.add_log_message("Error: Display not initialized for datetime screen rendering.")
        return

    display_manager.clear_display_buffer() # Clear the entire display buffer to white
    display.set_pen(display_manager.BLACK) # Set pen to black for text drawing
    
    local_time_tuple, offset_seconds = time_manager.get_london_localtime()
    
    if local_time_tuple:
        year, month, mday, hour, minute, second, weekday, yearday = local_time_tuple

        # Font scale 1 is usually 8 pixels high. So scale N text is N*8 pixels high.
        # Spacing of 5 pixels between elements.

        # --- Left Column Elements ---

        # 1. Day name (top left) - Adjusted scale to 4 for balance with Rickdate
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        display.text(day_names[weekday], 5, 5, scale=4)
        
        # y_pos calculation: previous_y + (previous_scale * 8) + gap
        y_pos_date = 5 + (4 * 8) + 5 # Based on Day name (scale 4)
        
        # 2. Date (Month Day, Year)
        month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        date_str = f"{month_names[month]} {mday}, {year}"
        display.text(date_str, 5, y_pos_date, scale=3)

        # 3. Time (HH:MM)
        y_pos_time = y_pos_date + (3 * 8) + 5 # Based on Date (scale 3)
        time_str = f"{hour:02d}:{minute:02d}"
        display.text(time_str, 5, y_pos_time, scale=2)

        # 4. Week number 
        y_pos_week = y_pos_time + (2 * 8) + 5 # Based on Time (scale 2)
        week_num = (yearday - 1) // 7 + 1 # Simple approximation (ISO week number is more complex if needed)
        display.text(f"WK{week_num:02d}", 5, y_pos_week, scale=4) # Using scale 4 for prominence

        # --- Right Column Elements ---
        
        # 5. Get and display the Rick Date value using the TimeManager function
        rick_date_val = time_manager.get_rickdate_format(local_time_tuple)
        
        # Calculate X for RIGHT alignment for "Rick date" value (scale 4)
        rick_date_val_width = display.measure_text(rick_date_val, scale=4)
        x_pos_rick_val = display_manager.WIDTH - rick_date_val_width - 5 # 5 pixels padding from right edge
        display.text(rick_date_val, x_pos_rick_val, 5, scale=4) # Top right, same Y as day name

        # 6. "rickdate" label (scale 1, below rick date value, RIGHT-aligned)
        rick_date_label = "rickdate"
        rick_date_label_width = display.measure_text(rick_date_label, scale=2)
        x_pos_rick_label = display_manager.WIDTH - rick_date_label_width - 5 # 5 pixels padding from right edge
        y_pos_rick_label = 5 + (4 * 8) + 5 # Below rick date value (scale 4 height)
        display.text(rick_date_label, x_pos_rick_label, y_pos_rick_label, scale=2)
        
    else:
        # Message for when time is not synced
        display.text("Time Not Synced", 5, 5, scale=2)
        display.text("Connect WiFi & NTP", 5, 30, scale=1)
        display.text("Press A to retry", 5, 45, scale=1) # Added tip for retry
        
    display_manager.display.update() # Always update the physical display