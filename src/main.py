import time
import network
import machine
import utime
import gc

# Import Pin for button handling
from machine import Pin

from display_manager import DisplayManager
from config_manager import ConfigManager 
from time_manager import TimeManager     
from wifi_manager import WifiManager 

# --- Global Instance for Managers ---
display_manager = None
config_manager = None
wifi_manager = None 
time_manager = None

# --- Button Setup for Pico Inky Pack ---
BUTTON_A_PIN = 12
BUTTON_B_PIN = 13
BUTTON_C_PIN = 14

button_a = Pin(BUTTON_A_PIN, Pin.IN, Pin.PULL_UP)
button_b = Pin(BUTTON_B_PIN, Pin.IN, Pin.PULL_UP)
button_c = Pin(BUTTON_C_PIN, Pin.IN, Pin.PULL_UP)

# Debounce states for buttons (True means released, False means pressed)
last_button_a_state = True
last_button_b_state = True
last_button_c_state = True
button_debounce_delay_ms = 50 # Milliseconds for debouncing

# --- Screen Management Variables ---
current_screen_mode = "main_info" # Initial screen mode
last_drawn_screen_mode = None     # Tracks which screen was last drawn
should_refresh_display = True     # Flag to force a display refresh

# --- Button Handling Function ---
def handle_buttons():
    global current_screen_mode, last_button_a_state, last_button_b_state, last_button_c_state, should_refresh_display

    # Read current button states (PULL_UP means value is False when pressed)
    button_a_val = button_a.value()
    button_b_val = button_b.value()
    button_c_val = button_c.value()

    # Button A logic
    if button_a_val != last_button_a_state:
        utime.sleep_ms(button_debounce_delay_ms) # Debounce delay
        if button_a_val != last_button_a_state and button_a_val == False: # Button A was pressed
            if current_screen_mode == "main_info":
                # If already on main info screen, refresh its content
                should_refresh_display = True
            else:
                # Switch to main info screen
                current_screen_mode = "main_info"
                should_refresh_display = True # Force refresh as screen mode changed
        last_button_a_state = button_a_val

    # Button B logic
    if button_b_val != last_button_b_state:
        utime.sleep_ms(button_debounce_delay_ms)
        if button_b_val != last_button_b_state and button_b_val == False: # Button B was pressed
            current_screen_mode = "todo_photo"
            should_refresh_display = True
        last_button_b_state = button_b_val

    # Button C logic
    if button_c_val != last_button_c_state:
        utime.sleep_ms(button_debounce_delay_ms)
        if button_c_val != last_button_c_state and button_c_val == False: # Button C was pressed
            current_screen_mode = "log"
            should_refresh_display = True
        last_button_c_state = button_c_val

# --- Screen Rendering Functions ---

def render_main_info_screen_content():
    display_manager.clear_display_full_refresh()
    display_manager.display.set_pen(display_manager.BLACK)
    
    local_time_tuple, offset_seconds = time_manager.get_london_localtime()
    
    if local_time_tuple:
        year, month, mday, hour, minute, second, weekday, yearday = local_time_tuple

        # Font scale 1 is usually 8 pixels high. So scale N text is N*8 pixels high.
        # Spacing of 5 pixels between elements.

        # 1. Day name (size 5 text top left)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        display_manager.display.text(day_names[weekday], 5, 5, scale=5)
        y_pos = 5 + (5 * 8) + 5 # Start position for next element: prev_y + prev_height + gap

        # 2. Date (July 3, 2025 format, size 3, below day)
        month_names = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        date_str = f"{month_names[month]} {mday}, {year}"
        display_manager.display.text(date_str, 5, y_pos, scale=3)
        y_pos += (3 * 8) + 5

        # 3. Time (size 4)
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        display_manager.display.text(time_str, 5, y_pos, scale=4)
        y_pos += (4 * 8) + 5

        # 4. Week number (WK## format, size 5)
        # Simplified week number (yearday / 7). Not ISO standard but functional.
        week_num = (yearday - 1) // 7 + 1
        display_manager.display.text(f"WK{week_num:02d}", 5, y_pos, scale=5)

        # 5. Top right print the rick date in size 5
        # 6. under that in size 2 print the word rickdate (as a unit)
        # Placeholder for Rick date - will fill this in once clarified
        rick_date_val = "????" # Placeholder
        
        # Calculate X for right alignment for "Rick date"
        # Approx width of text = num_chars * font_scale * 8 (assuming mono-spaced char width)
        rick_date_text_width_approx = len(rick_date_val) * 5 * 8 
        display_manager.display.text(rick_date_val, display_manager.WIDTH - rick_date_text_width_approx - 5, 5, scale=5)
        
        # Calculate X for right alignment for "rickdate" label
        rick_date_label_width_approx = len("rickdate") * 2 * 8
        display_manager.display.text("rickdate", display_manager.WIDTH - rick_date_label_width_approx - 5, 5 + (5 * 8) + 5, scale=2) 
        
    else:
        display_manager.display.text("Time Not Synced", 5, 5, scale=2)
        display_manager.display.text("Connect WiFi & NTP", 5, 30, scale=1)

