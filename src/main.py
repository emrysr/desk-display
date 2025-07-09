# main.py (Final version with separate screen files and optimized boot)

import time
import network
import machine
import utime
import gc

from machine import Pin 
from pimoroni import Button 

# Import our custom manager classes
from display_manager import DisplayManager
from config_manager import ConfigManager 
from time_manager import TimeManager     
from wifi_manager import WifiManager 

# Import screen rendering modules
import screens.datetime_screen
import screens.log_screen
import screens.todo_picture_screen

# --- Global Instance for Managers ---
display_manager = None
config_manager = None
wifi_manager = None 
time_manager = None

# --- Button Setup for Pico Inky Pack ---
BUTTON_A_PIN = 12
BUTTON_B_PIN = 13
BUTTON_C_PIN = 14

button_a = Button(BUTTON_A_PIN)
button_b = Button(BUTTON_B_PIN)
button_c = Button(BUTTON_C_PIN)

# --- Display Modes (strings for clarity) ---
DATE_TIME_MODE = "main_info"
PICTURE_MODE = "todo_photo"
LOG_MODE = "log"

# --- Screen Management Variables ---
current_screen_mode = DATE_TIME_MODE 
last_drawn_screen_mode = None     
should_refresh_display = True     


# --- Main Application Loop ---
def main_loop():
    global display_manager, config_manager, wifi_manager, time_manager 
    global current_screen_mode, last_drawn_screen_mode, should_refresh_display

    # Step 1: Initialize Display Manager.
    # This will cause ONE initial flash due to display.clear() in its __init__ method.
    # This is typically unavoidable for e-ink display initialization.
    display_manager = DisplayManager()
    display_manager.add_log_message("System booting...") # Logs to console
    display_manager.add_log_message("Initializing managers...") # Logs to console
    
    config_manager = ConfigManager(display_manager) 
    
    config = config_manager.load_config()
    if not config:
        display_manager.add_log_message("Failed to load config.toml! Resetting...")
        # If config fails, we must show an error. Use the log screen for details, then reset.
        current_screen_mode = LOG_MODE # Set mode for eventual display
        screens.log_screen.render(display_manager) # Force render error on screen immediately
        time.sleep(5)
        machine.reset() 

    # Extract configs
    wifi_config = config.get("wifi", {})
    ntp_config = config.get("ntp", {})

    # Initialize WifiManager
    wifi_manager = WifiManager(
        ssid=wifi_config.get("ssid"), 
        password=wifi_config.get("password"), 
        display_manager=display_manager,
    )

    # Initialize TimeManager
    ntp_server = ntp_config.get("server", "pool.ntp.org") 
    time_manager = TimeManager(ntp_server, display_manager) 

    # --- Connection and Sync Steps ---
    # Attempt WiFi connection. Only show error if it fails.
    if not wifi_manager.connect_to_wifi():
        display_manager.add_log_message("Exiting due to WiFi connection failure.")
        current_screen_mode = LOG_MODE # Set screen mode to log/error
        display_manager.show_connection_error() # Directly show error on screen and update
        # Enter infinite loop displaying error, waiting for user interaction or reset
        while True: 
            # Allow cycling to log screen for more details if user presses C
            if button_c.read():
                current_screen_mode = LOG_MODE
                # If we switch to log, force a refresh for the logs
                screens.log_screen.render(display_manager)
                time.sleep(0.5) 
            elif button_a.read() or button_b.read(): 
                # If user presses A or B, attempt to go back to main screen but keep showing error
                current_screen_mode = DATE_TIME_MODE 
                display_manager.show_connection_error() # Re-show error message
                time.sleep(0.5)
            gc.collect()
            utime.sleep_ms(100) 

    # Attempt NTP Time Sync. Only show error if it fails.
    if not time_manager.sync_ntp_time(): 
        display_manager.add_log_message("Exiting due to NTP sync failure.")
        current_screen_mode = LOG_MODE # Set screen mode to log/error
        display_manager.show_ntp_error() # Directly show error on screen and update
        # Enter infinite loop displaying error, waiting for user interaction or reset
        while True: 
            # Allow cycling to log screen for more details if user presses C
            if button_c.read():
                current_screen_mode = LOG_MODE
                # If we switch to log, force a refresh for the logs
                screens.log_screen.render(display_manager)
                time.sleep(0.5)
            elif button_a.read() or button_b.read():
                # If user presses A or B, attempt to go back to main screen but keep showing error
                current_screen_mode = DATE_TIME_MODE
                display_manager.show_ntp_error() # Re-show error message
                time.sleep(0.5)
            gc.collect()
            utime.sleep_ms(100) 

    # If we reach here, WiFi and NTP sync were successful.
    display_manager.add_log_message("System ready.") # Logs to console
    
    # Set initial screen to DATE_TIME_MODE and flag for first render in main loop.
    # This will be the first time the date/time screen is drawn to the e-ink.
    current_screen_mode = DATE_TIME_MODE
    should_refresh_display = True # Forces the first render in the main loop

    # --- Main Application Loop ---
    while True:
        # --- Button Handling ---
        if button_a.read(): 
            display_manager.add_log_message("Button A pressed!")
            if current_screen_mode == DATE_TIME_MODE:
                # If already on date_time, force a refresh (e.g., to update seconds)
                should_refresh_display = True 
            else:
                current_screen_mode = DATE_TIME_MODE
                should_refresh_display = True 
            time.sleep(0.5) # Debounce

        if button_b.read():
            display_manager.add_log_message("Button B pressed! Switching to Picture Mode...")
            current_screen_mode = PICTURE_MODE
            should_refresh_display = True 
            time.sleep(0.5) # Debounce

        if button_c.read():
            display_manager.add_log_message("Button C pressed! Switching to Log mode...")
            current_screen_mode = LOG_MODE
            should_refresh_display = True 
            time.sleep(0.5) # Debounce

        # --- Screen Rendering ---
        # Only redraw the screen if the mode has changed or if a refresh is explicitly requested
        if current_screen_mode != last_drawn_screen_mode or should_refresh_display:
            if current_screen_mode == DATE_TIME_MODE:
                screens.datetime_screen.render(display_manager, time_manager)
            elif current_screen_mode == LOG_MODE:
                screens.log_screen.render(display_manager)
            elif current_screen_mode == PICTURE_MODE:
                screens.todo_picture_screen.render(display_manager)
            
            last_drawn_screen_mode = current_screen_mode
            should_refresh_display = False # Reset flag after drawing

        # --- Periodic Tasks ---
        time_manager.check_and_sync_ntp() 

        # Housekeeping
        gc.collect() 
        time.sleep(0.1) # Short delay to prevent busy-waiting

# --- Entry Point ---
if __name__ == "__main__":
    main_loop()