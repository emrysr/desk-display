# display_utils.py (Version 0.1.1 - Final set_border Fix)
import time
from picographics import PicoGraphics, DISPLAY_INKY_PACK
from collections import deque
import time_manager
import sys # For sys.print_exception

# Display settings
BLACK = 0
WHITE = 15
FONT = "bitmap8" # Ensure bitmap8.bin is on your Pico!
LINE_HEIGHT = 8

# Known dimensions for the 2.9" Pico Inky Pack
INKY_DISPLAY_WIDTH = 296
INKY_DISPLAY_HEIGHT = 128

# Initialize display object as None initially
display = None

# Global log buffer for capturing messages
MAX_LOG_LINES = 15
log_buffer = deque([], MAX_LOG_LINES)

def add_log_message(message):
    """Adds a message to the internal log buffer and prints to console."""
    log_buffer.append(message)
    print(f"[LOG]: {message}") # Always print to Thonny shell for debugging

def _ensure_display_initialized():
    """
    Ensures the display object is initialized.
    If 'display' is None, it calls init_display_for_boot().
    Returns True if display is successfully initialized or already initialized, False otherwise.
    """
    global display

    if display is None:
        add_log_message("Display not initialized. Attempting initialization...")
        init_display_for_boot() # Call the main init function

    return display is not None # Return whether display is now valid

def init_display_for_boot():
    """
    Initializes the PicoGraphics display object.
    This function can be called multiple times but only initializes if 'display' is None.
    """
    global display

    if display is not None:
        return # Already initialized

    add_log_message("Running Inky display initialization routine...")
    try:
        print("DEBUG: Calling PicoGraphics(DISPLAY_INKY_PACK)...")
        display = PicoGraphics(DISPLAY_INKY_PACK)
        print("DEBUG: PicoGraphics instantiated.")

        # Set update speed for e-paper (0-3, 2 or 3 is fast for clearing)
        print("DEBUG: Setting display update speed to 2...")
        display.set_update_speed(2) # Retaining this as per your working example
        print("DEBUG: Update speed set.")

        # Step 2: Set font
        print(f"DEBUG: Setting font to '{FONT}'...")
        display.set_font(FONT)
        print("DEBUG: Font set.")

        # Step 3: Clear display (Crucially, set_border is REMOVED)
        print("DEBUG: Clearing display...")
        # display.set_border(BLACK) # THIS LINE IS NOW PERMANENTLY REMOVED
        clear_display_full_refresh(display) # Clear the screen once initialized
        print("DEBUG: Display cleared.")

        add_log_message("Inky display initialized successfully.")

    except Exception as e:
        print(f"ERROR: Failed to initialize Inky display: {e}")
        sys.print_exception(e) # Print full traceback for detailed error
        add_log_message(f"Display init ERROR: {e}")
        display = None # Ensure it's None if init fails


def clear_display_full_refresh(display_obj=None):
    """
    Clears the entire display to white with a full refresh.
    Ensures display is initialized before attempting to clear.
    """
    d = display_obj if display_obj else display
    if d is None:
        # If no display_obj is passed, try to ensure global display is initialized
        if not _ensure_display_initialized():
            print("Warning: Display object not initialized. Cannot clear.")
            return
        d = display # Update d with the potentially newly initialized global display

    if d is None: # Double check after attempt to initialize
        print("Warning: Display object still not initialized. Cannot clear.")
        return

    d.set_pen(WHITE)
    d.clear()
    d.update()