def render_todo_screen_content():
    display_manager.clear_display_full_refresh()
    display_manager.display.set_pen(display_manager.BLACK)
    display_manager.display.text("TODO: Load Photo", 5, 5, scale=2)
    display_manager.display.text("Not implemented yet!", 5, 30, scale=1)
    
def render_log_screen_content():
    # This just calls the existing function in DisplayManager
    display_manager.render_log_screen()


# --- Main Application Loop ---
def main_loop():
    global display_manager, config_manager, wifi_manager, time_manager 
    global current_screen_mode, last_drawn_screen_mode, should_refresh_display

    display_manager = DisplayManager()
    display_manager.add_log_message("System booting...")
    display_manager.add_log_message("Initializing managers...")
    
    config_manager = ConfigManager(display_manager) 
    
    config = config_manager.load_config()
    if not config:
        display_manager.add_log_message("Failed to load config.toml!")
        # Force log screen to show error immediately during boot
        current_screen_mode = "log"
        last_drawn_screen_mode = None # Ensure it draws
        should_refresh_display = True
        # Render the log screen to show error before potentially stopping
        render_log_screen_content() # Directly call content render
        display_manager.display.update()
        time.sleep(5)
        machine.reset() 

    # Extract configs
    wifi_config = config.get("wifi", {})
    ntp_config = config.get("ntp", {})

    # Initialize WifiManager.
    wifi_manager = WifiManager(
        ssid=wifi_config.get("ssid"), 
        password=wifi_config.get("password"), 
        display_manager=display_manager,
    )

    # Initialize TimeManager
    ntp_server = ntp_config.get("server", "pool.ntp.org") # Default NTP server
    time_manager = TimeManager(ntp_server, display_manager) 

    # --- Initial Setup Steps ---
    # Display log screen during initial setup
    current_screen_mode = "log"
    last_drawn_screen_mode = None # Ensure it draws
    should_refresh_display = True
    render_log_screen_content()
    display_manager.display.update()
    utime.sleep(2) # Show log for a bit

    # Connect to WiFi
    if not wifi_manager.connect_to_wifi():
        display_manager.add_log_message("Exiting due to WiFi connection failure.")
        current_screen_mode = "log" # Ensure log shows failure
        should_refresh_display = True
        while True: # Loop indefinitely on error screen
            if should_refresh_display or current_screen_mode != last_drawn_screen_mode:
                display_manager.show_connection_error() # This function renders and updates
                last_drawn_screen_mode = current_screen_mode
                should_refresh_display = False
            handle_buttons() # Allow switching to log
            if current_screen_mode == "log" and last_drawn_screen_mode != "log": # If changed to log
                should_refresh_display = True # Force refresh for log
            utime.sleep_ms(100) # Short delay

    # Sync NTP Time
    if not time_manager.sync_ntp_time(): 
        display_manager.add_log_message("Exiting due to NTP sync failure.")
        current_screen_mode = "log" # Ensure log shows failure
        should_refresh_display = True
        while True: # Loop indefinitely on error screen
            if should_refresh_display or current_screen_mode != last_drawn_screen_mode:
                display_manager.show_ntp_error() # This function renders and updates
                last_drawn_screen_mode = current_screen_mode
                should_refresh_display = False
            handle_buttons() # Allow switching to log
            if current_screen_mode == "log" and last_drawn_screen_mode != "log": # If changed to log
                should_refresh_display = True # Force refresh for log
            utime.sleep_ms(100) # Short delay

    display_manager.add_log_message("System ready.")
    
    # After boot, default to main info screen and refresh it
    current_screen_mode = "main_info"
    should_refresh_display = True # Force initial draw of main screen


    # --- Main Application Loop ---
    while True:
        # Check for button presses and update screen mode or refresh flag
        handle_buttons() 

        # Only redraw if the screen mode has changed OR a refresh is explicitly requested (e.g., Button A press)
        if current_screen_mode != last_drawn_screen_mode or should_refresh_display:
            if current_screen_mode == "main_info":
                render_main_info_screen_content()
            elif current_screen_mode == "log":
                render_log_screen_content()
            elif current_screen_mode == "todo_photo":
                render_todo_screen_content()
            
            # The update() call is now conditional, only when content changes or forced
            display_manager.display.update() 
            last_drawn_screen_mode = current_screen_mode
            should_refresh_display = False # Reset refresh flag after updating

        # Periodically check WiFi connection and reconnect if lost (without constant redraw)
        if not wifi_manager.is_connected():
            display_manager.add_log_message("WiFi disconnected. Attempting to reconnect...")
            if not wifi_manager.connect_to_wifi():
                display_manager.add_log_message("Reconnection failed. Will retry.")
                # If reconnection fails, you might want to switch to an error screen
                # For now, just log and continue, it won't force a redraw until a button press
        
        # Periodically check and sync NTP (without constant redraw)
        time_manager.check_and_sync_ntp()
        
        gc.collect() 
        utime.sleep_ms(100) # Short sleep to prevent busy-waiting and allow other tasks


# --- Entry Point ---
if __name__ == "__main__":
    main_loop()