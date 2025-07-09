# main.py (Version 0.0.3)
import time
import network
import ntptime
import machine
import utime
import gc
import json # For config file (if used, previously)

# Import Pimoroni display specific libraries
import picographics
import inky_pack # Assuming you have this specific driver for Inky Pack 2.13" or similar

# Display dimensions (usually fixed for Inky Pack)
WIDTH = 212
HEIGHT = 104

# Setup display
# You might need to adjust this based on your specific Inky Pack model and driver
display = picographics.PicoGraphics(inky_pack.DISPLAY_INKY_PACK) # Or similar constant
display.set_font("bitmap8") # Default font

# Define pens (colors)
# These might be constants depending on your picographics version
# For 1-bit displays, 0 and 1 are common pen IDs
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)

# --- Configuration (Moved to config.toml) ---
# WiFi credentials (old way, now from config.toml)
# WIFI_SSID = "your_ssid"
# WIFI_PASSWORD = "your_password"
# NTP_SERVER = "pool.ntp.org"
# TZ_OFFSET_SECONDS = 3600 # London is UTC+1 (BST)

# --- Global Variables for WiFi and Time ---
wlan = None
is_connected = False
last_sync_time = 0
NTP_RESYNC_INTERVAL_SECONDS = 3600 # Resync every hour (3600 seconds)

# --- Helper Functions ---

def load_config():
    # This will be replaced by toml parsing
    return {
        "wifi": {
            "ssid": "YOUR_WIFI_SSID",
            "password": "YOUR_WIFI_PASSWORD",
            "country": "GB"
        },
        "ntp": {
            "server": "pool.ntp.org",
            "timezone_offset_seconds": 3600 # London is UTC+1 (BST)
        }
    }

def connect_to_wifi(ssid, password, country):
    global wlan, is_connected
    
    display.set_pen(WHITE)
    display.clear()
    display.set_pen(BLACK)
    display.text("Connecting WiFi...", 5, 5, scale=1)
    display.update()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Set country for better regulatory compliance and faster scans
    wlan.config(country=country) 
    
    # Check if already connected
    if wlan.isconnected():
        display.text("Already connected.", 5, 20, scale=1)
        display.update()
        time.sleep(1)
        is_connected = True
        return True

    print(f"Connecting to WiFi: {ssid}...")
    display.text(f"To: {ssid}", 5, 20, scale=1)
    display.update()

    wlan.connect(ssid, password)
    
    max_wait = 20
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Waiting for connection...")
        display.text(".", WIDTH - 10 * max_wait, 20, scale=1) # Simple progress dot
        display.update()
        time.sleep(1)

    if wlan.isconnected():
        status = wlan.ifconfig()
        print(f"Connected. IP: {status[0]}")
        display.set_pen(WHITE)
        display.clear()
        display.set_pen(BLACK)
        display.text("WiFi Connected!", 5, 5, scale=1)
        display.text(f"IP: {status[0]}", 5, 20, scale=1)
        display.update()
        time.sleep(2)
        is_connected = True
        return True
    else:
        print("WiFi connection failed!")
        display.set_pen(WHITE)
        display.clear()
        display.set_pen(BLACK)
        display.text("WiFi Failed!", 5, 5, scale=1)
        display.text("Check config/signal", 5, 20, scale=1)
        display.update()
        time.sleep(3)
        is_connected = False
        return False

def sync_time_ntp(ntp_server, tz_offset_seconds):
    global last_sync_time
    if not is_connected:
        print("Not connected to WiFi, cannot sync time.")
        display.set_pen(WHITE)
        display.clear()
        display.set_pen(BLACK)
        display.text("NTP Sync Failed!", 5, 5, scale=1)
        display.text("No WiFi connection", 5, 20, scale=1)
        display.update()
        time.sleep(2)
        return False

    display.set_pen(WHITE)
    display.clear()
    display.set_pen(BLACK)
    display.text("Syncing NTP...", 5, 5, scale=1)
    display.update()
    
    try:
        ntptime.host = ntp_server
        ntptime.settime()
        # Apply timezone offset
        current_time = utime.time()
        utime.set_time(current_time + tz_offset_seconds)
        last_sync_time = utime.time()
        print("NTP time synced successfully.")
        display.text("NTP Synced!", 5, 20, scale=1)
        display.update()
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error syncing NTP: {e}")
        display.set_pen(WHITE)
        display.clear()
        display.set_pen(BLACK)
        display.text("NTP Sync Failed!", 5, 5, scale=1)
        display.text(str(e), 5, 20, scale=1)
        display.update()
        time.sleep(3)
        return False

def get_london_localtime():
    # Helper to get the current local time in London
    # Assuming utime.time() is already adjusted for timezone by sync_time_ntp
    return utime.localtime()

def get_formatted_datetime(dt_tuple):
    # dt_tuple is (year, month, mday, hour, minute, second, weekday, yearday)
    year, month, mday, hour, minute, second, _, _, _ = dt_tuple
    date_str = f"{mday:02d}/{month:02d}/{year}"
    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
    full_str = f"{date_str} {time_str}"
    return date_str, time_str, full_str

# --- Main Application Loop ---
def main_loop():
    global last_sync_time

    # Load config (replace with actual toml parsing later)
    config = load_config()
    wifi_config = config["wifi"]
    ntp_config = config["ntp"]

    # Initial setup
    if not connect_to_wifi(wifi_config["ssid"], wifi_config["password"], wifi_config["country"]):
        # If WiFi fails, display error and perhaps retry or halt
        print("Exiting due to WiFi connection failure.")
        # Loop forever showing error
        while True:
            display.set_pen(WHITE)
            display.clear()
            display.set_pen(BLACK)
            display.text("WiFi Failed!", 5, 5, scale=2)
            display.text("Reboot to retry", 5, 30, scale=1)
            display.update()
            time.sleep(10) # Display error for a while then refresh
    
    if not sync_time_ntp(ntp_config["server"], ntp_config["timezone_offset_seconds"]):
        print("Exiting due to NTP sync failure.")
        while True:
            display.set_pen(WHITE)
            display.clear()
            display.set_pen(BLACK)
            display.text("NTP Sync Failed!", 5, 5, scale=2)
            display.text("Reboot to retry", 5, 30, scale=1)
            display.update()
            time.sleep(10) # Display error for a while then refresh

    # Main loop logic
    while True:
        current_time_epoch = utime.time()
        # Resync NTP if interval passed
        if current_time_epoch - last_sync_time >= NTP_RESYNC_INTERVAL_SECONDS:
            print("Resyncing NTP...")
            sync_time_ntp(ntp_config["server"], ntp_config["timezone_offset_seconds"])
        
        # Get and display current time
        dt = get_london_localtime()
        date_str, time_str, full_str = get_formatted_datetime(dt)

        display.set_pen(WHITE) # Clear background
        display.clear()
        display.set_pen(BLACK) # Set text color

        display.text(date_str, 5, 5, scale=2)
        display.text(time_str, 5, 30, scale=3)
        
        display.update() # Update the e-paper display
        
        gc.collect() # Clean up memory

        time.sleep(1) # Update display every second


# --- Entry Point ---
if __name__ == "__main__":
    main_loop()