def update_display_with_datetime(display_obj=None):
    """Updates the Inky Pack display with current day and date.
    Ensures display is initialized before attempting to update.
    """
    d = display_obj if display_obj else display
    if d is None:
        if not _ensure_display_initialized():
            add_log_message("Error: Display not initialized. Cannot update datetime.")
            return
        d = display

    if d is None: # Double check
        add_log_message("Error: Display still not initialized. Cannot update datetime.")
        return

    add_log_message("Updating display with current date and time...")
    clear_display_full_refresh(d) # This will also ensure display init

    try:
        local_time, is_bst_active = time_manager.get_london_localtime()
        dst = 'BST' if is_bst_active else 'GMT'
        add_log_message(f"{dst} active (UTC+{1 if is_bst_active else 0})")

        day_name, formatted_date, formatted_time = time_manager.get_formatted_datetime(local_time) 
        rickdate_str = time_manager.get_rickdate_format(local_time)
        week_number = time_manager.get_week_number(local_time)

        add_log_message(f"Displaying: {day_name}, {formatted_date} - {formatted_time}")
        add_log_message(f"Rickdate: {rickdate_str}")
        add_log_message(f"Week Number: {week_number}")

        d.set_pen(BLACK)

        d.text(day_name, 5, 5, scale=3)
        d.text(formatted_date, 5, 35, scale=2)
        d.text(f'WK{week_number}', 200, 5, scale=4)
        d.text(f'{formatted_time} {dst}', 5, 60, scale=3)
        d.text(f'{rickdate_str}', 5, 90, scale=4)
        d.text('rickdate', 70, 110, scale=1)

        d.update()
        add_log_message("Display update complete.")
    except Exception as e:
        add_log_message(f"Error during datetime display update: {e}")
        sys.print_exception(e)
        # Optionally show a generic error on screen if time calc fails
        clear_display_full_refresh(d)
        d.set_pen(BLACK)
        d.text("Time Error!", 5, 5, scale=2)
        d.text(str(e), 5, 30, scale=1)
        d.update()


def update_display_with_picture(display_obj=None):
    """Updates the Inky Pack display with a random photo.
    Ensures display is initialized before attempting to update.
    """
    d = display_obj if display_obj else display
    if d is None:
        if not _ensure_display_initialized():
            add_log_message("Error: Display not initialized. Cannot update picture.")
            return
        d = display

    if d is None: # Double check
        add_log_message("Error: Display still not initialized. Cannot update picture.")
        return

    add_log_message("TODO: update_display_with_picture()")
    clear_display_full_refresh(d)
    d.set_pen(BLACK)
    d.text("Picture Mode", 5, 5, scale=2)
    d.text("Not Implemented Yet", 5, 30, scale=1)
    d.update()


def render_log_screen(display_obj=None):
    """Renders the captured log messages onto the display.
    Ensures display is initialized before attempting to render.
    """
    d = display_obj if display_obj else display
    if d is None:
        if not _ensure_display_initialized():
            print("Warning: Display object not initialized. Cannot render log screen.")
            return
        d = display

    if d is None: # Double check
        print("Warning: Display object still not initialized. Cannot render log screen.")
        return

    add_log_message("Displaying log screen...")
    clear_display_full_refresh(d) # This will also ensure display init

    d.set_pen(BLACK)
    d.set_font(FONT)

    y_pos = 5
    for line in log_buffer:
        d.text(line.strip(), 5, y_pos, scale=1)
        y_pos += LINE_HEIGHT

    d.update()
    add_log_message("Log screen display complete.")


def show_ntp_error(display_obj=None):
    d = display_obj if display_obj else display
    if d is None:
        if not _ensure_display_initialized():
            print("Warning: Display object not initialized. Cannot show NTP error.")
            return
        d = display

    if d is None: # Double check
        print("Warning: Display object still not initialized. Cannot show NTP error.")
        return

    add_log_message("--- WARNING: Time not synced! ---")
    clear_display_full_refresh(d) # This will also ensure display init
    d.set_pen(BLACK)
    d.set_font(FONT)
    d.text("Time Sync Failed!", 5, 5, scale=1)
    d.text("Check WiFi or NTP", 5, 20, scale=1)
    d.update()
    time.sleep(2)


def show_connection_error(display_obj=None):
    d = display_obj if display_obj else display
    if d is None:
        if not _ensure_display_initialized():
            print("Warning: Display object not initialized. Cannot show connection error.")
            return
        d = display

    if d is None: # Double check
        print("Warning: Display object still not initialized. Cannot show connection error.")
        return

    add_log_message("--- WARNING: Not on wifi! ---")
    clear_display_full_refresh(d) # This will also ensure display init
    d.set_pen(BLACK)
    d.set_font(FONT)
    d.text("No WiFi!", 5, 5, scale=1)
    d.text("Cannot connect to AP", 5, 20, scale=1)
    d.update()
    time.sleep(2)