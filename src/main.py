# main.py (Version 0.0.4 - Developer Friendly)
import time
import network
from machine import Pin
from pimoroni import Button

# Import our custom modules
import wifi_manager
import display_utils
import time_manager

display_utils.add_log_message("main.py execution started at boot.")

# --- Configuration ---
# Button pins
BUTTON_A_PIN = 12
BUTTON_B_PIN = 13
BUTTON_C_PIN = 14

# --- Display Modes ---
DATE_TIME_MODE = 0
PICTURE_MODE = 1
LOG_MODE = 2

current_display_mode = DATE_TIME_MODE # Start in date/time mode

# --- Hardware Initialization ---
button_a = Button(BUTTON_A_PIN)
button_b = Button(BUTTON_B_PIN)
button_c = Button(BUTTON_C_PIN)

# --- Main Program ---
display_utils.add_log_message("main.py started.")

# --- Ensure Wi-Fi and NTP sync if running main.py directly ---
# This block makes main.py more self-contained for development
if not network.WLAN(network.STA_IF).isconnected():
    display_utils.add_log_message("main.py: Wi-Fi not connected. Attempting connection...")
    WIFI_SSID = None
    WIFI_PASSWORD = None
    try:
        import WIFI_CONFIG
        WIFI_SSID = WIFI_CONFIG.SSID
        WIFI_PASSWORD = WIFI_CONFIG.PSK
    except ImportError:
        display_utils.add_log_message("ERROR: WIFI_CONFIG.py not found in main.py. Cannot connect to Wi-Fi.")
        display_utils.show_connection_error() # Uses display_utils' internal init check
        # Proceed without Wi-Fi/NTP
    else:
        # Pass None for LED as it's not managed here in main.py's direct run context
        wifi_connected_in_main = wifi_manager.connect_to_wifi(WIFI_SSID, WIFI_PASSWORD, display=display_utils.display, black_pen=display_utils.BLACK)
        if wifi_connected_in_main:
            display_utils.add_log_message("main.py: Wi-Fi connected. Attempting NTP sync...")
            wifi_manager.sync_time_ntp(display=display_utils.display, black_pen=display_utils.BLACK)
        else:
            display_utils.add_log_message("main.py: Wi-Fi connection failed.")
            display_utils.show_connection_error()

# Check if time is synced. If not, show error on display (if display works)
try:
    time.localtime()
    is_time_synced = True
except OSError:
    is_time_synced = False
    display_utils.add_log_message("WARNING: RTC not set (NTP sync failed?).")
    display_utils.show_ntp_error() # This will ensure display init before showing error

# Initial display update (this will now trigger display initialization if needed)
if is_time_synced:
    display_utils.update_display_with_datetime()
else:
    # If time not synced, the show_ntp_error above might have already shown something.
    # We can render the log screen to show more detail.
    display_utils.render_log_screen()
    display_utils.add_log_message("Initial display complete. Press Button A for Date/Time, Button C for Log.")


# Main loop: Wait for button press to update display or switch mode
while True:
    if button_a.read():
        display_utils.add_log_message("Button A pressed! Updating Date/Time display...")
        # Re-sync time if not already synced and Wi-Fi is connected
        if not is_time_synced and network.WLAN(network.STA_IF).isconnected():
            display_utils.add_log_message("Re-syncing time on Button A press...")
            if wifi_manager.sync_time_ntp(display=display_utils.display, black_pen=display_utils.BLACK):
                is_time_synced = True
            else:
                display_utils.add_log_message("Manual time re-sync failed.")
        
        if is_time_synced:
            display_utils.update_display_with_datetime()
        else:
            display_utils.show_ntp_error() # Show error if no time
        current_display_mode = DATE_TIME_MODE
        time.sleep(0.5) # Debounce

    if button_b.read():
        display_utils.add_log_message("Button B pressed! Switching to Picture Mode...")
        current_display_mode = PICTURE_MODE
        display_utils.update_display_with_picture()
        time.sleep(0.5) # Debounce

    if button_c.read():
        display_utils.add_log_message("Button C pressed! Switching to Log mode and updating display...")
        current_display_mode = LOG_MODE
        display_utils.render_log_screen()
        time.sleep(0.5) # Debounce

    time.sleep(0.01)