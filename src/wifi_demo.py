import time
import network
from machine import Pin

# --- Configuration ---
# IMPORTANT: Create a file named 'WIFI_CONFIG.py' in the same directory as this script
# and add the following lines to it, replacing with your actual credentials:
# SSID = "YOUR_WIFI_SSID"
# PSK = "YOUR_WIFI_PASSWORD"
try:
    import WIFI_CONFIG
    WIFI_SSID = WIFI_CONFIG.SSID
    WIFI_PASSWORD = WIFI_CONFIG.PSK
except ImportError:
    print("Error: WIFI_CONFIG.py not found or invalid.")
    print("Please create 'WIFI_CONFIG.py' with your SSID and PSK.")
    print("Example:")
    print("SSID = \"Your_Network_Name\"")
    print("PSK = \"Your_Network_Password\"")
    # Exit the script if config is missing
    raise SystemExit("Wi-Fi configuration missing. Cannot proceed.")


# Onboard LED for visual status during connection attempt
led = Pin("LED", Pin.OUT, value=0)

# --- Wi-Fi Connection Function ---

def connect_to_wifi():
    """Attempts to connect to the configured Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True) # Activate Wi-Fi interface

    # Check if already connected from a previous run
    if wlan.isconnected():
        print("Already connected to Wi-Fi.")
        status = wlan.ifconfig()
        print(f"IP address: {status[0]}")
        return True

    print(f"Attempting to connect to Wi-Fi network: '{WIFI_SSID}'...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout_seconds = 20 # Maximum time to wait for connection
    start_time = time.time()

    while not wlan.isconnected() and (time.time() - start_time < timeout_seconds):
        led.toggle() # Blink LED during connection attempt
        print(f"Waiting for connection... {int(timeout_seconds - (time.time() - start_time))}s left")
        time.sleep(1)

    led.value(0) # Turn off LED after connection attempt

    if wlan.isconnected():
        status = wlan.ifconfig()
        print("\n--- Wi-Fi Connected Successfully! ---")
        print(f"Network Status: {wlan.status()}")
        print(f"IP Address:     {status[0]}")
        print(f"Subnet Mask:    {status[1]}")
        print(f"Gateway:        {status[2]}")
        print(f"DNS Server:     {status[3]}")
        return True
    else:
        print("\n--- Wi-Fi Connection Failed! ---")
        print(f"Final WLAN Status: {wlan.status()}")
        if wlan.status() == network.STAT_NO_AP_FOUND:
            print("Reason: No access point found (SSID might be wrong or out of range).")
        elif wlan.status() == network.STAT_WRONG_PASSWORD:
            print("Reason: Incorrect Wi-Fi password (PSK).")
        elif wlan.status() == network.STAT_CONNECT_FAIL:
            print("Reason: General connection failure.")
        else:
            print("Reason: Unknown connection error.")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Wi-Fi connection test...")
    if connect_to_wifi():
        print("Wi-Fi test complete: SUCCESS.")
    else:
        print("Wi-Fi test complete: FAILURE.")
    print("Script finished.")
    # Keep the script running briefly so you can read the output in Thonny
    time.sleep(5)
